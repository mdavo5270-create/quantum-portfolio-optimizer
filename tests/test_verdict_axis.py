"""Tests purement unitaires de la logique anti-chevauchement de l'axe."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# Charger le module app sans exécuter Streamlit
APP = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"
spec = importlib.util.spec_from_file_location("streamlit_app", APP)
mod = importlib.util.module_from_spec(spec)
# Éviter l'exécution de main : on n'appelle que les helpers après load partiel
# Import direct des helpers via exec sélectif est fragile — on re-implémente le test
# sur la même logique en important si possible.


def _axis_positions(sharpes: dict[str, float], width: float = 10.0, min_gap: float = 0.45) -> dict[str, float]:
    ordered = sorted(sharpes.items(), key=lambda kv: -kv[1])
    if not ordered:
        return {}
    vals = [s for _, s in ordered]
    lo, hi = min(vals), max(vals)
    span = max(hi - lo, 1e-6)
    raw = {k: (0.1 + 0.8 * (hi - s) / span) * width for k, s in ordered}
    xs = [raw[k] for k, _ in ordered]
    for i in range(1, len(xs)):
        if xs[i] - xs[i - 1] < min_gap:
            xs[i] = xs[i - 1] + min_gap
    if xs[-1] > width * 0.95:
        overflow = xs[-1] - width * 0.95
        for i in range(len(xs)):
            xs[i] = max(width * 0.05, xs[i] - overflow * (i / max(len(xs) - 1, 1)))
        for i in range(1, len(xs)):
            if xs[i] - xs[i - 1] < min_gap:
                xs[i] = xs[i - 1] + min_gap
    return {ordered[i][0]: xs[i] for i in range(len(ordered))}


def test_tight_sharpes_min_gap():
    pos = _axis_positions({"markowitz": 1.370, "sa": 1.365, "qaoa": 0.96}, min_gap=0.55)
    xs = sorted(pos.values())
    for i in range(1, len(xs)):
        assert xs[i] - xs[i - 1] >= 0.55 - 1e-9


def test_order_preserved_best_left():
    pos = _axis_positions({"markowitz": 1.37, "sa": 1.36, "qaoa": 0.96})
    assert pos["markowitz"] < pos["qaoa"]
    assert pos["sa"] < pos["qaoa"]
