"""Optimisation classique (Markowitz / frontière efficiente) pour comparaison."""

from src.classical_baseline.markowitz import (
    OptimizationResult,
    maximize_sharpe,
    minimize_volatility,
    optimize_from_returns,
    portfolio_performance,
)

__all__ = [
    "OptimizationResult",
    "maximize_sharpe",
    "minimize_volatility",
    "optimize_from_returns",
    "portfolio_performance",
]
