# Quantum Portfolio Optimizer

**Banc d'essai** d'optimisation de portefeuille : Markowitz (classique) face au recuit simulé et au QAOA simulé — y compris quand l'approche « quantum-inspired » sous-performe.

Tourne entièrement sur matériel classique. **Ce n'est pas un conseil financier.**

## État d'avancement

- [x] Phase 0 — Mise en place
- [x] Phase 1 — Baseline Markowitz
- [x] Phase 2 — Recuit simulé
- [x] Phase 3 — Backtesting
- [x] Phase 4 — QAOA + cardinalité + investigation honnête
- [x] Phase 5 — Interface Streamlit (design papier)
- [ ] Phase 6 — Finalisation documentation / packaging

## Installation

```bash
git clone https://github.com/mdavo5270-create/quantum-portfolio-optimizer.git
cd quantum-portfolio-optimizer
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

## Interface utilisateur

```bash
streamlit run app/streamlit_app.py
```

Parcours : **Protocole** → **Verdict** (axe CLASSICAL → EXPERIMENTAL) → **Réplication** (backtest).

Design : fond papier, typo Fraunces + IBM Plex Sans, disclaimer permanent.  
Maquette Figma : [QPO UI Design — Phase 5](https://www.figma.com/design/iJbaCAXxY0BWQqWSi9gEAt)

## Scripts de démo (CLI)

```bash
pytest -v -m "not network"
python examples/demo_markowitz.py
python examples/demo_compare_sa_markowitz.py
python examples/demo_backtest.py
python examples/demo_cardinality_qaoa.py
```

## Documentation

- Markowitz : [`docs/methode_classique_markowitz.md`](docs/methode_classique_markowitz.md)
- Recuit simulé : [`docs/methode_recuit_simule.md`](docs/methode_recuit_simule.md)
- QAOA + limites : [`docs/methode_qaoa.md`](docs/methode_qaoa.md)
- Design UI : [`docs/ui_design_phase5.md`](docs/ui_design_phase5.md)

## Licence

MIT — voir `LICENSE`.
