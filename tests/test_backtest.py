"""Tests du moteur de backtesting."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import compare_backtests, compute_metrics, run_backtest
from src.optimizer.simulated_annealing import SAConfig


@pytest.fixture
def long_returns() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 600  # assez pour train 252 + plusieurs tests 63
    market = rng.normal(0.0003, 0.01, n)
    return pd.DataFrame(
        {
            "A": market + rng.normal(0.0001, 0.008, n),
            "B": market * 0.9 + rng.normal(0.0, 0.011, n),
            "C": rng.normal(0.0002, 0.007, n),
        },
        index=pd.bdate_range("2018-01-01", periods=n),
    )


def test_compute_metrics_basic():
    equity = pd.Series([1.0, 1.1, 1.05, 1.2])
    m = compute_metrics(equity, periods=252)
    assert m.total_return == pytest.approx(0.2)
    assert m.max_drawdown < 0  # il y a eu un creux 1.1 → 1.05
    assert m.n_days == 3


def test_run_backtest_markowitz(long_returns):
    res = run_backtest(
        long_returns, method="markowitz", train_days=120, test_days=40
    )
    assert res.method == "markowitz"
    assert len(res.equity_curve) > 50
    assert abs(res.equity_curve.iloc[0] - 1.0) < 1e-9
    assert res.metrics.n_days > 0


def test_run_backtest_sa(long_returns):
    res = run_backtest(
        long_returns,
        method="sa",
        train_days=120,
        test_days=40,
        sa_config=SAConfig(n_steps=500, seed=1),
    )
    assert res.method == "sa"
    assert len(res.equity_curve) > 50


def test_compare_backtests(long_returns):
    results = compare_backtests(
        long_returns,
        train_days=120,
        test_days=40,
        sa_config=SAConfig(n_steps=400, seed=2),
    )
    assert "markowitz" in results and "sa" in results


def test_insufficient_data_raises():
    short = pd.DataFrame({"A": [0.01] * 10, "B": [0.0] * 10})
    with pytest.raises(ValueError):
        run_backtest(short, train_days=50, test_days=20)
