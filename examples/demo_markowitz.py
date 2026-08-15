"""Démonstration de l'optimiseur Markowitz classique.

Utilise 4 grandes actions technologiques sur quelques années d'historique.

Exécution (depuis la racine du projet, environnement activé) :
    python examples/demo_markowitz.py

Avertissement : ce n'est PAS un conseil financier. Résultats de simulation uniquement.
"""

from __future__ import annotations

from src.data.market_data import prepare_data
from src.classical_baseline.markowitz import optimize_from_returns


def main() -> None:
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    print("Téléchargement des données (peut prendre quelques secondes)...")
    prices, returns = prepare_data(tickers, start="2019-01-01")
    print(f"Période : {returns.index[0].date()} → {returns.index[-1].date()}")
    print(f"Nombre de jours de rendement : {len(returns)}")
    print()

    print("=== Optimisation Max Sharpe (long-only) ===")
    result = optimize_from_returns(returns, method="max_sharpe")
    print(f"Succès optimisation : {result.success}")
    print("Poids optimaux :")
    for asset, w in result.weights.items():
        print(f"  {asset}: {w:.1%}")
    print(f"Rendement annualisé attendu : {result.expected_return:.1%}")
    print(f"Volatilité annualisée       : {result.volatility:.1%}")
    print(f"Ratio de Sharpe (rf=0)      : {result.sharpe:.2f}")
    print()

    print("=== Optimisation Min Volatilité ===")
    result_min = optimize_from_returns(returns, method="min_vol")
    print("Poids optimaux :")
    for asset, w in result_min.weights.items():
        print(f"  {asset}: {w:.1%}")
    print(f"Volatilité annualisée : {result_min.volatility:.1%}")
    print()
    print("Avertissement : ce n'est PAS un conseil financier.")


if __name__ == "__main__":
    main()
