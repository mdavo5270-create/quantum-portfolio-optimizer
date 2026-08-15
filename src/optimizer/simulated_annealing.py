"""Optimisation de portefeuille par recuit simulé (simulated annealing).

Approche quantum-inspired : exploration stochastique inspirée du recuit
métallurgique et des transitions d'énergie en physique statistique.
Contrairement à Markowitz (gradient / programmation quadratique), le recuit
peut accepter temporairement des solutions moins bonnes pour échapper aux
optima locaux.

Contraintes : poids ≥ 0 (long-only), somme = 1.

Avertissement : outil expérimental de simulation. Ce n'est PAS un conseil financier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from src.classical_baseline.markowitz import OptimizationResult, portfolio_performance


@dataclass
class SAConfig:
    """Hyperparamètres du recuit simulé."""

    n_steps: int = 5000
    t0: float = 1.0
    t_min: float = 1e-4
    cooling: float = 0.995  # facteur géométrique par pas
    step_size: float = 0.05  # amplitude de perturbation des poids
    seed: int | None = 42


def _normalize(w: np.ndarray) -> np.ndarray:
    """Projette sur le simplexe (poids ≥ 0, somme = 1)."""
    w = np.clip(w, 0.0, None)
    s = w.sum()
    if s < 1e-15:
        return np.ones_like(w) / len(w)
    return w / s


def _neighbor(w: np.ndarray, step_size: float, rng: np.random.Generator) -> np.ndarray:
    """Génère un voisin en perturbant deux poids (échange partiel) ou bruit gaussien."""
    n = len(w)
    w_new = w.copy()
    # Stratégie mixte : 50 % bruit gaussien, 50 % transfert entre deux actifs
    if rng.random() < 0.5 and n >= 2:
        i, j = rng.choice(n, size=2, replace=False)
        delta = rng.uniform(0, step_size) * w_new[i]
        w_new[i] -= delta
        w_new[j] += delta
    else:
        w_new = w_new + rng.normal(0.0, step_size, size=n)
    return _normalize(w_new)


def _energy(
    w: np.ndarray,
    mu: np.ndarray,
    Sigma: np.ndarray,
    objective: Literal["max_sharpe", "min_vol"],
    risk_free_rate_daily: float = 0.0,
) -> float:
    """Énergie à minimiser (plus bas = meilleur)."""
    port_ret = float(np.dot(w, mu))
    port_var = float(w @ Sigma @ w)
    port_vol = np.sqrt(max(port_var, 0.0))

    if objective == "min_vol":
        return port_vol

    # max_sharpe → minimiser -Sharpe
    if port_vol < 1e-12:
        return 0.0
    sharpe = (port_ret - risk_free_rate_daily) / port_vol
    return -sharpe


def simulated_annealing(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    risk_free_rate: float = 0.0,
    periods: int = 252,
    config: SAConfig | None = None,
) -> OptimizationResult:
    """Optimise les poids par recuit simulé.

    Parameters
    ----------
    mean_returns :
        Rendements moyens journaliers (index = actifs).
    cov_matrix :
        Matrice de covariance journalière.
    objective :
        "max_sharpe" ou "min_vol".
    risk_free_rate :
        Taux sans risque annualisé.
    periods :
        Nombre de périodes par an (252 pour journalier).
    config :
        Hyperparamètres SA (optionnel).
    """
    cfg = config or SAConfig()
    rng = np.random.default_rng(cfg.seed)

    assets = mean_returns.index.tolist()
    n = len(assets)
    mu = mean_returns.values.astype(float)
    Sigma = cov_matrix.values.astype(float)
    daily_rf = risk_free_rate / periods

    # État initial : équipondéré
    w = np.ones(n) / n
    e = _energy(w, mu, Sigma, objective, daily_rf)
    best_w, best_e = w.copy(), e

    t = cfg.t0
    accepted = 0

    for step in range(cfg.n_steps):
        w_cand = _neighbor(w, cfg.step_size, rng)
        e_cand = _energy(w_cand, mu, Sigma, objective, daily_rf)
        delta = e_cand - e

        # Acceptation Metropolis
        if delta < 0 or rng.random() < np.exp(-delta / max(t, 1e-15)):
            w, e = w_cand, e_cand
            accepted += 1
            if e < best_e:
                best_w, best_e = w.copy(), e

        t = max(t * cfg.cooling, cfg.t_min)

    best_w = _normalize(best_w)
    ret, vol, sharpe = portfolio_performance(best_w, mu, Sigma, periods)
    if risk_free_rate != 0.0 and vol > 1e-12:
        sharpe = (ret - risk_free_rate) / vol

    weights = pd.Series(best_w, index=assets)
    msg = (
        f"SA terminé — steps={cfg.n_steps}, acceptés={accepted}, "
        f"T_final={t:.2e}, énergie={best_e:.6f}"
    )

    return OptimizationResult(
        weights=weights,
        expected_return=ret,
        volatility=vol,
        sharpe=sharpe,
        success=True,
        message=msg,
    )


def optimize_sa_from_returns(
    returns: pd.DataFrame,
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    risk_free_rate: float = 0.0,
    periods: int = 252,
    config: SAConfig | None = None,
) -> OptimizationResult:
    """Point d'entrée : optimise à partir d'un DataFrame de rendements."""
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    return simulated_annealing(
        mean_returns,
        cov_matrix,
        objective=objective,
        risk_free_rate=risk_free_rate,
        periods=periods,
        config=config,
    )


def compare_with_markowitz(
    returns: pd.DataFrame,
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    risk_free_rate: float = 0.0,
    periods: int = 252,
    config: SAConfig | None = None,
) -> dict:
    """Compare recuit simulé vs Markowitz sur les mêmes données.

    Returns
    -------
    dict avec clés 'markowitz', 'simulated_annealing', 'delta_sharpe', 'delta_vol'.
    """
    from src.classical_baseline.markowitz import optimize_from_returns

    method = "max_sharpe" if objective == "max_sharpe" else "min_vol"
    mk = optimize_from_returns(
        returns, method=method, risk_free_rate=risk_free_rate, periods=periods
    )
    sa = optimize_sa_from_returns(
        returns,
        objective=objective,
        risk_free_rate=risk_free_rate,
        periods=periods,
        config=config,
    )

    return {
        "markowitz": mk,
        "simulated_annealing": sa,
        "delta_sharpe": sa.sharpe - mk.sharpe,
        "delta_vol": sa.volatility - mk.volatility,
        "delta_return": sa.expected_return - mk.expected_return,
    }
