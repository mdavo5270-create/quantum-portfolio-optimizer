"""Ajoute la racine du projet au PYTHONPATH.

Usage dans un script examples/ :

    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    # ou :
    import runpy
    runpy.run_path(str(Path(__file__).resolve().parent / "_bootstrap.py"))

Recommandé en plus : pip install -e . (voir README).
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
