"""Tests du module de données de marché.

Les tests de téléchargement réel (yfinance) sont optionnels / skippés en CI
pour éviter les dépendances réseau flakiness. On teste surtout le nettoyage
et le calcul de rendements sur données synthétiques.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data.market_data import FetchReport, compute_returns, fetch_prices


def test_compute_returns_log():
    prices = pd.DataFrame(
        {"A": [100.0, 110.0, 105.0], "B": [50.0, 50.0, 55.0]},
        index=pd.date_range("2020-01-01", periods=3),
    )
    rets = compute_returns(prices, method="log")
    assert len(rets) == 2
    expected_a = np.log(110 / 100)
    assert abs(rets["A"].iloc[0] - expected_a) < 1e-10


def test_compute_returns_simple():
    prices = pd.DataFrame(
        {"A": [100.0, 110.0]},
        index=pd.date_range("2020-01-01", periods=2),
    )
    rets = compute_returns(prices, method="simple")
    assert abs(rets["A"].iloc[0] - 0.10) < 1e-10


def test_compute_returns_invalid_method():
    prices = pd.DataFrame({"A": [1.0, 2.0]})
    with pytest.raises(ValueError):
        compute_returns(prices, method="magic")


def test_fetch_prices_empty_list():
    with pytest.raises(ValueError):
        fetch_prices([])


def test_fetch_report_summary():
    report = FetchReport(
        requested=["A", "B", "C"],
        succeeded=["A", "B"],
        failed={"C": "timeout"},
    )
    assert not report.all_succeeded
    text = report.summary()
    assert "Réussis : 2" in text
    assert "Échoués : 1" in text
    assert "A, B" in text
    assert "C" in text


@pytest.mark.network
def test_fetch_prices_real_smoke():
    """Test optionnel de connectivité (marqué network, non exécuté par défaut)."""
    prices, report = fetch_prices(["AAPL"], start="2024-01-01", end="2024-02-01")
    assert not prices.empty
    assert "AAPL" in report.succeeded
    assert report.all_succeeded or "AAPL" in prices.columns
