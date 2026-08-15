"""Récupération et nettoyage des données de marché historiques.

Utilise yfinance (données gratuites Yahoo Finance) pour télécharger
les prix ajustés d'actions (et certains ETFs / cryptos via tickers Yahoo).

Améliorations de robustesse (Phase 1) :
- Téléchargement séquentiel (évite les conflits SQLite "database is locked")
- Retry automatique avec backoff progressif (surtout sur rate-limit Yahoo)
- Fallback via Ticker.history() si yf.download échoue
- Cache local au projet (évite le cache global partagé et corrompu)
- Rapport clair des actifs réussis / échoués

Avertissement : ce module sert uniquement à la simulation et au backtesting.
Ce n'est PAS un conseil financier.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import yfinance as yf

# Cache local au projet (évite ~/.cache/py-yfinance partagé et souvent vérouillé)
_DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[2] / ".yfinance_cache"


@dataclass
class FetchReport:
    """Rapport de téléchargement : quels tickers ont réussi / échoué."""

    requested: list[str]
    succeeded: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)  # ticker -> message d'erreur

    @property
    def all_succeeded(self) -> bool:
        return len(self.failed) == 0 and len(self.succeeded) == len(self.requested)

    def summary(self) -> str:
        lines = [
            f"Demandés : {len(self.requested)} | Réussis : {len(self.succeeded)} | Échoués : {len(self.failed)}"
        ]
        if self.succeeded:
            lines.append(f"  ✓ Réussis : {', '.join(self.succeeded)}")
        if self.failed:
            lines.append("  ✗ Échoués :")
            for t, msg in self.failed.items():
                lines.append(f"      - {t} : {msg}")
        return "\n".join(lines)


def _ensure_cache_dir(cache_dir: Path | None = None) -> Path:
    """Crée le dossier de cache local et configure yfinance si possible."""
    path = cache_dir or _DEFAULT_CACHE_DIR
    path.mkdir(parents=True, exist_ok=True)
    try:
        yf.set_tz_cache_location(str(path))
    except Exception:
        pass
    os.environ.setdefault("YFINANCE_CACHE_DIR", str(path))
    return path


def _is_transient(msg: str) -> bool:
    msg = msg.lower()
    return any(
        k in msg
        for k in (
            "database is locked",
            "rate limited",
            "too many requests",
            "timeout",
            "timed out",
            "connection",
            "temporarily",
            "possibly delisted",  # souvent un faux positif transitoire Yahoo
            "aucune donnée renvoyée",
            "no price data",
            "failed download",
        )
    )


def _extract_close(data: pd.DataFrame, ticker: str) -> pd.Series:
    """Extrait une Series de prix de clôture depuis le résultat yfinance."""
    if data is None or data.empty:
        raise RuntimeError("aucune donnée renvoyée (symbole invalide ou période vide)")

    if isinstance(data.columns, pd.MultiIndex):
        if "Close" in data.columns.get_level_values(0):
            series = data["Close"].copy()
            if isinstance(series, pd.DataFrame):
                series = series.iloc[:, 0]
        else:
            series = data.iloc[:, 0].copy()
    else:
        if "Close" in data.columns:
            series = data["Close"].copy()
        else:
            series = data.iloc[:, 0].copy()

    series.name = ticker
    series = series.dropna()
    if series.empty:
        raise RuntimeError("série de prix vide après nettoyage")
    return series


def _download_one(
    ticker: str,
    start: str,
    end: str | None,
    auto_adjust: bool,
    max_retries: int = 4,
    base_delay: float = 2.0,
) -> pd.Series:
    """Télécharge un seul ticker avec retries + fallback Ticker.history().

    Raises
    ------
    RuntimeError
        Si tous les essais échouent.
    """
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            # Tentative 1..n-1 : yf.download ; dernière tentative : Ticker.history
            if attempt < max_retries:
                data = yf.download(
                    ticker,
                    start=start,
                    end=end,
                    auto_adjust=auto_adjust,
                    progress=False,
                    threads=False,
                    timeout=30,
                )
            else:
                t = yf.Ticker(ticker)
                data = t.history(start=start, end=end, auto_adjust=auto_adjust, timeout=30)

            return _extract_close(data, ticker)

        except Exception as exc:
            last_error = exc
            msg = str(exc)
            if attempt < max_retries and _is_transient(msg):
                # Backoff progressif : 2s, 4s, 8s... (plus long sur rate-limit)
                delay = base_delay * (2 ** (attempt - 1))
                if "rate" in msg.lower() or "too many" in msg.lower():
                    delay = max(delay, 8.0 * attempt)
                time.sleep(delay)
                continue
            break

    raise RuntimeError(f"échec après {max_retries} tentatives : {last_error}")


def fetch_prices(
    tickers: Sequence[str],
    start: str = "2018-01-01",
    end: str | None = None,
    auto_adjust: bool = True,
    max_retries: int = 4,
    cache_dir: Path | str | None = None,
    min_success: int = 1,
    pause_between: float = 0.8,
) -> tuple[pd.DataFrame, FetchReport]:
    """Télécharge les prix de clôture ajustés pour une liste de tickers.

    Téléchargement **séquentiel** (un ticker à la fois) + retries pour éviter
    les erreurs "database is locked" et les rate-limits Yahoo.

    Parameters
    ----------
    tickers :
        Liste de symboles (ex. ["AAPL", "MSFT", "GOOGL"]).
    start, end :
        Période (YYYY-MM-DD).
    auto_adjust :
        Prix ajustés (dividendes / splits).
    max_retries :
        Nombre de tentatives par ticker.
    cache_dir :
        Dossier de cache local (défaut : .yfinance_cache à la racine du projet).
    min_success :
        Nombre minimum de tickers qui doivent réussir, sinon RuntimeError.
    pause_between :
        Pause (secondes) entre deux tickers pour limiter le rate-limit Yahoo.

    Returns
    -------
    prices : DataFrame (index=dates, colonnes=tickers réussis)
    report : FetchReport (détail succès / échecs)
    """
    if not tickers:
        raise ValueError("La liste de tickers ne peut pas être vide.")

    _ensure_cache_dir(Path(cache_dir) if cache_dir else None)

    report = FetchReport(requested=list(tickers))
    series_list: list[pd.Series] = []

    for i, ticker in enumerate(tickers):
        if i > 0 and pause_between > 0:
            time.sleep(pause_between)
        try:
            s = _download_one(
                ticker,
                start=start,
                end=end,
                auto_adjust=auto_adjust,
                max_retries=max_retries,
            )
            series_list.append(s)
            report.succeeded.append(ticker)
        except Exception as exc:
            report.failed[ticker] = str(exc)

    if len(report.succeeded) < min_success:
        raise RuntimeError(
            f"Trop peu d'actifs récupérés ({len(report.succeeded)}/{len(tickers)}).\n"
            + report.summary()
        )

    if not series_list:
        raise RuntimeError("Aucun ticker n'a pu être téléchargé.\n" + report.summary())

    prices = pd.concat(series_list, axis=1, join="outer")
    prices = prices.dropna(how="all")
    prices = prices.ffill().bfill()
    prices = prices.dropna(axis=1, how="all")

    if prices.empty:
        raise RuntimeError("Après nettoyage, aucune donnée exploitable.\n" + report.summary())

    return prices, report


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
        returns = np.log(prices / prices.shift(1))
    elif method == "simple":
        returns = prices.pct_change()
    else:
        raise ValueError('method doit être "log" ou "simple".')

    return returns.dropna(how="all")


def prepare_data(
    tickers: Sequence[str],
    start: str = "2018-01-01",
    end: str | None = None,
    max_retries: int = 4,
    verbose: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, FetchReport]:
    """Pipeline complet : téléchargement + nettoyage + rendements log.

    Returns
    -------
    prices, returns, report
    """
    prices, report = fetch_prices(
        tickers, start=start, end=end, max_retries=max_retries
    )

    if verbose:
        print(report.summary())
        if report.failed:
            print(
                "Attention : l'optimisation ne portera que sur les actifs réussis."
            )

    returns = compute_returns(prices, method="log")
    returns = returns.dropna()
    prices = prices.loc[returns.index]
    return prices, returns, report
