"""QAOA simulé pour la sélection d'actifs sous contrainte de cardinalité.

Formulation :
- Variables binaires x_i ∈ {0,1} : actif i inclus ou non
- Coût QUBO approximant un proxy mean-variance (pas le Sharpe exact)
- Pénalité pour imposer sum(x) ≈ K

Le QAOA est simulé de façon classique (pas de hardware quantique) :
- pour n ≤ 16 : état complet (statevector) sur 2^n amplitudes
- pour n > 16 : échantillonnage variationnel heuristique

Après sélection des actifs, on repondère avec Markowitz sur le sous-ensemble.

Voir docs/methode_qaoa.md pour les limites mesurées expérimentalement.

Avertissement : expérimental — PAS un conseil financier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.classical_baseline.markowitz import (
    OptimizationResult,
    maximize_sharpe,
    minimize_volatility,
)


@dataclass
class QAOAConfig:
    """Hyperparamètres QAOA simulé."""

    p: int = 2  # profondeur (couches)
    max_assets: int = 5
    penalty: float = 10.0  # force de la contrainte de cardinalité
    n_samples: int = 512  # pour le mode sampling (n > 16)
    seed: int | None = 42
    risk_aversion: float = 1.0  # λ dans ret - λ * var
    n_restarts: int = 5  # multi-start pour la calibration des angles


def _build_qubo(
    mu: np.ndarray,
    Sigma: np.ndarray,
    K: int,
    penalty: float,
    risk_aversion: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Construit Q (matrice n×n) et c (linéaire) pour min x^T Q x + c^T x.

    Objectif proxy : maximiser μ·x/K - λ x^T Σ x  (équipondéré implicite)
    → minimiser  λ x^T Σ x - μ·x/K
    Contrainte : (sum x_i - K)^2 * penalty

    Attention : ce n'est PAS le ratio de Sharpe avec poids Markowitz optimaux.
    """
    n = len(mu)
    Q = risk_aversion * Sigma.copy()
    Q = Q + penalty * (np.ones((n, n)) - np.eye(n))
    np.fill_diagonal(Q, np.diag(Q) + penalty)
    c = -mu / max(K, 1) - 2.0 * penalty * K + penalty
    return Q, c


def _bitstring_energy(x: np.ndarray, Q: np.ndarray, c: np.ndarray) -> float:
    return float(x @ Q @ x + c @ x)


def _qaoa_statevector(
    Q: np.ndarray,
    c: np.ndarray,
    p: int,
    rng: np.random.Generator,
    n_restarts: int = 5,
) -> np.ndarray:
    """QAOA exact (statevector) pour n ≤ 16. Retourne les probabilités P(z)."""
    n = len(c)
    dim = 1 << n

    costs = np.zeros(dim)
    for z in range(dim):
        bits = np.array([(z >> i) & 1 for i in range(n)], dtype=float)
        costs[z] = _bitstring_energy(bits, Q, c)

    def run_circuit(params: np.ndarray) -> np.ndarray:
        state = np.ones(dim, dtype=complex) / np.sqrt(dim)
        gammas, betas = params[:p], params[p:]

        def apply_cost(gamma: float) -> None:
            nonlocal state
            state = state * np.exp(-1j * gamma * costs)

        def apply_mixer(beta: float) -> None:
            nonlocal state
            for q in range(n):
                new = state.copy()
                bit = 1 << q
                cB, sB = np.cos(beta), -1j * np.sin(beta)
                for z in range(dim):
                    z2 = z ^ bit
                    if z < z2:
                        a, b = state[z], state[z2]
                        new[z] = cB * a + sB * b
                        new[z2] = sB * a + cB * b
                state = new

        for i in range(p):
            apply_cost(gammas[i])
            apply_mixer(betas[i])
        return state

    def expectation(params: np.ndarray) -> float:
        state = run_circuit(params)
        probs = np.abs(state) ** 2
        return float(np.dot(probs, costs))

    best_params = None
    best_exp = np.inf
    for _ in range(max(1, n_restarts)):
        x0 = rng.uniform(0, 2 * np.pi, size=2 * p)
        res = minimize(expectation, x0, method="COBYLA", options={"maxiter": 100})
        val = expectation(res.x)
        if val < best_exp:
            best_exp = val
            best_params = res.x

    state = run_circuit(best_params)
    return np.abs(state) ** 2


def _select_from_probs(
    probs: np.ndarray,
    Q: np.ndarray,
    c: np.ndarray,
    K: int,
    top_m: int = 32,
) -> np.ndarray:
    """Parmi les bitstrings de poids K, garde ceux à plus haute proba puis
    choisit la plus basse énergie QUBO (meilleur proxy).
    """
    n = len(c)
    dim = len(probs)
    candidates: list[tuple[float, float, int]] = []  # (-prob, energy, z)
    for z in range(dim):
        bits = [(z >> i) & 1 for i in range(n)]
        if sum(bits) != K:
            continue
        candidates.append((-probs[z], _bitstring_energy(np.array(bits, dtype=float), Q, c), z))

    if not candidates:
        # fallback énergie pure
        best_e, best_z = np.inf, 0
        for z in range(dim):
            bits = np.array([(z >> i) & 1 for i in range(n)], dtype=float)
            if bits.sum() != K:
                continue
            e = _bitstring_energy(bits, Q, c)
            if e < best_e:
                best_e, best_z = e, z
        return np.array([(best_z >> i) & 1 for i in range(n)], dtype=bool)

    candidates.sort()  # proba décroissante
    pool = candidates[: min(top_m, len(candidates))]
    best = min(pool, key=lambda t: t[1])  # plus basse énergie
    z = best[2]
    return np.array([(z >> i) & 1 for i in range(n)], dtype=bool)


