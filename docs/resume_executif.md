# Résumé exécutif — Quantum Portfolio Optimizer (v1.0.0)

## Objet

Outil **expérimental et pédagogique** d’aide à la décision : comparer, sur données historiques, une allocation de portefeuille **classique (Markowitz)** à des méthodes **inspirées du quantique** (recuit simulé, QAOA simulé), **sans ordre réel** et **sans conseil financier**.

## Livrable

Dépôt public MIT : [quantum-portfolio-optimizer](https://github.com/mdavo5270-create/quantum-portfolio-optimizer)

Installation et usage documentés (README multi-OS + [guide utilisateur](guide_utilisateur.md)). Interface Streamlit (Protocole → Verdict → Réplication) et scripts de démonstration en ligne de commande. **28 tests automatisés** hors réseau ; CI GitHub Actions.

## Périmètre fonctionnel

| Capacité | Statut |
|----------|--------|
| Données de marché (Yahoo, retry, cache) | Livré |
| Markowitz (baseline) | Livré |
| Recuit simulé + comparaison | Livré |
| Contrainte de cardinalité (ex. max 5 titres sur ~25) | Livré |
| QAOA simulé (local, sans hardware quantique) | Livré |
| Backtest walk-forward (Sharpe, vol, drawdown) | Livré |
| Interface utilisateur soignée | Livré |
| Doc méthode + limites assumées | Livré |

## Résultat clé (Phase 4)

Sur le problème réaliste « **peu d’actifs parmi beaucoup** », le **QAOA simulé sous-performe** souvent face à Markowitz et au recuit simulé (ordre de grandeur Sharpe ~0,96 vs ~1,37).

- **Cause principale** : le modèle QUBO représente mal l’objectif financier réel (ratio de Sharpe après pondération optimale).
- **Cause secondaire** : calibration variationnelle instable.
- Augmenter la profondeur du circuit ne suffit pas.

Ce résultat est **affiché dans l’interface**, pas dissimulé — positionnement du projet : banc d’essai rigoureux, pas démonstration marketing du « quantique ».

## Ce que le projet n’est pas

- Pas un robot de trading
- Pas un conseil d’investissement
- Pas un accès à un ordinateur quantique réel
- Pas une garantie de surperformance des méthodes « quantum-inspired »

## Recommandation d’usage

Utiliser l’outil pour **explorer et comparer** des méthodes sur historique ; s’appuyer en priorité sur **Markowitz et le recuit simulé** pour ce cas d’usage ; traiter le QAOA comme **référence expérimentale** dont les limites sont connues.

## Statut

**Complet et validé en 1.0.0** (reproductibilité confirmée depuis un clone frais, y compris sous Windows).

Présentation Gamma (sans emojis) : https://gamma.app/generations/DtPPhVsWi3ooSAHRvqHFg
