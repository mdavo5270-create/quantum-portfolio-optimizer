# Changelog

Tous les changements notables de ce projet sont documentés dans ce fichier.

## [Unreleased]

## [0.5.0] - 2026-08-15

### Ajouté
- Contrainte de cardinalité (au plus K actifs) : Markowitz heuristique + SA
- QAOA simulé pour la sélection d'actifs (`src/optimizer/qaoa_portfolio.py`)
- Démo univers ~25 actifs, K=5 : `examples/demo_cardinality_qaoa.py`
- Documentation : `docs/methode_qaoa.md`
- Tests unitaires cardinalité + QAOA

## [0.4.0] - 2026-08-15

### Ajouté
- Backtesting walk-forward, métriques, graphiques, démo 3 périodes
- `pyproject.toml` + fix imports `src`

## [0.3.0] - 2026-08-15

### Ajouté
- Recuit simulé + comparaison Markowitz

## [0.2.1] / [0.2.0] / [0.1.0] - 2026-08-15

- Données yfinance robustes, Markowitz, mise en place projet
