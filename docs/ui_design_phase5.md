# Phase 5 — Design UI (point de contrôle)

**Statut : en attente de validation visuelle avant implémentation Streamlit.**

## Wireframes Excalidraw

Parcours utilisateur en 3 écrans :

1. **Configuration** — sélection d’actifs, contraintes (K, dates, méthodes), bandeau disclaimer, CTA « Lancer l’optimisation »
2. **Résultats & comparaison** — classement Markowitz / SA / QAOA (y compris sous-performance QAOA visible), poids, note de rigueur
3. **Backtest** — périodes, courbes d’équité, métriques (Sharpe, MDD, vol), disclaimer

Navigation commune + disclaimer **toujours visible** (ambre/rouge, pas gris pale).

## Maquette Figma

Fichier : [QPO UI Design — Phase 5](https://www.figma.com/design/iJbaCAXxY0BWQqWSi9gEAt)

### Direction visuelle

| Token | Valeur | Intention |
|-------|--------|-----------|
| Fond | Navy `#0F172A` | Finance, sérieux |
| Cartes | `#1A243D` | Profondeur |
| Accent primaire | Cyan `#38BDF8` | Données, clarté |
| Accent secondaire | Violet `#8B5CF6` | « Quantum », modernité |
| Alerte / disclaimer | Ambre `#F59E0B` + rouge | Visibilité obligatoire |
| Typo | Inter | Professionnelle, lisible |

### Écrans maquettés

- Design system (swatches)
- Screen 1 — Configuration
- Screen 2 — Résultats & comparaison (QAOA classé 3e, note explicite)
- Screen 3 — Backtest

## Prochaine étape

Après validation de ta part : implémentation Streamlit fidèle à cette maquette (custom CSS, pas le thème par défaut seul).
