# Changelog

Tous les changements notables de ce projet sont documentés dans ce fichier.

## [Unreleased]

## [0.5.1] - 2026-08-15

### Investigation QAOA
- Analyse de la sous-performance vs SA/Markowitz (données synthétiques + force brute)
- Causes : proxy QUBO faiblement corrélé au Sharpe (Spearman ≈ −0.36) + calibration variationnelle instable
- p=4/6 et plus d'échantillons n'égalent pas SA/Markowitz de façon fiable
- Multi-start des angles + sélection par énergie QUBO
- Conclusion documentée dans `docs/methode_qaoa.md`

## [0.5.0] - 2026-08-15

### Ajouté
- Cardinalité K, QAOA simulé, démo ~25 actifs, docs et tests

## [0.4.0] - 2026-08-15

### Ajouté
- Backtesting walk-forward, graphiques, fix imports

## [0.3.0] / [0.2.x] / [0.1.0] - 2026-08-15

- SA, Markowitz, données, mise en place
