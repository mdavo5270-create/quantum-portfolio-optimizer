# Changelog

Tous les changements notables de ce projet sont documentés dans ce fichier.

Le format est inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [Unreleased]

## [0.4.0] - 2026-08-15

### Ajouté
- Moteur de backtesting walk-forward (`src/backtest/engine.py`)
- Métriques : rendement total / annualisé, volatilité, Sharpe, max drawdown
- Graphiques comparatifs (`src/visualization/backtest_plots.py`)
- Démo sur 3 périodes historiques : `examples/demo_backtest.py`
- `pyproject.toml` + `pip install -e .` pour résoudre les imports `src`
- Bootstrap `sys.path` dans chaque script `examples/` (lancement direct possible)

### Corrigé
- `ModuleNotFoundError: No module named 'src'` lors de `python examples/xxx.py`

## [0.3.0] - 2026-08-15

### Ajouté
- Module `src/optimizer/simulated_annealing.py` : recuit simulé (max Sharpe / min vol)
- Fonction `compare_with_markowitz` pour comparaison automatique
- Tests unitaires du moteur SA + compétitivité vs Markowitz
- Documentation simple : `docs/methode_recuit_simule.md`
- Démo comparative : `examples/demo_compare_sa_markowitz.py`

## [0.2.1] - 2026-08-15

### Corrigé / Amélioré
- `market_data.py` : téléchargement séquentiel, retry, cache local, FetchReport

## [0.2.0] - 2026-08-15

### Ajouté
- Données yfinance, Markowitz, tests, docs méthode classique

## [0.1.0] - 2026-08-15

### Ajouté
- Mise en place du dépôt, structure, CI, hello_world
