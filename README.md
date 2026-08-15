# Quantum Portfolio Optimizer

**Moteur d'optimisation de portefeuille financier inspiré des principes de calcul quantique** (quantum-inspired).

Cet outil tourne entièrement sur du matériel classique. Il aide à explorer des allocations de portefeuille à partir d'actifs financiers (actions, cryptos, etc.) et de contraintes (budget, tolérance au risque), en comparant une approche classique (Markowitz) à des méthodes inspirées du quantique (recuit simulé, éventuellement QAOA simulé).

> **Avertissement important**  
> Cet outil est **expérimental** et purement pédagogique / de recherche.  
> **Ce n'est PAS un conseil financier.** Les résultats sont des simulations basées sur des données historiques. Ils ne constituent en aucun cas une recommandation d'investissement. Vous êtes seul responsable de vos décisions financières.

## État d'avancement

- [x] Phase 0 — Mise en place du projet
- [x] Phase 1 — Baseline classique (Markowitz)
- [x] Phase 2 — Moteur quantum-inspired v1 (recuit simulé)
- [x] Phase 3 — Backtesting
- [ ] Phase 4 — QAOA simulé (si pertinent)
- [ ] Phase 5 — Interface utilisateur simple
- [ ] Phase 6 — Documentation finale et packaging

## Installation

```bash
git clone https://github.com/mdavo5270-create/quantum-portfolio-optimizer.git
cd quantum-portfolio-optimizer
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

> **Important — imports `src`**  
> Après `pip install -e .`, le package est enregistré et les scripts fonctionnent.  
> Chaque script dans `examples/` ajoute aussi automatiquement la racine du projet au `PYTHONPATH`, donc `python examples/demo_xxx.py` fonctionne même sans install éditable.  
> En CI et en usage normal, préférez toujours `pip install -e .`.

## Utilisation rapide

```bash
# Environnement
python -m src.hello_world

# Tests
pytest -v -m "not network"

# Démos
python examples/demo_markowitz.py
python examples/demo_compare_sa_markowitz.py
python examples/demo_backtest.py          # 3 périodes + graphiques dans output/backtest/
```

## Structure

```
examples/          # scripts de démo (lancement direct OK)
src/
  data/            # yfinance + rendements
  classical_baseline/  # Markowitz
  optimizer/       # recuit simulé
  backtest/        # walk-forward + métriques
  visualization/   # graphiques
tests/
docs/
```

## Documentation

- Markowitz : [`docs/methode_classique_markowitz.md`](docs/methode_classique_markowitz.md)
- Recuit simulé : [`docs/methode_recuit_simule.md`](docs/methode_recuit_simule.md)

## Licence

MIT — voir `LICENSE`.
