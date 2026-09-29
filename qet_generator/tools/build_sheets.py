#!/usr/bin/env python3
"""build_sheets.py — Ensambla el proyecto FV 588 módulos (JSON multi-folio).

Cada hoja D-0XX se define en generator/builders.py con trazabilidad documental.
Este script las serializa a examples/proyecto_fv_588.json para pasar por el
generador (main.py), que produce el .qet editable en QElectroTech.

Uso:
    python tools/build_sheets.py            # escribe el JSON del proyecto
    python main.py examples/proyecto_fv_588.json -o output/Proyecto_FV_588_Modulos.qet
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from generator.sheets import build_all  # noqa: E402
from generator.builders import folio_to_dict  # noqa: E402

# Registro de hojas del proyecto (estructura objetivo de 18 planos):
ESTRUCTURA_18 = [
    "D-001 Arquitectura del sistema / índice",
    "D-002 Diagrama general del módulo tipo",
    "D-003 String fotovoltaico 8 paneles",
    "D-004 Protección DC (QF-DC + SPD)",
    "D-005 Alimentación 24 VDC",
    "D-006 Eje de elevación",
    "D-007 Eje de azimut",
    "D-008 Sensores y entradas",
    "D-009 Sistema de viento / STOW",
    "D-010 Mapa de E/S",
    "D-011 Diagrama de estados",
    "D-012 Seguridad y enclavamientos",
    "D-013 Comunicaciones RS485/IoT",
    "D-014 Puesta a tierra TT",
    "D-015 Canalizaciones",
    "D-016 Borneras",
    "D-017 Interfaz con planta",
    "D-018 Módulo tipo × 588",
]


def main() -> int:
    folios = build_all()
    data = {
        "project": {
            "title": "PROYECTO FV 588 MÓDULOS — SEGUEIDOR BIAXIAL 8×650 Wp",
            "author": "Documentación eléctrica (Generador QET)",
            "filename": "Proyecto_FV_588_Modulos.qet",
        },
        "diagrams": [folio_to_dict(f) for f in folios],
    }
    out = BASE / "examples" / "proyecto_fv_588.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK  {out} — {len(folios)} planos")
    for f in folios:
        print(f"    {f.title}: {len(f.elements)} elementos, "
              f"{len(f.connections)} conexiones, {len(f.texts)} textos, "
              f"{len(f.shapes)} bloques")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
