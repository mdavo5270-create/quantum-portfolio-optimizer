# Guide utilisateur — Quantum Portfolio Optimizer

Ce document s’adresse à quelqu’un qui veut **utiliser** l’outil sans lire le code.

## En une phrase

C’est un **banc d’essai** : vous choisissez des actions, des règles (par ex. « au plus 5 titres »), et l’outil compare plusieurs façons de composer un portefeuille **en simulation**. Il ne place aucun ordre réel.

> **Ce n’est pas un conseil financier.** Les chiffres viennent de l’historique de marché. Le passé ne prédit pas l’avenir.

## Installation (une fois)

1. Installez [Python 3.11+](https://www.python.org/downloads/).
2. Ouvrez un terminal et tapez :

```bash
git clone https://github.com/mdavo5270-create/quantum-portfolio-optimizer.git
cd quantum-portfolio-optimizer
python -m venv .venv
```

3. Activez l’environnement :
   - macOS / Linux : `source .venv/bin/activate`
   - Windows : `.venv\Scripts\activate`

4. Installez le projet :

```bash
pip install -e .
pip install -r requirements.txt
```

## Lancer l’interface (recommandé)

```bash
streamlit run app/streamlit_app.py
```

Une page s’ouvre dans le navigateur. Trois étapes :

### 1. Protocole
- Choisissez un **preset** d’actions (ou collez vos propres tickers, séparés par des virgules).
- Réglez **K** : nombre maximum d’actifs dans le portefeuille (ex. 5).
- Indiquez une **date de début** pour l’historique.
- Cochez les méthodes à comparer.
- Cliquez sur **Lancer le banc d’essai**.

Le premier lancement peut prendre une à deux minutes (téléchargement des cours).

### 2. Verdict
- Une phrase résume qui « gagne » sur **cette** expérience.
- L’**axe de verdict** place les méthodes de la plus « classique » à la plus « expérimentale » selon le résultat.
- Le tableau donne ratio de Sharpe, volatilité, rendement et titres retenus.
- Si le QAOA est derrière, c’est **affiché clairement** (ce n’est pas un bug : voir [methode_qaoa.md](methode_qaoa.md)).

### 3. Réplication
- Rejoue Markowitz et le recuit simulé sur d’autres périodes (walk-forward).
- Utile pour voir si un classement tient sur d’autres fenêtres historiques.

## Les trois méthodes, en langage simple

| Méthode | Idée |
|--------|------|
| **Markowitz** | Approche classique (années 1950) : équilibre rendement espéré / risque. |
| **Recuit simulé** | Exploration « à tâtons » inspirée du refroidissement des métaux ; utile avec la contrainte « peu d’actifs ». |
| **QAOA simulé** | Idée inspirée du quantique, simulée sur ordinateur classique. Sur ce problème précis, elle **sous-performe souvent** — c’est documenté. |

## Scripts en ligne de commande (optionnel)

Sans interface graphique :

```bash
python examples/demo_markowitz.py
python examples/demo_compare_sa_markowitz.py
python examples/demo_backtest.py
python examples/demo_cardinality_qaoa.py
```

## Vérifier que tout fonctionne

```bash
pytest -v -m "not network"
```

Les tests marqués `network` appellent Internet (Yahoo Finance) et peuvent échouer selon le réseau.

## Limites importantes

- Données gratuites (Yahoo) : parfois incomplètes ou ralenties.
- Aucune garantie de performance future.
- Aucun compte de courtage, aucun ordre.
- Outil **expérimental / pédagogique**.

## Aller plus loin

- [Méthode Markowitz](methode_classique_markowitz.md)
- [Recuit simulé](methode_recuit_simule.md)
- [QAOA et ses limites](methode_qaoa.md)
- [Design de l’interface](ui_design_phase5.md)
