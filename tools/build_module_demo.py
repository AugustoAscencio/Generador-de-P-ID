#!/usr/bin/env python3
"""build_module_demo.py — Genera examples/module_demo.json (MÓDULO TIPO × 2 folios).

Uso:
    python tools/build_module_demo.py [MODULO] [PANELES]
    python tools/build_module_demo.py M001 8
Luego:
    qetgen build examples/module_demo.json
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from qetgen.core.io import save_spec  # noqa: E402
from qetgen.core.models import Project  # noqa: E402
from qetgen.sheets.fv588.builders import build_module_folios  # noqa: E402


def main() -> int:
    module = sys.argv[1] if len(sys.argv) > 1 else "M001"
    panels = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    folios = build_module_folios(module=module, panel_count=panels)
    project = Project(
        title=f"Modulo FV tipo {module} - {panels} paneles",
        author="Generador QET",
        filename=f"module_{module}.qet",
        folios=folios,
    )
    out = BASE / "examples" / "module_demo.json"
    save_spec(project, out)

    total_el = sum(len(f.elements) for f in folios)
    total_cn = sum(len(f.connections) for f in folios)
    print(f"OK  {out}")
    print(f"    Modulo: {module} | folios: {len(folios)} | "
          f"elementos: {total_el} | conexiones: {total_cn}")
    print(f"    Siguiente: qetgen build {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
