# QAOA simulé et contrainte de cardinalité — explication simple

## Pourquoi une contrainte de cardinalité ?

Dans la vraie vie, un gérant ne met pas 1 % dans 30 actions. Il choisit souvent **un petit nombre** d’actifs (par exemple 5 à 10) parmi un univers large.

Mathématiquement : « choisir au plus K actifs parmi N, puis les pondérer » est un problème **combinatoire** (beaucoup de sous-ensembles possibles). Markowitz « pur » (continu) ne gère pas cette contrainte discrète nativement.

C’est précisément le type de problème où des méthodes stochastiques / quantum-inspired peuvent être intéressantes.

## Les trois méthodes comparées

### 1. Markowitz + cardinalité (baseline classique)
1. Optimisation continue classique.
2. On ne garde que les K plus gros poids (projection).
3. En plus : on tire au hasard de nombreux sous-ensembles de taille K, on optimise Markowitz sur chacun, on garde le meilleur.

### 2. Recuit simulé + cardinalité
Le SA explore à la fois **quels** actifs garder et **quels** poids leur donner (échanges d’actifs, repondérations). La contrainte K est appliquée à chaque candidat.

### 3. QAOA simulé
**QAOA** = Quantum Approximate Optimization Algorithm.

Idée (simplifiée) :
1. On traduit le choix d’actifs en un problème de type QUBO (variables 0/1 : inclus ou non).
2. Un « circuit » variationnel (couches de phases de coût + mélange) est simulé **sur un ordinateur classique**.
3. On lit la meilleure configuration binaire (les K actifs retenus).
4. On calcule ensuite les poids optimaux Markowitz **uniquement** sur ce sous-ensemble.

Ce n’est **pas** un vrai ordinateur quantique : tout tourne en local (simulation). Pour N ≤ 16 actifs on peut simuler l’état quantique complet ; au-delà on utilise un mode d’échantillonnage variationnel.

## Que faut-il attendre ?

- Sur un problème **sans** contrainte de cardinalité (4–5 actifs, tout pondéré), Markowitz et SA convergent souvent au même point.
- Avec **N ≈ 25** et **K = 5**, l’espace de recherche est vaste : les écarts de Sharpe entre méthodes peuvent apparaître.
- Un avantage « quantum-inspired » n’est **pas garanti** : l’objectif de cette phase est de **mesurer** honnêtement s’il y en a un sur ce problème plus difficile.

## Limites

- Simulation approximative du QAOA (surtout si N > 16).
- Le QUBO est un **proxy** du ratio de Sharpe, pas le Sharpe exact.
- Résultats sensibles aux hyperparamètres (profondeur p, pénalité, graine).
- **Ce n’est pas un conseil financier.**

## Lancer la comparaison

```bash
python examples/demo_cardinality_qaoa.py
```
