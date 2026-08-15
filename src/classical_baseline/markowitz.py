"""Optimisation de portefeuille classique à la Markowitz (mean-variance).

Implémente :
- Minimisation de la variance pour un rendement cible
- Maximisation du ratio de Sharpe (sans taux sans risque pour simplifier, ou avec rf=0)
- Contraintes : poids positifs (long-only) et somme des poids = 1

Utilise scipy.optimize.minimize (SLSQP).

Avertissement : outil expérimental de simulation. Ce n'est PAS un conseil financier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.optimize import minimize


@dataclass
class OptimizationResult:
    """Résultat d'une optimisation de portefeuille."""

    weights: pd.Series          # poids optimaux (index = actifs)
    expected_return: float      # rendement attendu annualisé (approx)
    volatility: float           # volatilité annualisée
    sharpe: float               # ratio de Sharpe (rf=0)
    success: bool
    message: str


def _annualize_return(mean_daily: float, periods: int = 252) -> float:
    return mean_daily * periods


def _annualize_vol(std_daily: float, periods: int = 252) -> float:
    return std_daily * np.sqrt(periods)


def portfolio_performance(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    periods: int = 252,
) -> tuple[float, float, float]:
    """Calcule rendement, volatilité et Sharpe (rf=0) annualisés."""
    ret = float(np.dot(weights, mean_returns) * periods)
    vol = float(np.sqrt(weights @ cov_matrix @ weights) * np.sqrt(periods))
    sharpe = ret / vol if vol > 1e-12 else 0.0
    return ret, vol, sharpe


def minimize_volatility(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    target_return: float | None = None,
    periods: int = 252,
) -> OptimizationResult:
    """Trouve les poids qui minimisent la volatilité.

    Si target_return est fourni (annualisé), on l'impose comme contrainte.
    Sinon on cherche purement le portefeuille de variance minimale (GMV).
    """
    assets = mean_returns.index.tolist()
    n = len(assets)
    mu = mean_returns.values
    Sigma = cov_matrix.values

    def objective(w: np.ndarray) -> float:
        return float(w @ Sigma @ w)

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    if target_return is not None:
        # target_return est annualisé → on convertit en daily
        daily_target = target_return / periods
        constraints.append(
            {"type": "eq", "fun": lambda w: np.dot(w, mu) - daily_target}
        )

    bounds = tuple((0.0, 1.0) for _ in range(n))  # long-only
    x0 = np.array([1.0 / n] * n)

    res = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    weights = pd.Series(res.x if res.success else x0, index=assets)
    weights = weights.clip(lower=0.0)
    weights = weights / weights.sum()  # renormalisation de sécurité

    ret, vol, sharpe = portfolio_performance(weights.values, mu, Sigma, periods)

    return OptimizationResult(
        weights=weights,
        expected_return=ret,
        volatility=vol,
        sharpe=sharpe,
        success=bool(res.success),
        message=str(res.message),
    )


def maximize_sharpe(
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods: int = 252,
) -> OptimizationResult:
    """Maximise le ratio de Sharpe (rendement excessif / volatilité).

    risk_free_rate est annualisé (ex. 0.02 pour 2 %).
    """
    assets = mean_returns.index.tolist()
    n = len(assets)
    mu = mean_returns.values
    Sigma = cov_matrix.values
    daily_rf = risk_free_rate / periods

    def neg_sharpe(w: np.ndarray) -> float:
        port_ret = np.dot(w, mu)
        port_vol = np.sqrt(w @ Sigma @ w)
        if port_vol < 1e-12:
            return 0.0
        return -((port_ret - daily_rf) / port_vol)

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = tuple((0.0, 1.0) for _ in range(n))
    x0 = np.array([1.0 / n] * n)

    res = minimize(
        neg_sharpe,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    weights = pd.Series(res.x if res.success else x0, index=assets)
    weights = weights.clip(lower=0.0)
    weights = weights / weights.sum()

    ret, vol, sharpe = portfolio_performance(weights.values, mu, Sigma, periods)
    # Ajustement Sharpe avec rf si nécessaire
    if risk_free_rate != 0.0 and vol > 1e-12:
        sharpe = (ret - risk_free_rate) / vol

    return OptimizationResult(
        weights=weights,
        expected_return=ret,
        volatility=vol,
        sharpe=sharpe,
        success=bool(res.success),
        message=str(res.message),
    )


def optimize_from_returns(
    returns: pd.DataFrame,
    method: str = "max_sharpe",
    target_return: float | None = None,
    risk_free_rate: float = 0.0,
    periods: int = 252,
) -> OptimizationResult:
    """Point d'entrée principal : optimise à partir d'un DataFrame de rendements.

    Parameters
    ----------
    returns :
        DataFrame de rendements journaliers (index=dates, colonnes=actifs).
    method :
        "max_sharpe" ou "min_vol".
    target_return :
        Uniquement pour method="min_vol" (rendement annualisé cible).
    """
    mean_returns = returns.mean()
    cov_matrix = returns.cov()

    if method == "max_sharpe":
        return maximize_sharpe(mean_returns, cov_matrix, risk_free_rate, periods)
    elif method == "min_vol":
        return minimize_volatility(mean_returns, cov_matrix, target_return, periods)
    else:
        raise ValueError('method doit être "max_sharpe" ou "min_vol".')
