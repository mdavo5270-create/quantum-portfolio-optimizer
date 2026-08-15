# Quantum Portfolio Optimizer

**Moteur d'optimisation de portefeuille financier inspiré des principes de calcul quantique** (quantum-inspired).

Cet outil tourne entièrement sur du matériel classique. Il aide à explorer des allocations de portefeuille à partir d'actifs financiers (actions, cryptos, etc.) et de contraintes (budget, tolérance au risque), en comparant une approche classique (Markowitz) à des méthodes inspirées du quantique (recuit simulé, éventuellement QAOA simulé).

> **Avertissement important**  
> Cet outil est **expérimental** et purement pédagogique / de recherche.  
> **Ce n'est PAS un conseil financier.** Les résultats sont des simulations basées sur des données historiques. Ils ne constituent en aucun cas une recommandation d'investissement. Vous êtes seul responsable de vos décisions financières.

## État d'avancement

- [x] Phase 0 — Mise en place du projet
- [ ] Phase 1 — Baseline classique (Markowitz)
- [ ] Phase 2 — Moteur quantum-inspired v1 (recuit simulé)
- [ ] Phase 3 — Backtesting
- [ ] Phase 4 — QAOA simulé (si pertinent)
- [ ] Phase 5 — Interface utilisateur simple
- [ ] Phase 6 — Documentation finale et packaging

Voir `docs/TODO.md` pour le détail des tâches et `CHANGELOG.md` pour l'historique des versions.

## Installation (préparation)

```bash
git clone https://github.com/mdavo5270-create/quantum-portfolio-optimizer.git
cd quantum-portfolio-optimizer
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation rapide (Phase 0)

```bash
python -m src.hello_world
```

Cela doit afficher un message de confirmation que l'environnement fonctionne.

## Structure du projet

```
quantum-portfolio-optimizer/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .env.example
├── .gitignore
├── requirements.txt
├── src/
│   ├── data/
│   ├── optimizer/
│   ├── classical_baseline/
│   ├── backtest/
│   └── visualization/
├── tests/
├── notebooks/
└── docs/
```

## Licence

MIT — voir le fichier `LICENSE`.

## Contribution

Projet en développement actif. Les commits et les branches de feature sont utilisés. Les tests automatiques (GitHub Actions) doivent passer avant toute fusion.
