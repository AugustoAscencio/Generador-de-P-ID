#!/usr/bin/env python3
"""build_sheets.py — Ensambla el proyecto FV 588 módulos (JSON multi-folio).

Cada hoja D-0XX se define en ``src/qetgen/sheets/fv588/`` con trazabilidad
documental. Este script las serializa a ``examples/proyecto_fv_588.json``
para pasar por el generador, que produce el .qet editable.

Uso:
    python tools/build_sheets.py
    qetgen build examples/proyecto_fv_588.json -o output/Proyecto_FV_588_Modulos.qet
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from qetgen.core.io import save_spec  # noqa: E402
from qetgen.sheets.fv588 import build_project  # noqa: E402
from qetgen.sheets.fv588.registry import ESTRUCTURA_18  # noqa: E402


def main() -> int:
    project = build_project()
    out = BASE / "examples" / "proyecto_fv_588.json"
    save_spec(project, out)

    print(f"OK  {out} — {len(project.folios)} planos")
    for (code, _name), folio in zip(ESTRUCTURA_18, project.folios):
        print(f"    {code}  {len(folio.elements):>3} elementos, "
              f"{len(folio.connections):>3} conexiones, "
              f"{len(folio.texts):>3} textos, "
              f"{len(folio.shapes):>3} bloques")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
