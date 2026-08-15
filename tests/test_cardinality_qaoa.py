"""Tests contrainte de cardinalité et QAOA simulé."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.optimizer.cardinality import optimize_cardinality_from_returns
from src.optimizer.qaoa_portfolio import QAOAConfig, optimize_qaoa_from_returns
from src.optimizer.simulated_annealing import SAConfig


@pytest.fixture
def returns_12() -> pd.DataFrame:
    rng = np.random.default_rng(123)
    n_days, n_assets = 300, 12
    market = rng.normal(0.0003, 0.01, n_days)
    data = {}
    for i in range(n_assets):
        data[f"A{i}"] = market * rng.uniform(0.5, 1.2) + rng.normal(0, 0.008, n_days)
    return pd.DataFrame(data)


def test_markowitz_cardinality_respects_k(returns_12):
    res = optimize_cardinality_from_returns(
        returns_12, max_assets=4, method="markowitz", n_random_subsets=20, seed=0
    )
    n_active = (res.weights > 1e-6).sum()
    assert n_active <= 4
    assert abs(res.weights.sum() - 1.0) < 1e-5


def test_sa_cardinality_respects_k(returns_12):
    res = optimize_cardinality_from_returns(
        returns_12,
        max_assets=3,
        method="sa",
        sa_config=SAConfig(n_steps=1500, seed=1),
    )
    n_active = (res.weights > 1e-6).sum()
    assert n_active <= 3
    assert abs(res.weights.sum() - 1.0) < 1e-5


def test_qaoa_cardinality_respects_k(returns_12):
    # n=12 ≤ 16 → statevector
    res = optimize_qaoa_from_returns(
        returns_12,
        max_assets=4,
        config=QAOAConfig(p=1, max_assets=4, seed=2),
    )
    n_active = (res.weights > 1e-6).sum()
    assert n_active <= 4
    assert abs(res.weights.sum() - 1.0) < 1e-5
    assert res.success


def test_qaoa_sampling_mode_large_n():
    rng = np.random.default_rng(0)
    n_days, n_assets = 200, 20
    rets = pd.DataFrame(
        rng.normal(0.0002, 0.01, (n_days, n_assets)),
        columns=[f"S{i}" for i in range(n_assets)],
    )
    res = optimize_qaoa_from_returns(
        rets,
        max_assets=5,
        config=QAOAConfig(p=1, max_assets=5, n_samples=128, seed=0),
    )
    assert (res.weights > 1e-6).sum() <= 5
