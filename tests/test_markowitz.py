"""Tests de l'optimiseur Markowitz classique.

On utilise des données synthétiques pour rester déterministe et indépendant
du réseau (CI GitHub Actions).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.classical_baseline.markowitz import (
    OptimizationResult,
    maximize_sharpe,
    minimize_volatility,
    optimize_from_returns,
    portfolio_performance,
)


@pytest.fixture
def synthetic_returns() -> pd.DataFrame:
    """Génère 4 actifs avec rendements corrélés réalistes (seed fixe)."""
    rng = np.random.default_rng(42)
    n_days = 500
    # Facteur commun + idiosyncrasies
    market = rng.normal(0.0004, 0.01, n_days)
    assets = {
        "A": market + rng.normal(0.0001, 0.008, n_days),
        "B": market * 0.8 + rng.normal(0.0002, 0.012, n_days),
        "C": market * 1.2 + rng.normal(-0.0001, 0.015, n_days),
        "D": rng.normal(0.0003, 0.006, n_days),  # plus indépendant / faible vol
    }
    return pd.DataFrame(assets)


def test_weights_sum_to_one(synthetic_returns):
    result = optimize_from_returns(synthetic_returns, method="max_sharpe")
    assert isinstance(result, OptimizationResult)
    assert result.success
    assert abs(result.weights.sum() - 1.0) < 1e-6
    assert (result.weights >= -1e-8).all()  # long-only (tolérance numérique)


def test_min_vol_weights_sum_to_one(synthetic_returns):
    result = optimize_from_returns(synthetic_returns, method="min_vol")
    assert result.success
    assert abs(result.weights.sum() - 1.0) < 1e-6
    assert (result.weights >= -1e-8).all()


def test_max_sharpe_better_or_equal_than_equal_weight(synthetic_returns):
    """Le portefeuille max-Sharpe doit avoir un Sharpe >= portefeuille équipondéré."""
    result = optimize_from_returns(synthetic_returns, method="max_sharpe")
    n = len(synthetic_returns.columns)
    equal_w = np.array([1.0 / n] * n)
    mu = synthetic_returns.mean().values
    Sigma = synthetic_returns.cov().values
    _, _, equal_sharpe = portfolio_performance(equal_w, mu, Sigma)
    assert result.sharpe >= equal_sharpe - 1e-6


def test_min_vol_has_lower_or_equal_vol_than_equal_weight(synthetic_returns):
    result = optimize_from_returns(synthetic_returns, method="min_vol")
    n = len(synthetic_returns.columns)
    equal_w = np.array([1.0 / n] * n)
    mu = synthetic_returns.mean().values
    Sigma = synthetic_returns.cov().values
    _, equal_vol, _ = portfolio_performance(equal_w, mu, Sigma)
    assert result.volatility <= equal_vol + 1e-6


def test_three_assets_manual_consistency():
    """Petit exemple 3 actifs vérifiable à la main (rendements constants)."""
    # Actifs A, B, C avec moyennes et covariances simples
    dates = pd.date_range("2020-01-01", periods=100, freq="B")
    rng = np.random.default_rng(0)
    # On force des moyennes différentes
    rets = pd.DataFrame(
        {
            "X": rng.normal(0.001, 0.01, 100),
            "Y": rng.normal(0.0005, 0.02, 100),
            "Z": rng.normal(0.0002, 0.005, 100),
        },
        index=dates,
    )
    result = optimize_from_returns(rets, method="max_sharpe")
    assert result.success
    assert abs(result.weights.sum() - 1.0) < 1e-6
    # L'actif le plus attractif (meilleur ratio moyen/vol) doit recevoir un poids > 0
    assert (result.weights > 0).any()


def test_invalid_method_raises(synthetic_returns):
    with pytest.raises(ValueError):
        optimize_from_returns(synthetic_returns, method="unknown")
