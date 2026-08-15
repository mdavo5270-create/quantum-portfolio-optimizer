# La méthode classique de Markowitz — explication simple

## En une phrase

Harry Markowitz (années 1950) a proposé de choisir les poids d’un portefeuille en cherchant le **meilleur compromis entre rendement espéré et risque** (mesuré par la volatilité).

## L’idée de base

Imagine que tu as plusieurs actions. Chacune a :
- un **rendement moyen** historique (combien elle a rapporté en moyenne),
- une **volatilité** (à quel point son prix monte et descend),
- des **corrélations** avec les autres (est-ce qu’elles bougent ensemble ?).

Markowitz dit : au lieu de mettre tout sur l’action qui a le plus gros rendement moyen, on regarde **l’ensemble**. En mélangeant des actifs qui ne bougent pas parfaitement ensemble, on peut **réduire le risque total** du portefeuille sans forcément sacrifier tout le rendement.

C’est l’idée de la **diversification** formalisée mathématiquement.

## Ce que fait notre optimiseur

Deux modes principaux :

1. **Maximise le ratio de Sharpe**  
   On cherche les poids qui donnent le meilleur « rendement par unité de risque ».  
   C’est souvent le portefeuille le plus « efficace » selon cette métrique.

2. **Minimise la volatilité** (portefeuille de variance minimale)  
   On cherche simplement le mélange le moins risqué possible (avec des poids positifs qui somment à 100 %).  
   On peut aussi imposer un rendement minimum souhaité.

**Contraintes utilisées** :
- Tous les poids ≥ 0 (on n’autorise pas la vente à découvert dans cette version).
- La somme des poids = 1 (on investit 100 % du capital).

## Comment ça se calcule (sans les formules)

1. On télécharge l’historique des prix.
2. On calcule les rendements journaliers.
3. On estime le rendement moyen de chaque actif et la matrice de covariance (qui capture les volatilités et les corrélations).
4. Un algorithme d’optimisation numérique (SLSQP) cherche les poids qui maximisent (ou minimisent) l’objectif tout en respectant les contraintes.

## Limites importantes (à connaître)

- On se base sur le **passé**. Le futur peut être très différent.
- Les estimations de covariance sont bruitées, surtout avec peu d’historique ou beaucoup d’actifs.
- Pas de coûts de transaction, pas d’impôts, pas de liquidité réelle.
- Ce n’est **pas un conseil financier**. C’est un outil de simulation et d’apprentissage.

## Lien avec le reste du projet

Cette méthode classique sert de **référence**. Toutes les approches « quantum-inspired » (recuit simulé, etc.) seront comparées à elle sur les mêmes données et les mêmes contraintes. Si une méthode plus exotique n’apporte rien de mieux, on le verra clairement.
