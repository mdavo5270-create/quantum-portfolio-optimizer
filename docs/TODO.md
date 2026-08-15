# TODO — Quantum Portfolio Optimizer

## Phase 0 — Mise en place
- [x] Créer le dépôt GitHub public avec licence MIT
- [x] Structure de dossiers initiale
- [x] README.md initial (description, avertissement non-conseil-financier)
- [x] .gitignore, .env.example, requirements.txt
- [x] Script "hello world" qui tourne sans erreur + premier commit
- [x] GitHub Actions : pipeline de test automatique de base

## Phase 1 — Baseline classique
- [x] Module de récupération de données de marché (yfinance ou équivalent)
- [x] Nettoyage et mise en forme des données (pandas)
- [x] Implémentation de l'optimisation Markowitz classique
- [x] Test manuel de cohérence sur un petit exemple (3-4 actifs)
- [x] Documentation simple de la méthode classique dans docs/

## Phase 2 — Moteur quantum-inspired v1
- [x] Implémentation du recuit simulé pour l'allocation de portefeuille
- [x] Comparaison automatique avec la baseline classique
- [x] Documentation simple (langage non technique) de la méthode
- [x] Tests unitaires du module optimizer

## Phase 3 — Backtesting
- [x] Moteur de backtesting historique
- [x] Calcul des métriques (rendement, volatilité, Sharpe, drawdown)
- [x] Rapport visuel comparatif (graphiques)
- [x] Test sur au moins 3 périodes historiques différentes

## Phase 4 — QAOA simulé
- [x] Implémentation QAOA simulé
- [x] Comparaison à trois (classique / recuit simulé / QAOA)
- [x] Documentation de la méthode (limites incluses)
- [x] Univers large + contrainte de cardinalité K

## Phase 5 — Interface utilisateur
- [x] Interface Streamlit (design papier, axe de verdict)
- [x] Sélection d'actifs et contraintes sans toucher au code
- [x] Affichage clair des résultats et comparaisons

## Phase 6 — Finalisation
- [x] README complet et à jour
- [x] Documentation utilisateur complète dans docs/ (guide_utilisateur.md)
- [x] Nettoyage (imports, version 1.0.0, dépendances alignées)
- [x] Vérification de la reproductibilité depuis un clone frais
- [x] CHANGELOG.md à jour, résumant tout le projet