def _qaoa_sampling(
    Q: np.ndarray,
    c: np.ndarray,
    p: int,
    n_samples: int,
    K: int,
    rng: np.random.Generator,
    n_restarts: int = 5,
) -> np.ndarray:
    """Mode sampling pour n > 16.

    Heuristique variationnelle inspirée QAOA (pas une simulation unitaire exacte).
    Multi-start + grand nombre d'échantillons améliorent la stabilité mais restent
    limités par le proxy QUBO.
    """
    n = len(c)

    def sample_batch(params: np.ndarray, m: int) -> tuple[np.ndarray, np.ndarray]:
        gammas = params[:p]
        betas = params[p:]
        score = -c + 0.05 * rng.normal(size=n)
        for g, b in zip(gammas, betas):
            score = score * (0.5 + 0.5 * np.cos(b)) - 0.1 * g * np.diag(Q)
        logits = score - score.max()
        probs = np.exp(logits)
        probs = probs / probs.sum()
        xs = np.zeros((m, n))
        for i in range(m):
            idx = rng.choice(n, size=min(K, n), replace=False, p=probs)
            xs[i, idx] = 1.0
        energies = np.array([_bitstring_energy(xs[i], Q, c) for i in range(m)])
        return xs, energies

    def expectation(params: np.ndarray) -> float:
        _, energies = sample_batch(params, min(96, n_samples))
        return float(energies.mean())

    best_params = None
    best_exp = np.inf
    for _ in range(max(1, n_restarts)):
        x0 = rng.uniform(0, np.pi, size=2 * p)
        res = minimize(expectation, x0, method="COBYLA", options={"maxiter": 60})
        val = expectation(res.x)
        if val < best_exp:
            best_exp = val
            best_params = res.x

    xs, energies = sample_batch(best_params, n_samples)
    return xs[int(np.argmin(energies))]


def qaoa_select_and_weight(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    max_assets: int = 5,
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    risk_free_rate: float = 0.0,
    periods: int = 252,
    config: QAOAConfig | None = None,
) -> OptimizationResult:
    """Sélection QAOA simulée puis pondération Markowitz sur le sous-ensemble."""
    cfg = config or QAOAConfig()
    rng = np.random.default_rng(cfg.seed)

    assets = mean_returns.index.tolist()
    n = len(assets)
    K = min(cfg.max_assets, max_assets, n)
    mu = mean_returns.values.astype(float)
    Sigma = cov_matrix.values.astype(float)

    Q, c = _build_qubo(mu, Sigma, K, cfg.penalty, cfg.risk_aversion)

    if n <= 16:
        probs = _qaoa_statevector(Q, c, cfg.p, rng, n_restarts=cfg.n_restarts)
        selection = _select_from_probs(probs, Q, c, K)
        mode = "statevector"
    else:
        best_bits = _qaoa_sampling(
            Q, c, cfg.p, cfg.n_samples, K, rng, n_restarts=cfg.n_restarts
        )
        selection = best_bits.astype(bool)
        if selection.sum() != K:
            scores = mu - cfg.risk_aversion * np.diag(Sigma)
            order = np.argsort(scores)[::-1]
            selection = np.zeros(n, dtype=bool)
            selection[order[:K]] = True
        mode = "sampling"

    selected = [assets[i] for i in range(n) if selection[i]]
    if len(selected) < 2:
        order = np.argsort(mu)[::-1][:K]
        selected = [assets[i] for i in order]

    sub_mu = mean_returns.loc[selected]
    sub_cov = cov_matrix.loc[selected, selected]
    if objective == "max_sharpe":
        sub_res = maximize_sharpe(sub_mu, sub_cov, risk_free_rate, periods)
    else:
        sub_res = minimize_volatility(sub_mu, sub_cov, None, periods)

    full_w = pd.Series(0.0, index=assets)
    full_w.loc[sub_res.weights.index] = sub_res.weights.values

    return OptimizationResult(
        weights=full_w,
        expected_return=sub_res.expected_return,
        volatility=sub_res.volatility,
        sharpe=sub_res.sharpe,
        success=True,
        message=(
            f"QAOA-{mode} p={cfg.p} restarts={cfg.n_restarts} "
            f"K={K} selected={selected}"
        ),
    )


def optimize_qaoa_from_returns(
    returns: pd.DataFrame,
    max_assets: int = 5,
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    risk_free_rate: float = 0.0,
    periods: int = 252,
    config: QAOAConfig | None = None,
) -> OptimizationResult:
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    return qaoa_select_and_weight(
        mean_returns,
        cov_matrix,
        max_assets=max_assets,
        objective=objective,
        risk_free_rate=risk_free_rate,
        periods=periods,
        config=config,
    )
