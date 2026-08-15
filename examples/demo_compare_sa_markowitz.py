"""Comparaison Markowitz (classique) vs recuit simulé (quantum-inspired).

Exécution :
    python examples/demo_compare_sa_markowitz.py

Avertissement : ce n'est PAS un conseil financier.
"""

from __future__ import annotations

import examples._bootstrap  # noqa: F401  — ajoute la racine au PYTHONPATH

from src.data.market_data import prepare_data
from src.optimizer.simulated_annealing import SAConfig, compare_with_markowitz


def _print_result(label: str, result) -> None:
    print(f"--- {label} ---")
    print("Poids :")
    for asset, w in result.weights.items():
        print(f"  {asset}: {w:.1%}")
    print(f"Rendement annualisé : {result.expected_return:.1%}")
    print(f"Volatilité          : {result.volatility:.1%}")
    print(f"Sharpe (rf=0)       : {result.sharpe:.2f}")
    print()


def main() -> None:
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    print("Téléchargement des données...")
    _, returns, report = prepare_data(tickers, start="2019-01-01", verbose=True)
    if len(report.succeeded) < 2:
        print("Pas assez d'actifs pour comparer.")
        return

    print()
    print(f"Période : {returns.index[0].date()} → {returns.index[-1].date()}")
    print(f"Actifs  : {list(returns.columns)}")
    print()

    cfg = SAConfig(n_steps=4000, seed=42, step_size=0.06)
    cmp = compare_with_markowitz(returns, objective="max_sharpe", config=cfg)

    _print_result("Markowitz (max Sharpe)", cmp["markowitz"])
    _print_result("Recuit simulé (max Sharpe)", cmp["simulated_annealing"])

    print("=== Écarts (SA − Markowitz) ===")
    print(f"Δ Sharpe   : {cmp['delta_sharpe']:+.3f}")
    print(f"Δ Volatilité : {cmp['delta_vol']:+.2%}")
    print(f"Δ Rendement  : {cmp['delta_return']:+.2%}")
    print()
    print("Avertissement : ce n'est PAS un conseil financier.")


if __name__ == "__main__":
    main()
