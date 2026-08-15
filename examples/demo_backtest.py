"""Backtesting comparatif Markowitz vs recuit simulé sur 3 périodes.

Exécution :
    python examples/demo_backtest.py

Génère des graphiques dans artifacts/backtest/ (ou ./output/backtest/).

Avertissement : ce n'est PAS un conseil financier.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.backtest.engine import compare_backtests
from src.data.market_data import prepare_data
from src.optimizer.simulated_annealing import SAConfig
from src.visualization.backtest_plots import metrics_table, plot_equity_comparison

# Trois fenêtres historiques distinctes
PERIODS = [
    ("2018-2020 (pré + début COVID)", "2018-01-01", "2020-12-31"),
    ("2020-2022 (COVID + inflation)", "2020-01-01", "2022-12-31"),
    ("2022-2025 (hausse des taux)", "2022-01-01", "2025-12-31"),
]

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN"]
OUT_DIR = _ROOT / "output" / "backtest"


def _print_metrics(label: str, table) -> None:
    print(f"\n=== {label} ===")
    # Affichage lisible
    fmt = table.copy()
    for col in ["Rendement total", "Rendement annualisé", "Volatilité annualisée", "Max drawdown"]:
        if col in fmt.columns:
            fmt[col] = fmt[col].map(lambda x: f"{x:.1%}")
    if "Sharpe" in fmt.columns:
        fmt["Sharpe"] = fmt["Sharpe"].map(lambda x: f"{x:.2f}")
    print(fmt.to_string())


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sa_cfg = SAConfig(n_steps=2000, seed=42)

    print("Téléchargement des données (peut prendre un moment)...")
    _, returns_full, report = prepare_data(TICKERS, start="2018-01-01", verbose=True)
    if len(report.succeeded) < 2:
        print("Pas assez d'actifs.")
        return

    for name, start, end in PERIODS:
        mask = (returns_full.index >= start) & (returns_full.index <= end)
        rets = returns_full.loc[mask].dropna()
        if len(rets) < 300:
            print(f"\nPériode '{name}' : données insuffisantes ({len(rets)} jours), ignorée.")
            continue

        print(f"\nBacktest — {name} ({len(rets)} jours)...")
        results = compare_backtests(
            rets,
            train_days=min(252, len(rets) // 3),
            test_days=min(63, len(rets) // 8),
            sa_config=sa_cfg,
        )
        table = metrics_table(results)
        _print_metrics(name, table)

        safe_name = name.split("(")[0].strip().replace(" ", "_").replace("–", "-")
        plot_path = OUT_DIR / f"equity_{safe_name}.png"
        plot_equity_comparison(
            results,
            title=f"Backtest — {name}\n(ce n'est PAS un conseil financier)",
            output_path=plot_path,
        )
        print(f"Graphique sauvegardé : {plot_path}")

    print("\nAvertissement : ce n'est PAS un conseil financier.")
    print(f"Graphiques dans : {OUT_DIR}")


if __name__ == "__main__":
    main()
