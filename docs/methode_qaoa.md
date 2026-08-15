# QAOA simulé et contrainte de cardinalité — explication simple

## Pourquoi une contrainte de cardinalité ?

Dans la vraie vie, un gérant ne met pas 1 % dans 30 actions. Il choisit souvent **un petit nombre** d’actifs (par exemple 5 à 10) parmi un univers large.

Mathématiquement : « choisir au plus K actifs parmi N, puis les pondérer » est un problème **combinatoire**. Markowitz « pur » (continu) ne gère pas cette contrainte discrète nativement.

## Les trois méthodes comparées

### 1. Markowitz + cardinalité (baseline classique)
Optimisation continue, projection top-K, plus tirage de sous-ensembles aléatoires de taille K.

### 2. Recuit simulé + cardinalité
Explore à la fois quels actifs garder et quels poids leur donner.

### 3. QAOA simulé
Traduction en QUBO (variables 0/1), circuit variationnel simulé en local, puis Markowitz sur le sous-ensemble retenu.

---

## Investigation : pourquoi le QAOA sous-performe ?

Sur la démo réelle (~25 actifs, K=5), le classement observé était du type :

| Méthode | Sharpe (ordre de grandeur) |
|--------|----------------------------|
| Markowitz + cardinalité | ~1.37 |
| Recuit simulé + cardinalité | ~1.37 |
| QAOA simulé | ~0.96 |

Des expériences contrôlées (données synthétiques, N=12, K=4, optimum exact par force brute) ont été menées pour séparer **limitation structurelle** et **problème de calibration**.

### Résultat 1 — Le QUBO est un mauvais proxy du Sharpe

Le QAOA n’optimise **pas** le ratio de Sharpe directement. Il minimise une énergie QUBO du type :

> variance (équipondérée) − rendement moyen, + pénalité de cardinalité

Sur C(12,4)=495 sous-ensembles :

- Corrélation de Spearman entre **énergie QUBO** et **vrai Sharpe Markowitz** ≈ **−0.36** seulement (idéalement proche de −1).
- Le sous-ensemble de **meilleure énergie QUBO** a un Sharpe ≈ 0.99 alors que l’optimum exact est ≈ 1.03 (écart déjà non négligeable).
- Des sous-ensembles très proches en énergie QUBO ont des Sharpe très différents (0.75 à 1.00).

**Conclusion structurelle :** même un solveur QUBO *parfait* ne garantit pas le meilleur Sharpe, parce que le modèle mathématique (QUBO) ne représente pas fidèlement l’objectif financier réel (Sharpe avec poids optimaux).

### Résultat 2 — La calibration variationnelle est instable

En mode statevector (simulation exacte du circuit, N=12) :

| Profondeur p | Comportement observé |
|--------------|----------------------|
| p=1 | Souvent loin de l’optimum |
| p=2 | Variable selon la graine |
| p=4 | Très sensible à la graine (Sharpe de ~0.42 à ~0.99 selon seed) |
| p=6 | *Peut* atteindre l’optimum exact sur certaines graines, pas toutes |

Augmenter p (4 ou 6) **n’améliore pas de façon fiable** la moyenne : l’espace des paramètres (γ, β) devient plus accidenté, et l’optimiseur classique (COBYLA) tombe dans des minima locaux.

**Conclusion calibration :** une partie de la sous-performance vient d’une optimisation variationnelle difficile (paysage non convexe, dépendance à l’initialisation), pas seulement de la profondeur trop faible.

### Résultat 3 — Mode sampling (N > 16)

Pour N≈25, on ne peut plus stocker 2^N amplitudes. Le mode « sampling » est une **heuristique inspirée** du QAOA, pas une simulation unitaire exacte. Augmenter le nombre d’échantillons (128 → 2048) stabilise un peu les résultats mais **ne comble pas** l’écart structurel lié au QUBO.

### Résultat 4 — Markowitz / SA restent plus adaptés ici

Sur le même jeu synthétique N=12 K=4, Markowitz+cardinalité et le recuit simulé retrouvent l’optimum exact (Sharpe ≈ 1.03). Ils travaillent **directement** sur le Sharpe (ou une énergie équivalente avec vrais poids), sans passer par un proxy QUBO faible.

---

## Conclusion honnête (Phase 4)

1. **Le sous-performance du QAOA sur ce problème n’est pas un « bug » isolé** : elle a des causes identifiées et reproductibles.
2. **Cause principale (structurelle) :** le QUBO mean-variance équipondéré + pénalité est un proxy **médiocrement corrélé** au vrai objectif (Sharpe après Markowitz sur le sous-ensemble).
3. **Cause secondaire (calibration) :** l’optimisation des angles QAOA est instable ; p plus grand n’est pas une solution magique et peut même empirer la variance entre exécutions.
4. **Sur ce cas d’usage (sélection d’actifs + Sharpe),** le recuit simulé et l’heuristique Markowitz+cardinalité sont **plus efficaces et plus robustes** que le QAOA simulé tel qu’implémenté.
5. Cela **ne « réfute » pas** le QAOA en général : sur d’autres QUBO bien formulés (MaxCut, etc.) il peut être pertinent. Ici, le goulot d’étranglement est surtout la **traduction finance → QUBO**, pas uniquement le simulateur.

Améliorations techniques testées (multi-start des angles, sélection par énergie QUBO parmi les bitstrings probables, plus d’échantillons) : utiles pour la robustesse, **insuffisantes** pour égaler SA/Markowitz tant que le proxy reste faible.

---

## Limites rappelées

- Simulation classique uniquement (pas de hardware quantique).
- Résultats sensibles aux hyperparamètres (p, pénalité, graine).
- **Ce n’est pas un conseil financier.**

## Lancer la comparaison

```bash
python examples/demo_cardinality_qaoa.py
```
