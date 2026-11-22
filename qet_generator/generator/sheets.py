"""sheets — Fachada de compatibilidad (deprecated → ``qetgen.sheets.fv588``).

> **Deprecated:** los 18 planos viven ahora en
> ``src/qetgen/sheets/fv588/sheets.py``. Esta fachada re-exporta la API.
"""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.sheets.fv588.sheets import (build_all, build_d001, build_d004,
                                         build_d005, build_d006, build_d007,
                                         build_d008, build_d009, build_d010,
                                         build_d011, build_d012, build_d013,
                                         build_d014, build_d015, build_d016,
                                         build_d017, build_d018)

__all__ = [
    "build_all",
    "build_d001",
    "build_d004",
    "build_d005",
    "build_d006",
    "build_d007",
    "build_d008",
    "build_d009",
    "build_d010",
    "build_d011",
    "build_d012",
    "build_d013",
    "build_d014",
    "build_d015",
    "build_d016",
    "build_d017",
    "build_d018",
]
