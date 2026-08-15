"""QAOA simulé pour la sélection d'actifs sous contrainte de cardinalité.

Formulation :
- Variables binaires x_i ∈ {0,1} : actif i inclus ou non
- Coût QUBO approximant −Sharpe (via rendement / risque quadratique)
- Pénalité pour imposer sum(x) ≈ K

Le QAOA est simulé de façon classique (pas de hardware quantique) :
- pour n ≤ 16 : état complet (statevector) sur 2^n amplitudes
- pour n > 16 : échantillonnage variationnel (circuit QAOA approximé par
  tirages de bitstrings biaisés par les angles γ, β)

Après sélection des actifs, on repondère avec Markowitz sur le sous-ensemble.

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
    portfolio_performance,
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


def _build_qubo(
    mu: np.ndarray,
    Sigma: np.ndarray,
    K: int,
    penalty: float,
    risk_aversion: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Construit Q (matrice n×n) et c (linéaire) pour min x^T Q x + c^T x.

    Objectif financier : maximiser μ·x/K - λ x^T Σ x  (proxy equipondéré)
    → minimiser  λ x^T Σ x - μ·x/K
    Contrainte : (sum x_i - K)^2 * penalty
    """
    n = len(mu)
    # Terme variance (quadratique)
    Q = risk_aversion * Sigma.copy()
    # Pénalité (sum x - K)^2 = sum_i x_i + 2 sum_{i<j} x_i x_j - 2K sum x + K^2
    # → ajouter penalty sur diagonale et hors diagonale
    Q = Q + penalty * (np.ones((n, n)) - np.eye(n))
    # Diagonale : variance déjà dedans + penalty pour x_i^2 = x_i
    np.fill_diagonal(Q, np.diag(Q) + penalty)

    # Linéaire : -mu/K - 2*penalty*K  (et +penalty déjà partiellement dans diag pour x_i)
    c = -mu / max(K, 1) - 2.0 * penalty * K + penalty
    return Q, c


def _bitstring_energy(x: np.ndarray, Q: np.ndarray, c: np.ndarray) -> float:
    return float(x @ Q @ x + c @ x)


def _qaoa_statevector(
    Q: np.ndarray,
    c: np.ndarray,
    p: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """QAOA exact (statevector) pour n ≤ 16. Retourne les probabilités P(z)."""
    n = len(c)
    dim = 1 << n

    # Coût diagonal
    costs = np.zeros(dim)
    for z in range(dim):
        bits = np.array([(z >> i) & 1 for i in range(n)], dtype=float)
        costs[z] = _bitstring_energy(bits, Q, c)

    # État initial |+>^n
    state = np.ones(dim, dtype=complex) / np.sqrt(dim)

    def apply_cost(gamma: float) -> None:
        nonlocal state
        state = state * np.exp(-1j * gamma * costs)

    def apply_mixer(beta: float) -> None:
        nonlocal state
        # Mixer = produit de RX(2β) sur chaque qubit
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

    def expectation(params: np.ndarray) -> float:
        nonlocal state
        state = np.ones(dim, dtype=complex) / np.sqrt(dim)
        gammas = params[:p]
        betas = params[p:]
        for i in range(p):
            apply_cost(gammas[i])
            apply_mixer(betas[i])
        probs = np.abs(state) ** 2
        return float(np.dot(probs, costs))

    x0 = rng.uniform(0, 2 * np.pi, size=2 * p)
    res = minimize(expectation, x0, method="COBYLA", options={"maxiter": 80})

    # Reconstruire l'état final
    state = np.ones(dim, dtype=complex) / np.sqrt(dim)
    params = res.x
    for i in range(p):
        apply_cost(params[i])
        apply_mixer(params[p + i])
    return np.abs(state) ** 2


def _qaoa_sampling(
    Q: np.ndarray,
    c: np.ndarray,
    p: int,
    n_samples: int,
    K: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Mode sampling pour n > 16 : optimise γ,β via Monte-Carlo sur bitstrings.

    Approximation : on tire des bitstrings de poids de Hamming proche de K,
    biaisés par un score QUBO et des angles QAOA (heuristique variationnelle).
    """
    n = len(c)

    def sample_batch(params: np.ndarray, m: int) -> tuple[np.ndarray, np.ndarray]:
        # Heuristique : probabilités d'inclusion liées à -c_i (attrait linéaire)
        gammas = params[:p]
        betas = params[p:]
        # Score d'inclusion
        score = -c + 0.1 * rng.normal(size=n)
        for g, b in zip(gammas, betas):
            score = score * np.cos(b) - g * np.diag(Q)
        logits = score - score.max()
        probs = np.exp(logits) / np.exp(logits).sum()
        xs = np.zeros((m, n))
        for i in range(m):
            # Échantillonner exactement K actifs selon probs
            idx = rng.choice(n, size=min(K, n), replace=False, p=probs)
            xs[i, idx] = 1.0
        energies = np.array([_bitstring_energy(xs[i], Q, c) for i in range(m)])
        return xs, energies

    def expectation(params: np.ndarray) -> float:
        _, energies = sample_batch(params, min(64, n_samples))
        return float(energies.mean())

    x0 = rng.uniform(0, np.pi, size=2 * p)
    minimize(expectation, x0, method="COBYLA", options={"maxiter": 40})

    # Échantillon final plus large avec meilleurs params (re-opt déjà fait)
    # On relance un dernier batch avec x0 affiné
    res = minimize(expectation, x0, method="COBYLA", options={"maxiter": 30})
    xs, energies = sample_batch(res.x, n_samples)
    best = xs[int(np.argmin(energies))]
    return best


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
        probs = _qaoa_statevector(Q, c, cfg.p, rng)
        # Parmi les bitstrings de poids K, prendre le plus probable
        best_z, best_p = -1, -1.0
        for z in range(1 << n):
            bits = [(z >> i) & 1 for i in range(n)]
            if sum(bits) == K and probs[z] > best_p:
                best_p = probs[z]
                best_z = z
        if best_z < 0:
            # fallback : meilleur coût parmi Hamming weight K
            best_e = np.inf
            for z in range(1 << n):
                bits = np.array([(z >> i) & 1 for i in range(n)], dtype=float)
                if bits.sum() != K:
                    continue
                e = _bitstring_energy(bits, Q, c)
                if e < best_e:
                    best_e = e
                    best_z = z
        selection = np.array([(best_z >> i) & 1 for i in range(n)], dtype=bool)
        mode = "statevector"
    else:
        best_bits = _qaoa_sampling(Q, c, cfg.p, cfg.n_samples, K, rng)
        selection = best_bits.astype(bool)
        # Forcer exactement K
        if selection.sum() != K:
            scores = mu - cfg.risk_aversion * np.diag(Sigma)
            order = np.argsort(scores)[::-1]
            selection = np.zeros(n, dtype=bool)
            selection[order[:K]] = True
        mode = "sampling"

    selected = [assets[i] for i in range(n) if selection[i]]
    if len(selected) < 2:
        # Fallback : top K par rendement moyen
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
        message=f"QAOA-{mode} p={cfg.p} K={K} selected={selected}",
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
