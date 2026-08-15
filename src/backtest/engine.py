"""Moteur de backtesting historique.

Principe (walk-forward simple) :
1. Sur une fenêtre d'entraînement, estimer les poids (Markowitz ou SA).
2. Appliquer ces poids sur la période de test suivante (hors échantillon).
3. Mesurer rendement, volatilité, Sharpe, drawdown maximum.

Avertissement : simulation uniquement — ce n'est PAS un conseil financier.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

from src.classical_baseline.markowitz import optimize_from_returns
from src.optimizer.simulated_annealing import SAConfig, optimize_sa_from_returns


@dataclass
class BacktestMetrics:
    """Métriques de performance d'une courbe de valeur."""

    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe: float
    max_drawdown: float
    n_days: int

    def as_dict(self) -> dict:
        return {
            "total_return": self.total_return,
            "annualized_return": self.annualized_return,
            "annualized_volatility": self.annualized_volatility,
            "sharpe": self.sharpe,
            "max_drawdown": self.max_drawdown,
            "n_days": self.n_days,
        }


@dataclass
class BacktestResult:
    """Résultat complet d'un backtest pour une méthode."""

    method: str
    equity_curve: pd.Series
    metrics: BacktestMetrics
    weights_history: list[pd.Series] = field(default_factory=list)


def compute_metrics(equity: pd.Series, periods: int = 252) -> BacktestMetrics:
    """Calcule les métriques à partir d'une courbe de valeur (base 1.0)."""
    if len(equity) < 2:
        return BacktestMetrics(0.0, 0.0, 0.0, 0.0, 0.0, len(equity))

    rets = equity.pct_change().dropna()
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    n = len(rets)
    ann_ret = float((1.0 + total_return) ** (periods / max(n, 1)) - 1.0) if n > 0 else 0.0
    ann_vol = float(rets.std() * np.sqrt(periods)) if n > 1 else 0.0
    sharpe = ann_ret / ann_vol if ann_vol > 1e-12 else 0.0

    # Max drawdown
    peak = equity.cummax()
    dd = (equity - peak) / peak
    max_dd = float(dd.min())  # négatif

    return BacktestMetrics(
        total_return=total_return,
        annualized_return=ann_ret,
        annualized_volatility=ann_vol,
        sharpe=sharpe,
        max_drawdown=max_dd,
        n_days=n,
    )


def _optimize_weights(
    train_returns: pd.DataFrame,
    method: Literal["markowitz", "sa"],
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    sa_config: SAConfig | None = None,
) -> pd.Series:
    if method == "markowitz":
        res = optimize_from_returns(train_returns, method=objective)
    elif method == "sa":
        res = optimize_sa_from_returns(
            train_returns, objective=objective, config=sa_config or SAConfig(n_steps=2000, seed=42)
        )
    else:
        raise ValueError(f"Méthode inconnue : {method}")
    return res.weights


def run_backtest(
    returns: pd.DataFrame,
    method: Literal["markowitz", "sa"] = "markowitz",
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    train_days: int = 252,
    test_days: int = 63,
    sa_config: SAConfig | None = None,
) -> BacktestResult:
    """Backtest walk-forward.

    Parameters
    ----------
    returns :
        Rendements journaliers (index=dates, colonnes=actifs).
    method :
        "markowitz" ou "sa".
    objective :
        Objectif d'optimisation.
    train_days :
        Taille de la fenêtre d'entraînement (ex. 252 ≈ 1 an).
    test_days :
        Taille de chaque segment de test (ex. 63 ≈ 1 trimestre).
    """
    returns = returns.dropna(how="all").copy()
    n = len(returns)
    if n < train_days + test_days:
        raise ValueError(
            f"Pas assez de données ({n} jours) pour train={train_days} + test={test_days}."
        )

    equity_parts: list[pd.Series] = []
    weights_history: list[pd.Series] = []
    cursor = train_days

    while cursor + test_days <= n:
        train = returns.iloc[cursor - train_days : cursor]
        test = returns.iloc[cursor : cursor + test_days]

        # Alignement colonnes sans NaN massifs
        train = train.dropna(axis=1, how="any")
        test = test[train.columns].dropna(how="any")
        if train.shape[1] < 2 or len(test) < 5:
            cursor += test_days
            continue

        w = _optimize_weights(train, method=method, objective=objective, sa_config=sa_config)
        w = w.reindex(test.columns).fillna(0.0)
        if w.sum() <= 0:
            w = pd.Series(1.0 / len(test.columns), index=test.columns)
        else:
            w = w / w.sum()

        weights_history.append(w)

        # Rendements du portefeuille sur la période de test
        port_rets = test.values @ w.values
        # Courbe de valeur relative (départ à 1 pour ce segment)
        segment = pd.Series(np.cumprod(1.0 + port_rets), index=test.index)
        equity_parts.append(segment)
        cursor += test_days

    if not equity_parts:
        raise RuntimeError("Aucun segment de backtest n'a pu être calculé.")

    # Chaînage des segments (valeur continue)
    equity = equity_parts[0]
    for seg in equity_parts[1:]:
        scaled = seg / seg.iloc[0] * equity.iloc[-1]
        # éviter le double comptage du premier point si index se chevauche
        equity = pd.concat([equity, scaled.iloc[1:] if scaled.index[0] in equity.index else scaled])

    equity = equity[~equity.index.duplicated(keep="last")].sort_index()
    # Normaliser base 1.0
    equity = equity / equity.iloc[0]

    metrics = compute_metrics(equity)
    return BacktestResult(
        method=method,
        equity_curve=equity,
        metrics=metrics,
        weights_history=weights_history,
    )


def compare_backtests(
    returns: pd.DataFrame,
    objective: Literal["max_sharpe", "min_vol"] = "max_sharpe",
    train_days: int = 252,
    test_days: int = 63,
    sa_config: SAConfig | None = None,
) -> dict[str, BacktestResult]:
    """Lance Markowitz et SA sur les mêmes données / fenêtres."""
    mk = run_backtest(
        returns, method="markowitz", objective=objective,
        train_days=train_days, test_days=test_days,
    )
    sa = run_backtest(
        returns, method="sa", objective=objective,
        train_days=train_days, test_days=test_days,
        sa_config=sa_config or SAConfig(n_steps=2000, seed=42),
    )
    return {"markowitz": mk, "sa": sa}
