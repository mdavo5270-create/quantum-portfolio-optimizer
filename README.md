# Quantum Portfolio Optimizer

**Moteur d'optimisation de portefeuille financier inspiré des principes de calcul quantique** (quantum-inspired).

Cet outil tourne entièrement sur du matériel classique. Il aide à explorer des allocations de portefeuille à partir d'actifs financiers (actions, cryptos, etc.) et de contraintes (budget, tolérance au risque, **cardinalité**), en comparant Markowitz, le recuit simulé et le QAOA simulé.

> **Avertissement important**  
> Cet outil est **expérimental** et purement pédagogique / de recherche.  
> **Ce n'est PAS un conseil financier.** Les résultats sont des simulations basées sur des données historiques. Ils ne constituent en aucun cas une recommandation d'investissement. Vous êtes seul responsable de vos décisions financières.

## État d'avancement

- [x] Phase 0 — Mise en place du projet
- [x] Phase 1 — Baseline classique (Markowitz)
- [x] Phase 2 — Moteur quantum-inspired v1 (recuit simulé)
- [x] Phase 3 — Backtesting
- [x] Phase 4 — QAOA simulé + cardinalité (univers large)
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
> Après `pip install -e .`, le package est enregistré.  
> Les scripts `examples/` ajoutent aussi la racine au `PYTHONPATH` automatiquement.

## Utilisation rapide

```bash
pytest -v -m "not network"

python examples/demo_markowitz.py
python examples/demo_compare_sa_markowitz.py
python examples/demo_backtest.py
python examples/demo_cardinality_qaoa.py   # ~25 actifs, K=5, Markowitz vs SA vs QAOA
```

## Documentation

- Markowitz : [`docs/methode_classique_markowitz.md`](docs/methode_classique_markowitz.md)
- Recuit simulé : [`docs/methode_recuit_simule.md`](docs/methode_recuit_simule.md)
- QAOA + cardinalité : [`docs/methode_qaoa.md`](docs/methode_qaoa.md)

## Licence

MIT — voir `LICENSE`.
