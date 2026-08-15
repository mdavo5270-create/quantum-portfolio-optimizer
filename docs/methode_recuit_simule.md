# Le recuit simulé — explication simple

## En une phrase

Le **recuit simulé** est une méthode d’optimisation inspirée de la physique : on « chauffe » le système puis on le refroidit progressivement pour qu’il se stabilise dans une bonne configuration (ici : de bons poids de portefeuille).

## L’analogie physique

En métallurgie, on chauffe un métal puis on le laisse refroidir lentement. Les atomes s’organisent alors dans une structure plus ordonnée et plus stable.  
Le recuit *simulé* reprend cette idée en informatique :

1. On part d’une solution quelconque (par exemple des poids égaux).
2. On propose de petits changements aléatoires.
3. Si le changement **améliore** le résultat → on l’accepte.
4. Si le changement **empire** le résultat → on peut quand même l’accepter *parfois*, surtout quand la « température » est élevée. Cela permet d’échapper aux pièges (optima locaux).
5. On baisse progressivement la température : à la fin, on n’accepte presque plus que les améliorations.

## Pourquoi « quantum-inspired » ?

Ce n’est **pas** un vrai calcul quantique.  
C’est une méthode **classique** dont le comportement (exploration / exploitation, transitions d’énergie) rappelle certains principes de la physique statistique et des algorithmes quantiques d’optimisation. D’où le label « quantum-inspired » : inspiré, pas quantique au sens matériel.

## Ce que fait notre version

- **Objectif** : maximiser le ratio de Sharpe **ou** minimiser la volatilité (comme Markowitz).
- **Contraintes** : poids positifs uniquement, somme = 100 %.
- **Exploration** : à chaque pas, on perturbe un peu les poids (bruit ou transfert entre deux actifs), puis on renormalise.
- **Décision** : règle de Metropolis (acceptation probabiliste des pires solutions au début).

## Comparaison avec Markowitz

| | Markowitz | Recuit simulé |
|---|---|---|
| Type | Optimisation mathématique exacte (ou quasi) | Recherche stochastique |
| Garantie | Optimum global sous hypothèses (si le problème est convexe) | Pas de garantie, mais souvent très proche |
| Points forts | Rapide, déterministe, bien compris | Peut explorer des paysages plus « accidentés » |
| Points faibles | Sensible aux estimations de covariance ; hypothèses fortes | Dépend des hyperparamètres (température, nombre de pas) |

Sur un problème mean-variance classique avec peu d’actifs, Markowitz est en général excellent. Le recuit simulé sert surtout de **première brique quantum-inspired** et de base de comparaison pour des méthodes plus avancées (QAOA simulé, etc.).

## Limites à garder en tête

- Résultats légèrement variables d’une exécution à l’autre (aléa contrôlé par une graine).
- Qualité liée au nombre de pas et au schéma de refroidissement.
- Comme Markowitz : basé sur le passé, pas de magie prédictive.
- **Ce n’est pas un conseil financier.**

## Comment le tester dans le projet

```bash
python examples/demo_compare_sa_markowitz.py
```

Vous verrez côte à côte les poids et les métriques des deux méthodes sur les mêmes données.
