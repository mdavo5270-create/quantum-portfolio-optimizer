"""Graphiques de rapport de backtesting.

Avertissement : simulations uniquement — pas un conseil financier.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend non interactif (CI / scripts)
import matplotlib.pyplot as plt
import pandas as pd

from src.backtest.engine import BacktestResult


def plot_equity_comparison(
    results: dict[str, BacktestResult],
    title: str = "Courbes de valeur — Markowitz vs Recuit simulé",
    output_path: str | Path | None = None,
) -> Path | None:
    """Trace les courbes d'équité côte à côte.

    Returns
    -------
    Path du fichier sauvegardé, ou None si pas de output_path.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, res in results.items():
        label = f"{name} (Sharpe={res.metrics.sharpe:.2f}, MDD={res.metrics.max_drawdown:.1%})"
        ax.plot(res.equity_curve.index, res.equity_curve.values, label=label, linewidth=1.5)

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Valeur du portefeuille (base 1)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=120)
        plt.close(fig)
        return path

    plt.close(fig)
    return None


def metrics_table(results: dict[str, BacktestResult]) -> pd.DataFrame:
    """Tableau récapitulatif des métriques."""
    rows = {}
    for name, res in results.items():
        m = res.metrics
        rows[name] = {
            "Rendement total": m.total_return,
            "Rendement annualisé": m.annualized_return,
            "Volatilité annualisée": m.annualized_volatility,
            "Sharpe": m.sharpe,
            "Max drawdown": m.max_drawdown,
            "Jours": m.n_days,
        }
    return pd.DataFrame(rows).T
