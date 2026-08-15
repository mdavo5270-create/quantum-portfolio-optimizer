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
- [ ] Phase 3 — Backtesting
- [ ] Phase 4 — QAOA simulé (si pertinent)
- [ ] Phase 5 — Interface utilisateur simple
- [ ] Phase 6 — Documentation finale et packaging

Voir `docs/TODO.md` pour le détail des tâches et `CHANGELOG.md` pour l'historique des versions.

## Installation

```bash
git clone https://github.com/mdavo5270-create/quantum-portfolio-optimizer.git
cd quantum-portfolio-optimizer
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation rapide

### Vérifier l'environnement
```bash
python -m src.hello_world
```

### Lancer les tests
```bash
pytest -v -m "not network"
```

### Démonstration Markowitz
```bash
python examples/demo_markowitz.py
```

### Comparaison Markowitz vs recuit simulé
```bash
python examples/demo_compare_sa_markowitz.py
```
Affiche côte à côte les poids et métriques des deux méthodes sur AAPL, MSFT, GOOGL, AMZN.

## Structure du projet

```
quantum-portfolio-optimizer/
├── examples/
│   ├── demo_markowitz.py
│   └── demo_compare_sa_markowitz.py
├── src/
│   ├── data/               # yfinance + rendements
│   ├── classical_baseline/ # Markowitz
│   ├── optimizer/          # recuit simulé (quantum-inspired)
│   ├── backtest/
│   └── visualization/
├── tests/
└── docs/
    ├── methode_classique_markowitz.md
    └── methode_recuit_simule.md
```

## Documentation

- Markowitz : [`docs/methode_classique_markowitz.md`](docs/methode_classique_markowitz.md)
- Recuit simulé : [`docs/methode_recuit_simule.md`](docs/methode_recuit_simule.md)

## Licence

MIT — voir le fichier `LICENSE`.

## Contribution

Projet en développement actif. Les tests automatiques (GitHub Actions) doivent passer avant toute fusion.
