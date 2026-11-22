"""Interfaz de línea de comandos.

Un único punto de entrada (``qetgen``) con subcomandos explícitos, códigos
de salida documentados y salida JSON opcional (para integraciones y para
que el servidor MCP reutilice exactamente la misma lógica).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .. import __version__
from ..core.catalog import SymbolCatalog, default_catalog_path
from ..core.errors import CatalogError, QetGenError, SpecError
from ..core.io import load_spec, save_spec
from ..core.sheet import SHEET_FORMATS
from ..exporters.json import export_json
from ..exporters.qet import export_qet
from ..validation.structural import validate_project

EXIT_OK = 0
EXIT_VALIDATION = 1
EXIT_INPUT = 2
EXIT_IO = 3


def _print(text: str = "") -> None:
    print(text)


def _err(text: str) -> None:
    print(text, file=sys.stderr)


def _catalog(args) -> SymbolCatalog:
    catalog_path = Path(args.catalog) if args.catalog else default_catalog_path()
    library = args.library
    if library is None:
        config = getattr(args, "config", None)
        if config:
            from ..config import load_config
            try:
                library = load_config(config).sources.library_path
            except QetGenError:
                library = None
    return SymbolCatalog(catalog_path, library)


# --------------------------------------------------------------------------
# Subcomandos
# --------------------------------------------------------------------------

def cmd_build(args) -> int:
    """Genera un proyecto .qet desde un JSON de especificación."""
    try:
        project = load_spec(args.input)
    except SpecError as exc:
        _err(f"ERROR leyendo el JSON: {exc}")
        return EXIT_INPUT
    try:
        catalog = _catalog(args)
    except CatalogError as exc:
        _err(f"ERROR con el catálogo de símbolos: {exc}")
        return EXIT_INPUT

    report = validate_project(project, catalog)
    if report.errors:
        _err("VALIDACIÓN FALLIDA — no se genera el proyecto:")
        for issue in report.errors:
            _err(f"  - {issue}")
        return EXIT_VALIDATION
    for issue in report.warnings:
        _err(f"  aviso: {issue}")

    output = Path(args.output) if args.output else (
        Path("output") / f"{Path(args.input).stem}.qet")
    try:
        output, results = export_qet(project, catalog, output)
    except OSError as exc:
        _err(f"ERROR escribiendo {output}: {exc}")
        return EXIT_IO

    n_el = sum(r.element_count for r in results)
    n_cn = sum(r.conductor_count for r in results)
    n_tx = sum(r.text_count for r in results)
    _print(f"OK  Proyecto generado: {output}")
    _print(f"    Título:        {project.title}")
    _print(f"    Folios:        {len(results)}")
    _print(f"    Elementos:     {n_el}")
    _print(f"    Conductores:   {n_cn}")
    _print(f"    Textos:        {n_tx}")
    _print(f"    Tamaño:        {output.stat().st_size:,} bytes")
    _print(f"    Ábrelo con:    QElectroTech → Archivo → Abrir")
    return EXIT_OK


def cmd_validate(args) -> int:
    """Valida un JSON (estructura + avisos) sin generar nada."""
    try:
        project = load_spec(args.input)
        catalog = _catalog(args)
    except (SpecError, CatalogError) as exc:
        _err(f"ERROR: {exc}")
        return EXIT_INPUT

    report = validate_project(project, catalog)
    if args.json:
        _print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
    else:
        _print(f"Proyecto: {project.title}")
        _print(f"Folios:   {len(project.folios)}")
        for issue in report.errors:
            _print(f"  ERROR   {issue}")
        for issue in report.warnings:
            _print(f"  AVISO   {issue}")
        _print(report.summary())
    return EXIT_OK if report.ok else EXIT_VALIDATION


def cmd_export(args) -> int:
    """Exporta un JSON a otro formato (json canónico o .qet)."""
    try:
        project = load_spec(args.input)
        catalog = _catalog(args)
    except (SpecError, CatalogError) as exc:
        _err(f"ERROR: {exc}")
        return EXIT_INPUT
    report = validate_project(project, catalog)
    if report.errors and not args.force:
        _err("VALIDACIÓN FALLIDA — usa --force para exportar de todos modos:")
        for issue in report.errors:
            _err(f"  - {issue}")
        return EXIT_VALIDATION

    output = Path(args.output)
    if args.format == "json":
        export_json(project, output)
    else:
        export_qet(project, catalog, output)
    _print(f"OK  Exportado: {output}")
    return EXIT_OK


def cmd_symbols(args) -> int:
    """Lista el catálogo de símbolos disponibles."""
    try:
        catalog = _catalog(args)
    except CatalogError as exc:
        _err(f"ERROR: {exc}")
        return EXIT_INPUT
    rows = []
    for entry in catalog.entries():
        symbol = catalog.get(entry["type"])
        rows.append({
            "type": entry["type"],
            "description": entry["description"],
            "prefix": entry["prefix"],
            "terminals": symbol.terminal_count,
            "size": f"{symbol.width:.0f}×{symbol.height:.0f}",
            "bounds": list(symbol.bounds.as_tuple()),
        })
    if args.json:
        _print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        _print(f"{'TIPO':<22}{'TER':>4}  {'TAMAÑO':>10}  DESCRIPCIÓN")
        for row in rows:
            _print(f"{row['type']:<22}{row['terminals']:>4}  {row['size']:>10}  "
                   f"{row['description']}")
    return EXIT_OK


def cmd_sheets(args) -> int:
    """Lista los formatos de hoja disponibles."""
    if args.json:
        _print(json.dumps({k: v.to_dict() for k, v in SHEET_FORMATS.items()},
                          ensure_ascii=False, indent=2))
        return EXIT_OK
    _print(f"{'NOMBRE':<12}{'COLS×ROWS':>12}{'ANCHO':>8}{'ALTO':>8}  ZONA SEGURA")
    for name, fmt in SHEET_FORMATS.items():
        safe = fmt.safe_area
        _print(f"{name:<12}{f'{fmt.cols}×{fmt.rows}':>12}{fmt.width:>8.0f}"
               f"{fmt.usable_height:>8.0f}  "
               f"({safe.x1:.0f},{safe.y1:.0f})-({safe.x2:.0f},{safe.y2:.0f})")
    return EXIT_OK


def cmd_fv588(args) -> int:
    """Regenera el paquete completo de 18 planos del caso FV 588."""
    from ..sheets.fv588 import build_project

    project = build_project()
    output_json = Path(args.output) if args.output else Path(
        "examples/proyecto_fv_588.json")
    save_spec(project, output_json)
    _print(f"OK  JSON: {output_json} — {len(project.folios)} planos")
    try:
        catalog = _catalog(args)
    except CatalogError as exc:
        _err(f"ERROR con el catálogo de símbolos: {exc}")
        return EXIT_INPUT
    report = validate_project(project, catalog)
    if report.errors:
        _err("VALIDACIÓN FALLIDA:")
        for issue in report.errors:
            _err(f"  - {issue}")
        return EXIT_VALIDATION
    output_qet = Path(args.qet) if args.qet else Path(
        "output/Proyecto_FV_588_Modulos.qet")
    export_qet(project, catalog, output_qet)
    _print(f"OK  QET:  {output_qet}")
    return EXIT_OK


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos de ``qetgen``."""
    parser = argparse.ArgumentParser(
        prog="qetgen",
        description=f"qetgen v{__version__} — generador de documentación "
                    f"eléctrica QElectroTech (.qet)")
    parser.add_argument("--version", action="version", version=f"qetgen {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p, catalog=True):
        p.add_argument("--catalog", help="Catálogo de símbolos (JSON)")
        p.add_argument("--library", help="Ruta de la biblioteca de elementos de QET")
        if catalog:
            p.add_argument("--config", help="Archivo de configuración (YAML/JSON)")
        return p

    p_build = sub.add_parser("build", help="Genera un .qet desde un JSON")
    p_build.add_argument("input", help="JSON de especificación")
    p_build.add_argument("-o", "--output", help="Ruta del .qet a generar")
    common(p_build)
    p_build.set_defaults(func=cmd_build)

    p_val = sub.add_parser("validate", help="Valida un JSON sin generar")
    p_val.add_argument("input", help="JSON de especificación")
    p_val.add_argument("--json", action="store_true", help="Salida en JSON")
    common(p_val)
    p_val.set_defaults(func=cmd_validate)

    p_exp = sub.add_parser("export", help="Exporta un JSON a otro formato")
    p_exp.add_argument("input", help="JSON de especificación")
    p_exp.add_argument("-f", "--format", choices=["qet", "json"], default="qet")
    p_exp.add_argument("-o", "--output", required=True, help="Archivo de salida")
    p_exp.add_argument("--force", action="store_true",
                       help="Exporta aunque haya errores de validación")
    common(p_exp)
    p_exp.set_defaults(func=cmd_export)

    p_sym = sub.add_parser("symbols", help="Lista el catálogo de símbolos")
    p_sym.add_argument("--json", action="store_true", help="Salida en JSON")
    common(p_sym)
    p_sym.set_defaults(func=cmd_symbols)

    p_sh = sub.add_parser("sheets", help="Lista los formatos de hoja")
    p_sh.add_argument("--json", action="store_true", help="Salida en JSON")
    p_sh.set_defaults(func=cmd_sheets)

    p_fv = sub.add_parser("fv588", help="Regenera el paquete FV 588 (18 planos)")
    p_fv.add_argument("-o", "--output", help="JSON de salida")
    p_fv.add_argument("--qet", help="Ruta del .qet de salida")
    common(p_fv)
    p_fv.set_defaults(func=cmd_fv588)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de la CLI. Devuelve el código de salida."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except QetGenError as exc:
        _err(f"ERROR: {exc}")
        return EXIT_INPUT
    except FileNotFoundError as exc:
        _err(f"ERROR: {exc}")
        return EXIT_INPUT
    except KeyboardInterrupt:      # pragma: no cover
        _err("Interrumpido.")
        return 130


__all__ = ["build_parser", "main"]
