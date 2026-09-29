#!/usr/bin/env python3
"""main.py — Generador de proyectos QElectroTech (.qet) desde JSON.

Uso:
    python main.py examples/basic_circuit.json
    python main.py examples/basic_circuit.json -o output/mi_proyecto.qet

Flujo:  JSON -> validación -> XML (formato QET 0.100.0) -> .qet
Basado en evidencia real: docs/QET_FORMAT_NOTES.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from generator import __version__                       # noqa: E402
from generator import project as project_mod            # noqa: E402
from generator.elements import SymbolCatalog            # noqa: E402
from generator.model import SpecError, load_spec       # noqa: E402
from generator.validate import validate_spec           # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=f"Generador de proyectos QElectroTech v{__version__}")
    parser.add_argument("input", help="Archivo JSON de entrada (especificación)")
    parser.add_argument("-o", "--output",
                        help="Ruta del .qet a generar "
                             "(por defecto: output/<nombre>.qet)")
    parser.add_argument("--catalog",
                        default=str(BASE_DIR / "templates" / "symbol_catalog.json"),
                        help="Catálogo de símbolos (JSON)")
    parser.add_argument("--library",
                        help="Ruta de la colección de elementos de QET "
                             "(por defecto: instalación estándar)")
    args = parser.parse_args(argv)

    # 1) Leer modelo
    try:
        spec = load_spec(args.input)
    except SpecError as e:
        print(f"ERROR leyendo el JSON: {e}", file=sys.stderr)
        return 2

    # 2) Catálogo de símbolos reales
    try:
        catalog = SymbolCatalog(args.catalog, args.library)
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"ERROR con el catálogo de símbolos: {e}", file=sys.stderr)
        return 2

    # 3) Validar ANTES de generar
    errors = validate_spec(spec, catalog)
    if errors:
        print("VALIDACIÓN FALLIDA — no se genera el proyecto:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    # 4) Generar
    root, results = project_mod.build_project(spec, catalog)

    output = Path(args.output) if args.output else (
        BASE_DIR / "output" / f"{Path(args.input).stem}.qet")
    try:
        project_mod.export_project(root, output)
    except OSError as e:
        print(f"ERROR escribiendo {output}: {e}", file=sys.stderr)
        return 3

    # 5) Resumen
    size = output.stat().st_size
    n_el = sum(r.element_count for r in results)
    n_cn = sum(r.conductor_count for r in results)
    n_tx = sum(r.text_count for r in results)
    print(f"OK  Proyecto generado: {output}")
    print(f"    Título:        {spec.title}")
    print(f"    Folios:        {len(results)}")
    print(f"    Elementos:     {n_el}")
    print(f"    Conductores:   {n_cn}")
    print(f"    Textos:        {n_tx}")
    print(f"    Tamaño:        {size:,} bytes")
    print(f"    Ábrelo con:    QElectroTech -> Archivo -> Abrir")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
