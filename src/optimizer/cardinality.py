"""Optimisation de portefeuille avec contrainte de cardinalité.

Problème : choisir au plus K actifs parmi N, puis les pondérer
(long-only, somme = 1). C'est un problème combinatoire (NP-difficile)
plus réaliste qu'une simple pondération de tous les actifs.

Avertissement : simulation expérimentale — PAS un conseil financier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from src.classical_baseline.markowitz import (
    OptimizationResult,
    maximize_sharpe,
    minimize_volatility,
    portfolio_performance,
)
from src.optimizer.simulated_annealing import SAConfig, _energy, _normalize


def _project_cardinality(w: np.ndarray, max_assets: int) -> np.ndarray:
    """Garde les max_assets plus grands poids, met le reste à 0, renormalise."""
    w = np.asarray(w, dtype=float).copy()
    if max_assets >= len(w):
        return _normalize(w)
    idx = np.argsort(w)[::-1][:max_assets]
    mask = np.zeros_like(w)
    mask[idx] = 1.0
    return _normalize(w * mask)


def markowitz_cardinality(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    max_assets: int = 5,
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    risk_free_rate: float = 0.0,
    periods: int = 252,
    n_random_subsets: int = 80,
    seed: int | None = 42,
) -> OptimizationResult:
    """Baseline classique avec cardinalité.

    Stratégie en deux temps :
    1. Markowitz continu → projection top-K (rapide).
    2. Échantillonnage aléatoire de sous-ensembles de taille K +
       Markowitz sur chaque sous-ensemble ; on garde le meilleur.

    Cela reste une heuristique classique (pas de solveur MIP).
    """
    assets = mean_returns.index.tolist()
    n = len(assets)
    K = min(max_assets, n)
    rng = np.random.default_rng(seed)

    def _eval_subset(idx: list[int]) -> OptimizationResult:
        sub_mu = mean_returns.iloc[idx]
        sub_cov = cov_matrix.iloc[idx, idx]
        if objective == "max_sharpe":
            res = maximize_sharpe(sub_mu, sub_cov, risk_free_rate, periods)
        else:
            res = minimize_volatility(sub_mu, sub_cov, None, periods)
        # Réintégrer dans le vecteur complet
        full = pd.Series(0.0, index=assets)
        full.loc[res.weights.index] = res.weights.values
        res.weights = full
        return res

    candidates: list[OptimizationResult] = []

    # 1) Projection top-K du Markowitz global
    if objective == "max_sharpe":
        full = maximize_sharpe(mean_returns, cov_matrix, risk_free_rate, periods)
    else:
        full = minimize_volatility(mean_returns, cov_matrix, None, periods)
    w_proj = _project_cardinality(full.weights.values, K)
    mu = mean_returns.values
    Sigma = cov_matrix.values
    ret, vol, sharpe = portfolio_performance(w_proj, mu, Sigma, periods)
    candidates.append(
        OptimizationResult(
            weights=pd.Series(w_proj, index=assets),
            expected_return=ret,
            volatility=vol,
            sharpe=sharpe,
            success=True,
            message="markowitz+topK",
        )
    )

    # 2) Sous-ensembles aléatoires
    for _ in range(n_random_subsets):
        idx = sorted(rng.choice(n, size=K, replace=False).tolist())
        try:
            candidates.append(_eval_subset(idx))
        except Exception:
            continue

    # Meilleur selon l'objectif
    if objective == "max_sharpe":
        best = max(candidates, key=lambda r: r.sharpe)
    else:
        best = min(candidates, key=lambda r: r.volatility)

    best.message = f"markowitz_cardinality K={K}, candidats={len(candidates)}"
    return best


def sa_cardinality(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    max_assets: int = 5,
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    risk_free_rate: float = 0.0,
    periods: int = 252,
    config: SAConfig | None = None,
) -> OptimizationResult:
    """Recuit simulé avec contrainte de cardinalité (au plus K actifs)."""
    cfg = config or SAConfig(n_steps=8000, step_size=0.08, seed=42)
    rng = np.random.default_rng(cfg.seed)

    assets = mean_returns.index.tolist()
    n = len(assets)
    K = min(max_assets, n)
    mu = mean_returns.values.astype(float)
    Sigma = cov_matrix.values.astype(float)
    daily_rf = risk_free_rate / periods

    # État = masque binaire + poids sur les actifs actifs
    active = np.zeros(n, dtype=bool)
    active[rng.choice(n, size=K, replace=False)] = True
    w = np.zeros(n)
    w[active] = 1.0 / K

    def energy(weights: np.ndarray) -> float:
        return _energy(weights, mu, Sigma, objective, daily_rf)

    e = energy(w)
    best_w, best_e = w.copy(), e
    t = cfg.t0
    accepted = 0

    for _ in range(cfg.n_steps):
        w_cand = w.copy()
        active_cand = active.copy()

        move = rng.random()
        if move < 0.4 and K < n:
            # Swap : désactive un actif, en active un autre
            on = np.where(active_cand)[0]
            off = np.where(~active_cand)[0]
            if len(on) and len(off):
                i = rng.choice(on)
                j = rng.choice(off)
                active_cand[i] = False
                active_cand[j] = True
                w_cand[i] = 0.0
                w_cand[j] = rng.uniform(0.05, 0.3)
                w_cand = _normalize(w_cand * active_cand)
        elif move < 0.7:
            # Repondération sur les actifs actifs
            on = np.where(active_cand)[0]
            if len(on) >= 2:
                i, j = rng.choice(on, size=2, replace=False)
                delta = rng.uniform(-cfg.step_size, cfg.step_size)
                w_cand[i] = max(0.0, w_cand[i] + delta)
                w_cand[j] = max(0.0, w_cand[j] - delta)
                w_cand = _normalize(w_cand * active_cand)
        else:
            # Bruit gaussien + projection cardinalité
            w_cand = w_cand + rng.normal(0, cfg.step_size, n)
            w_cand = _project_cardinality(w_cand, K)
            active_cand = w_cand > 1e-8

        e_cand = energy(w_cand)
        delta = e_cand - e
        if delta < 0 or rng.random() < np.exp(-delta / max(t, 1e-15)):
            w, e, active = w_cand, e_cand, active_cand
            accepted += 1
            if e < best_e:
                best_w, best_e = w.copy(), e

        t = max(t * cfg.cooling, cfg.t_min)

    best_w = _project_cardinality(best_w, K)
    ret, vol, sharpe = portfolio_performance(best_w, mu, Sigma, periods)
    return OptimizationResult(
        weights=pd.Series(best_w, index=assets),
        expected_return=ret,
        volatility=vol,
        sharpe=sharpe,
        success=True,
        message=f"SA cardinality K={K}, steps={cfg.n_steps}, accepted={accepted}",
    )


def optimize_cardinality_from_returns(
    returns: pd.DataFrame,
    max_assets: int = 5,
    method: Literal["markowitz", "sa"] = "markowitz",
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    risk_free_rate: float = 0.0,
    periods: int = 252,
    sa_config: SAConfig | None = None,
    n_random_subsets: int = 80,
    seed: int | None = 42,
) -> OptimizationResult:
    """Point d'entrée cardinalité Markowitz ou SA."""
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    if method == "markowitz":
        return markowitz_cardinality(
            mean_returns,
            cov_matrix,
            max_assets=max_assets,
            objective=objective,
            risk_free_rate=risk_free_rate,
            periods=periods,
            n_random_subsets=n_random_subsets,
            seed=seed,
        )
    return sa_cardinality(
        mean_returns,
        cov_matrix,
        max_assets=max_assets,
        objective=objective,
        risk_free_rate=risk_free_rate,
        periods=periods,
        config=sa_config,
    )
