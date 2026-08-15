# Changelog

Tous les changements notables de ce projet sont documentés dans ce fichier.

Le format est inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [Unreleased]

## [0.2.0] - 2026-08-15

### Ajouté
- Module `src/data/market_data.py` : téléchargement de prix via yfinance + calcul de rendements (log / simple)
- Module `src/classical_baseline/markowitz.py` : optimiseur Markowitz (max Sharpe et min volatilité, long-only)
- Tests unitaires déterministes avec données synthétiques (3-4 actifs)
- Documentation simple non technique : `docs/methode_classique_markowitz.md`
- Dépendances : numpy, pandas, scipy, yfinance

### Notes
- Les tests de téléchargement réel yfinance sont marqués `@pytest.mark.network` et ne bloquent pas la CI.

## [0.1.0] - 2026-08-15

### Ajouté
- Création du dépôt GitHub public avec licence MIT
- Structure de dossiers initiale (src/, tests/, docs/, notebooks/)
- README.md avec description du projet et avertissement non-conseil financier
- .gitignore, .env.example, requirements.txt
- Script hello_world pour valider l'environnement Python
- Pipeline GitHub Actions de base (pytest)
- Fichier docs/TODO.md (todo liste maîtresse)
