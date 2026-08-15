"""Comparaison Markowitz / SA / QAOA sur un univers large avec cardinalité.

Univers : ~25 actions liquides US
Contrainte : au plus K=5 actifs dans le portefeuille

Exécution :
    python examples/demo_cardinality_qaoa.py

Avertissement : ce n'est PAS un conseil financier.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.data.market_data import prepare_data
from src.optimizer.cardinality import optimize_cardinality_from_returns
from src.optimizer.qaoa_portfolio import QAOAConfig, optimize_qaoa_from_returns
from src.optimizer.simulated_annealing import SAConfig

# Univers diversifié ~25 tickers (tech, santé, finance, conso, industrie, énergie)
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX",
    "JPM", "BAC", "WFC", "GS",
    "JNJ", "PFE", "UNH", "ABBV",
    "PG", "KO", "PEP", "WMT",
    "XOM", "CVX",
    "CAT", "BA", "GE",
]

K = 5  # nombre max d'actifs dans le portefeuille


def _print(label: str, result) -> None:
    active = result.weights[result.weights > 1e-4].sort_values(ascending=False)
    print(f"\n=== {label} ===")
    print(f"Actifs retenus ({len(active)}/{K} max) :")
    for a, w in active.items():
        print(f"  {a}: {w:.1%}")
    print(f"Rendement annualisé : {result.expected_return:.1%}")
    print(f"Volatilité          : {result.volatility:.1%}")
    print(f"Sharpe              : {result.sharpe:.2f}")
    print(f"Info                : {result.message}")


def main() -> None:
    print(f"Univers : {len(TICKERS)} actifs | Contrainte : au plus {K} actifs")
    print("Téléchargement (séquentiel, peut prendre 1–2 min)...\n")

    _, returns, report = prepare_data(TICKERS, start="2019-01-01", verbose=True)
    n_ok = len(report.succeeded)
    print(f"\nActifs disponibles pour l'optimisation : {n_ok}")
    if n_ok < 10:
        print("Trop peu d'actifs récupérés — réessayez plus tard (rate-limit Yahoo).")
        return

    print("\n--- Optimisation sous contrainte de cardinalité ---")

    mk = optimize_cardinality_from_returns(
        returns, max_assets=K, method="markowitz", n_random_subsets=100, seed=42
    )
    _print("Markowitz + cardinalité (top-K + sous-ensembles aléatoires)", mk)

    sa = optimize_cardinality_from_returns(
        returns,
        max_assets=K,
        method="sa",
        sa_config=SAConfig(n_steps=6000, seed=42, step_size=0.08),
    )
    _print("Recuit simulé + cardinalité", sa)

    qaoa = optimize_qaoa_from_returns(
        returns,
        max_assets=K,
        config=QAOAConfig(p=2, max_assets=K, n_samples=256, seed=42),
    )
    _print("QAOA simulé + Markowitz sur sous-ensemble", qaoa)

    print("\n=== Rang par Sharpe ===")
    ranking = sorted(
        [("Markowitz", mk), ("SA", sa), ("QAOA", qaoa)],
        key=lambda x: x[1].sharpe,
        reverse=True,
    )
    for i, (name, r) in enumerate(ranking, 1):
        print(f"  {i}. {name}: Sharpe={r.sharpe:.3f}  vol={r.volatility:.1%}")

    print("\nAvertissement : ce n'est PAS un conseil financier.")


if __name__ == "__main__":
    main()
