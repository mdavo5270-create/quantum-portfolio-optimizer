"""Récupération et nettoyage des données de marché historiques.

Utilise yfinance (données gratuites Yahoo Finance) pour télécharger
les prix ajustés d'actions (et certains ETFs / cryptos via tickers Yahoo).

Avertissement : ce module sert uniquement à la simulation et au backtesting.
Ce n'est PAS un conseil financier.
"""

from __future__ import annotations

from typing import Sequence

import pandas as pd
import yfinance as yf


def fetch_prices(
    tickers: Sequence[str],
    start: str = "2018-01-01",
    end: str | None = None,
    auto_adjust: bool = True,
) -> pd.DataFrame:
    """Télécharge les prix de clôture ajustés pour une liste de tickers.

    Parameters
    ----------
    tickers :
        Liste de symboles (ex. ["AAPL", "MSFT", "GOOGL"]).
    start :
        Date de début (YYYY-MM-DD).
    end :
        Date de fin (YYYY-MM-DD). None = aujourd'hui.
    auto_adjust :
        Si True, utilise les prix ajustés (dividendes / splits).

    Returns
    -------
    DataFrame indexé par date, colonnes = tickers, valeurs = prix de clôture.
    """
    if not tickers:
        raise ValueError("La liste de tickers ne peut pas être vide.")

    data = yf.download(
        list(tickers),
        start=start,
        end=end,
        auto_adjust=auto_adjust,
        progress=False,
        threads=True,
    )

    if data.empty:
        raise RuntimeError(
            f"Aucune donnée récupérée pour {tickers}. "
            "Vérifiez les symboles et la connectivité réseau."
        )

    # yfinance renvoie un MultiIndex si plusieurs tickers
    if isinstance(data.columns, pd.MultiIndex):
        # On prend uniquement la colonne 'Close'
        if "Close" in data.columns.get_level_values(0):
            prices = data["Close"].copy()
        else:
            # Fallback : première colonne de niveau 0
            prices = data.xs(data.columns.levels[0][0], axis=1, level=0).copy()
    else:
        # Un seul ticker
        prices = data[["Close"]].copy() if "Close" in data.columns else data.copy()
        if len(tickers) == 1:
            prices.columns = [tickers[0]]

    # Nettoyage basique
    prices = prices.dropna(how="all")
    prices = prices.ffill().bfill()  # rares trous intra-jour
    prices = prices.dropna(axis=1, how="all")  # colonnes entièrement vides

    if prices.empty:
        raise RuntimeError("Après nettoyage, aucune donnée exploitable.")

    return prices


def compute_returns(prices: pd.DataFrame, method: str = "log") -> pd.DataFrame:
    """Calcule les rendements à partir des prix.

    Parameters
    ----------
    prices :
        DataFrame de prix (index = dates, colonnes = actifs).
    method :
        "log" (log-returns, recommandé pour l'optimisation) ou "simple".

    Returns
    -------
    DataFrame de rendements (même index/colonnes, première ligne NaN supprimée).
    """
    if method == "log":
        returns = (prices / prices.shift(1)).apply(lambda x: pd.Series(
            __import__("numpy").log(x), index=x.index
        ))
    elif method == "simple":
        returns = prices.pct_change()
    else:
        raise ValueError('method doit être "log" ou "simple".')

    return returns.dropna(how="all")


def prepare_data(
    tickers: Sequence[str],
    start: str = "2018-01-01",
    end: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pipeline complet : téléchargement + nettoyage + rendements log.

    Returns
    -------
    prices, returns
    """
    prices = fetch_prices(tickers, start=start, end=end)
    returns = compute_returns(prices, method="log")
    # Alignement strict : on garde seulement les dates communes non-NaN
    returns = returns.dropna()
    prices = prices.loc[returns.index]
    return prices, returns
