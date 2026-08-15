# Phase 5 — Design UI

**Figma :** [QPO UI Design — Phase 5](https://www.figma.com/design/iJbaCAXxY0BWQqWSi9gEAt)

## Direction retenue

- Fond **papier** `#F3EDE3`, encre `#1C1917` — rapport de banc d'essai, pas dashboard SaaS.
- Accents : **Classique** `#1F4D3A`, **Recuit** `#9A6B2F`, **Avertissement** `#7A2E2E`.
- Typo cible : **Fraunces** (titres) + **IBM Plex Sans** (corps/données).
- Layout vertical type protocole → verdict → preuves → réplication.

## Axe de verdict (mix A+B)

- Continuum CLASSICAL → EXPERIMENTAL.
- Rang 1/2/3 dans le label.
- Formes a11y : ■ Markowitz · ◆ SA · ○ QAOA (+ textures de trait).

### Cas serré (Sharpe quasi égaux)

Règle d'implémentation :
1. Position idéale = f(Sharpe) ; si écart centres < 28px → écarter en préservant l'ordre.
2. Labels alternés dessus / dessous + tick sur l'axe.
3. Rang toujours affiché dans le label.

## Écrans

1. **Protocole** — conditions de l'expérience
2. **Verdict** — axe + preuves (QAOA sous-perf. visible)
3. **Réplication** — backtest multi-fenêtres

Disclaimer permanent (bandeau brique, pas footer gris).
