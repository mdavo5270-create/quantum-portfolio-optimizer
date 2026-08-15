"""Tests du recuit simulé (quantum-inspired v1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.optimizer.simulated_annealing import (
    SAConfig,
    compare_with_markowitz,
    optimize_sa_from_returns,
)


@pytest.fixture
def synthetic_returns() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n_days = 400
    market = rng.normal(0.0004, 0.01, n_days)
    return pd.DataFrame(
        {
            "A": market + rng.normal(0.0001, 0.008, n_days),
            "B": market * 0.8 + rng.normal(0.0002, 0.012, n_days),
            "C": market * 1.1 + rng.normal(-0.0001, 0.014, n_days),
            "D": rng.normal(0.0003, 0.006, n_days),
        }
    )


def test_sa_weights_sum_to_one(synthetic_returns):
    result = optimize_sa_from_returns(
        synthetic_returns,
        objective="max_sharpe",
        config=SAConfig(n_steps=1500, seed=0),
    )
    assert result.success
    assert abs(result.weights.sum() - 1.0) < 1e-6
    assert (result.weights >= -1e-8).all()


def test_sa_min_vol_weights(synthetic_returns):
    result = optimize_sa_from_returns(
        synthetic_returns,
        objective="min_vol",
        config=SAConfig(n_steps=1500, seed=1),
    )
    assert result.success
    assert abs(result.weights.sum() - 1.0) < 1e-6
    assert (result.weights >= -1e-8).all()


def test_sa_competitive_with_markowitz_sharpe(synthetic_returns):
    """Le SA doit atteindre un Sharpe proche de Markowitz (tolérance large)."""
    cmp = compare_with_markowitz(
        synthetic_returns,
        objective="max_sharpe",
        config=SAConfig(n_steps=3000, seed=42, step_size=0.08),
    )
    mk = cmp["markowitz"]
    sa = cmp["simulated_annealing"]
    # SA ne doit pas être catastrophiquement pire (tolérance 25 % relatif ou 0.15 abs)
    assert sa.sharpe >= mk.sharpe * 0.75 - 0.05


def test_sa_competitive_with_markowitz_vol(synthetic_returns):
    cmp = compare_with_markowitz(
        synthetic_returns,
        objective="min_vol",
        config=SAConfig(n_steps=3000, seed=7),
    )
    mk = cmp["markowitz"]
    sa = cmp["simulated_annealing"]
    # Vol SA ≤ 1.25 × vol Markowitz
    assert sa.volatility <= mk.volatility * 1.25 + 1e-6


def test_compare_returns_both_results(synthetic_returns):
    cmp = compare_with_markowitz(
        synthetic_returns,
        objective="max_sharpe",
        config=SAConfig(n_steps=800, seed=3),
    )
    assert "markowitz" in cmp
    assert "simulated_annealing" in cmp
    assert "delta_sharpe" in cmp
