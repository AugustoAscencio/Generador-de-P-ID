"""Bootstrap de la v0.1: hace visible el paquete canónico ``qetgen``.

La v1.0 vive en ``<repo>/src/qetgen``. Este módulo permite que el código
antiguo (``import generator.model``) siga funcionando **sin instalar nada**
añadiendo ``src`` al ``sys.path``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]      # raíz del repositorio
_SRC = _ROOT / "src"

if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

#: Raíz del repositorio (útil para resolver recursos por ruta relativa).
REPO_ROOT = _ROOT

__all__ = ["REPO_ROOT"]
