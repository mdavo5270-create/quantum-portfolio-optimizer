# Quantum Portfolio Optimizer

Banc d’essai d’**optimisation de portefeuille** : méthode classique (Markowitz) face au **recuit simulé** et au **QAOA simulé**, y compris lorsque l’approche « quantum-inspired » sous-performe.

Tout tourne sur un ordinateur classique. **Ce n’est pas un conseil financier** et **aucun ordre réel** n’est passé.

## Démarrage rapide

```bash
git clone https://github.com/mdavo5270-create/quantum-portfolio-optimizer.git
cd quantum-portfolio-optimizer
python -m venv .venv
```

**Activer l’environnement virtuel (selon votre système) :**

```bash
# Linux / macOS
source .venv/bin/activate
```

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

```bat
# Windows (Invite de commandes cmd)
.venv\Scripts\activate.bat
```

Puis :

```bash
pip install -e .
pip install -r requirements.txt

# Interface (recommandé)
streamlit run app/streamlit_app.py

# Tests hors réseau
pytest -v -m "not network"
```

Guide pas à pas (sans jargon) : **[docs/guide_utilisateur.md](docs/guide_utilisateur.md)**  
Résumé exécutif : **[docs/resume_executif.md](docs/resume_executif.md)**

## Ce que fait l’outil

1. **Protocole** — vous choisissez des actifs, une limite du nombre de titres (cardinalité K), une période, les méthodes à comparer.
2. **Verdict** — classement et **axe CLASSICAL → EXPERIMENTAL** (avec gestion des scores quasi égaux).
3. **Réplication** — backtest walk-forward sur d’autres fenêtres historiques.

## Méthodes

| Méthode | Rôle |
|--------|------|
| Markowitz | Baseline classique mean-variance |
| Recuit simulé | Heuristique stochastique, adaptée à la cardinalité |
| QAOA simulé | Sélection binaire simulée ; **souvent inférieure ici** — [pourquoi](docs/methode_qaoa.md) |

## Structure du dépôt

```
app/streamlit_app.py     # Interface utilisateur
src/data/                # Données de marché (yfinance, cache, retry)
src/classical_baseline/  # Markowitz
src/optimizer/           # SA, cardinalité, QAOA
src/backtest/            # Walk-forward + métriques
examples/                # Démos en ligne de commande
tests/                   # pytest
docs/                    # Guides et notes de méthode
```

## Démos CLI

```bash
python examples/demo_markowitz.py
python examples/demo_compare_sa_markowitz.py
python examples/demo_backtest.py
python examples/demo_cardinality_qaoa.py
```

> Après `pip install -e .`, les imports `src` fonctionnent. Chaque script `examples/` ajoute aussi la racine au chemin Python.

## Documentation

| Document | Public |
|----------|--------|
| [Résumé exécutif](docs/resume_executif.md) | Décideurs |
| [Guide utilisateur](docs/guide_utilisateur.md) | Non technicien |
| [Markowitz](docs/methode_classique_markowitz.md) | Méthode |
| [Recuit simulé](docs/methode_recuit_simule.md) | Méthode |
| [QAOA + limites](docs/methode_qaoa.md) | Méthode + investigation |
| [Design UI](docs/ui_design_phase5.md) | Maquette |
| [CHANGELOG](CHANGELOG.md) | Historique des versions |

Maquette Figma : [QPO UI Design](https://www.figma.com/design/iJbaCAXxY0BWQqWSi9gEAt)

## État du projet

Phases 0 à 6 terminées (mise en place → baseline → SA → backtest → QAOA → interface → finalisation).

## Licence

MIT — voir [LICENSE](LICENSE).
