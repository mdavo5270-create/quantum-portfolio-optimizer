"""Ajoute la racine du projet au PYTHONPATH.

Permet de lancer n'importe quel script avec :
    python examples/xxx.py
sans ModuleNotFoundError: No module named 'src'.

Alternative recommandée (une fois pour toutes) :
    pip install -e .
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
