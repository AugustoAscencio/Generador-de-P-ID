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
    _print("    Ábrelo con:    QElectroTech → Archivo → Abrir")
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
# Motor de layout y diagnóstico del entorno
# --------------------------------------------------------------------------

def _load_config(args):
    """Carga la configuración central (YAML/JSON) o la de por defecto."""
    from ..config import default_config_path, load_config

    path = getattr(args, "config", None) or default_config_path()
    return load_config(path), path


def cmd_layout(args) -> int:
    """Ejecuta el motor de layout y audita la estética del proyecto.

    Por defecto **no escribe nada**: informa de lo que haría el motor
    (*simulación*). Con ``--apply`` persiste el JSON resultante.
    """
    from ..layout.pipeline import LayoutOptions, apply_layout
    from ..validation.aesthetics import validate_aesthetics

    try:
        project = load_spec(args.input)
        catalog = _catalog(args)
        config, config_path = _load_config(args)
    except (SpecError, CatalogError) as exc:
        _err(f"ERROR: {exc}")
        return EXIT_INPUT

    options = LayoutOptions(
        snap=args.snap,
        auto_layout=args.auto_layout,
        route=not args.no_route,
        snap_texts=args.snap_texts,
        respect_locked=not args.ignore_locked,
        folio=args.folio)

    if args.folio is not None and not 1 <= args.folio <= len(project.folios):
        _err(f"ERROR: el folio {args.folio} no existe "
             f"(el proyecto tiene {len(project.folios)} folio/s).")
        return EXIT_INPUT

    outcome = apply_layout(project, catalog, config, options)

    # -- auditoría estética --------------------------------------------------
    aesthetic = None
    if args.check:
        aesthetic = validate_aesthetics(outcome.project, catalog, config)

    # -- previsualización SVG ------------------------------------------------
    previews: list[str] = []
    if args.preview:
        try:
            from ..exporters.svg import export_sheet_svg
            previews = []
            for index, sheet in enumerate(outcome.project.folios, start=1):
                if args.folio is not None and index != args.folio:
                    continue
                path = Path(args.preview) / f"folio_{index:02d}.svg"
                export_sheet_svg(sheet, catalog, path)
                previews.append(str(path))
        except OSError as exc:
            _err(f"ERROR escribiendo la previsualización: {exc}")
            return EXIT_IO

    # -- persistencia --------------------------------------------------------
    saved = ""
    if args.apply:
        output = Path(args.output) if args.output else Path(
            "output") / f"{Path(args.input).stem}_layout.json"
        try:
            save_spec(outcome.project, output)
        except OSError as exc:
            _err(f"ERROR escribiendo {output}: {exc}")
            return EXIT_IO
        saved = str(output)

    # -- informe -------------------------------------------------------------
    if args.json:
        payload = outcome.as_dict()
        payload["config"] = str(config_path)
        payload["preview"] = previews
        payload["saved"] = saved
        if aesthetic is not None:
            payload["aesthetics"] = aesthetic.as_dict()
        _print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print(f"Proyecto: {project.title}")
        _print(f"Config:   {config_path}")
        _print(f"Rejilla:  {config.layout.grid_size:g} px "
               f"(snap {'activo' if config.layout.snap_to_grid else 'desactivado'})")
        _print("")
        for folio in outcome.folios:
            flags = []
            if folio.snapped:
                flags.append(f"{folio.snapped} alineado(s)")
            if folio.moved:
                flags.append(f"{len(folio.moved)} movido(s)")
            if folio.kept_locked:
                flags.append(f"{len(folio.kept_locked)} bloqueado(s)")
            if folio.routes:
                flags.append(f"{folio.routes_ok}/{len(folio.routes)} ruta(s) OK")
            _print(f"Folio {folio.folio:>2} — {folio.title[:40]:<42} "
                   f"{'; '.join(flags) if flags else 'sin cambios'}")
            for cid, old, new in folio.moved:
                _print(f"      movido  {cid:<12} ({old[0]:.0f},{old[1]:.0f}) → "
                       f"({new[0]:.0f},{new[1]:.0f})")
            for cid in folio.unresolved:
                _print(f"      SIN RESOLVER  {cid}: no se encontró hueco libre")
            for route in folio.routes:
                if not route.ok:
                    _print(f"      SIN RUTA  {route.key}: {route.message}")
        if outcome.locked_count:
            _print("")
            _print(f"Modo híbrido: {outcome.locked_count} elemento(s) con "
                   f"locked:true respetados (no se mueven).")
        if aesthetic is not None:
            _print("")
            _print(aesthetic.summary())
            for issue in aesthetic.errors:
                _print(f"  ERROR   [{issue.code}] {issue.folio}: {issue.message}")
                if issue.suggestion:
                    _print(f"          → {issue.suggestion}")
            for issue in aesthetic.warnings[:20]:
                _print(f"  aviso   [{issue.code}] {issue.folio}: {issue.message}")
            if len(aesthetic.warnings) > 20:
                _print(f"          … y {len(aesthetic.warnings) - 20} aviso(s) más")
        if previews:
            _print("")
            _print(f"Previsualización SVG: {len(previews)} archivo(s) en {args.preview}")
        if saved:
            _print("")
            _print(f"JSON guardado: {saved}")
        elif not args.check and not args.preview:
            _print("")
            _print("Nada se ha escrito (simulación). Usa --apply para guardar "
                   "el resultado.")

    if aesthetic is not None and aesthetic.errors:
        return EXIT_VALIDATION
    if outcome.unresolved or outcome.routes_failed:
        return EXIT_VALIDATION
    return EXIT_OK


def _doctor_check(name: str, ok: bool, detail: str, hint: str = "",
                  status: str | None = None) -> dict:
    """Construye un diagnóstico del entorno.

    ``status`` puede fijarse explícitamente (``ok``/``warn``/``error``); si no,
    se deduce de ``ok`` y de si hay consejo (``hint``).
    """
    if status is None:
        status = "ok" if ok else ("warn" if hint else "error")
    return {
        "check": name,
        "status": status,
        "detail": detail,
        "hint": hint,
    }


def cmd_doctor(args) -> int:
    """Diagnostica el entorno de trabajo (dependencias, QET, catálogo, config)."""
    from .. import __version__
    from ..config import default_config_path, load_config

    checks: list[dict] = []

    # -- Python --------------------------------------------------------------
    version_ok = sys.version_info >= (3, 10)
    checks.append(_doctor_check(
        "python", version_ok,
        f"Python {sys.version.split()[0]}",
        "qetgen requiere Python 3.10 o superior" if not version_ok else ""))

    # -- dependencias --------------------------------------------------------
    for module, required, hint in (
            ("pydantic", True, "pip install pydantic>=2.0"),
            ("yaml", True, "pip install PyYAML>=6.0"),
            ("mcp", False, "pip install 'qetgen[mcp]' para usar el servidor MCP")):
        try:
            mod = __import__(module)
            detail = f"{module} {getattr(mod, '__version__', '(sin versión)')}"
            checks.append(_doctor_check(module, True, detail))
        except ImportError:
            checks.append(_doctor_check(
                module, not required, f"{module} NO instalado",
                hint if required else hint,
                status="error" if required else "warn"))

    # -- configuración -------------------------------------------------------
    config_path = Path(args.config) if args.config else default_config_path()
    try:
        config = load_config(config_path)
        checks.append(_doctor_check(
            "config", True,
            f"{config_path} — {config.sheet.format}, rejilla "
            f"{config.layout.grid_size:g} px"))
    except (SpecError, OSError) as exc:
        config = None
        checks.append(_doctor_check("config", False, f"{config_path}: {exc}",
                                    "Revise config/default.yaml", status="error"))

    # -- biblioteca de QElectroTech -----------------------------------------
    library = args.library or (config.sources.library_path if config else None)
    if library:
        lib_path = Path(library)
        elmt_count = len(list(lib_path.rglob("*.elmt"))) if lib_path.is_dir() else 0
        checks.append(_doctor_check(
            "qet_library", lib_path.is_dir(),
            f"{lib_path} — {elmt_count} archivo(s) .elmt"
            if lib_path.is_dir() else f"{lib_path}: no existe",
            "" if lib_path.is_dir()
            else "Instala QElectroTech 0.100.0 o corrige sources.library_path",
            status="ok" if lib_path.is_dir() else "error"))

    # -- catálogo de símbolos ------------------------------------------------
    try:
        catalog = _catalog(args)
        entries = catalog.entries()
        missing = []
        for entry in entries:
            elmt = str(entry.get("elmt_path", "")).replace("\\", "/").strip("/")
            if not elmt or not (catalog.library / elmt).is_file():
                missing.append(entry["type"])
        checks.append(_doctor_check(
            "catalog", not missing,
            f"{len(entries)} símbolo(s) en el catálogo"
            + (f" — faltan {len(missing)} .elmt: {', '.join(missing[:5])}"
               if missing else ""),
            "Revise resources/symbol_catalog.json" if missing else ""))
    except (CatalogError, OSError) as exc:
        catalog = None
        checks.append(_doctor_check("catalog", False, str(exc),
                                    "Revise resources/symbol_catalog.json"))

    # -- proyecto opcional ---------------------------------------------------
    project_report = None
    if getattr(args, "input", None):
        try:
            project = load_spec(args.input)
            structural = validate_project(project, catalog) if catalog else None
            aesthetic = None
            if config is not None and catalog is not None:
                from ..validation.aesthetics import validate_aesthetics
                aesthetic = validate_aesthetics(project, catalog, config)
            project_report = {
                "file": str(args.input),
                "folios": len(project.folios),
                "structural_ok": structural.ok if structural else None,
                "structural_errors": [str(e) for e in structural.errors]
                if structural else [],
                "aesthetics": aesthetic.as_dict() if aesthetic else None,
            }
            ok = (structural is None or structural.ok) and \
                 (aesthetic is None or aesthetic.ok)
            checks.append(_doctor_check(
                "project", ok,
                f"{args.input}: {len(project.folios)} folio(s)"
                + (f" — {aesthetic.summary()}" if aesthetic else ""),
                "" if ok else "Revise los diagnósticos del proyecto",
                status="ok" if ok else "error"))
        except (SpecError, CatalogError) as exc:
            checks.append(_doctor_check("project", False, str(exc),
                                        "Revise el JSON de especificación"))

    # -- salida --------------------------------------------------------------
    errors = [c for c in checks if c["status"] == "error"]
    warns = [c for c in checks if c["status"] == "warn"]

    if args.json:
        _print(json.dumps({
            "version": __version__,
            "ok": not errors,
            "checks": checks,
            "project": project_report,
        }, ensure_ascii=False, indent=2))
    else:
        _print(f"qetgen v{__version__} — diagnóstico del entorno")
        _print("")
        for check in checks:
            icon = {"ok": "OK   ", "warn": "AVISO", "error": "ERROR"}[check["status"]]
            _print(f"  [{icon}] {check['check']:<14} {check['detail']}")
            if check["hint"]:
                _print(f"                    → {check['hint']}")
        _print("")
        if errors:
            _print(f"{len(errors)} problema(s) bloqueante(s).")
        elif warns:
            _print(f"Todo operativo ({len(warns)} aviso(s)).")
        else:
            _print("Todo operativo.")

    return EXIT_OK if not errors else EXIT_VALIDATION


def cmd_serve(args) -> int:
    """Arranca el servidor MCP por stdio."""
    from ..mcp_server.main import main as serve_main

    argv: list[str] = []
    if getattr(args, "config", None):
        argv += ["--config", args.config]
    if getattr(args, "catalog", None):
        argv += ["--catalog", args.catalog]
    if getattr(args, "library", None):
        argv += ["--library", args.library]
    if getattr(args, "fallback", False):
        argv.append("--fallback")
    return serve_main(argv)


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
    common(p_sh)
    p_sh.set_defaults(func=cmd_sheets)

    p_fv = sub.add_parser("fv588", help="Regenera el paquete FV 588 (18 planos)")
    p_fv.add_argument("-o", "--output", help="JSON de salida")
    p_fv.add_argument("--qet", help="Ruta del .qet de salida")
    common(p_fv)
    p_fv.set_defaults(func=cmd_fv588)

    p_lay = sub.add_parser(
        "layout", help="Motor de layout: snap, auto-layout, routing y auditoría")
    p_lay.add_argument("input", help="JSON de especificación")
    p_lay.add_argument("--snap", action="store_true",
                       help="Alinea a la rejilla lo que no esté bloqueado")
    p_lay.add_argument("--snap-texts", action="store_true",
                       help="Alinea también los textos a la rejilla")
    p_lay.add_argument("--auto-layout", action="store_true",
                       help="Reubica los componentes en columnas lógicas")
    p_lay.add_argument("--no-route", action="store_true",
                       help="No calcula las rutas Manhattan")
    p_lay.add_argument("--ignore-locked", action="store_true",
                       help="Ignora locked:true (desactiva el modo híbrido)")
    p_lay.add_argument("--folio", type=int, help="Opera solo sobre este folio (1..N)")
    p_lay.add_argument("--check", action="store_true",
                       help="Audita la estética y devuelve error si hay defectos")
    p_lay.add_argument("--preview", metavar="DIR",
                       help="Escribe un SVG de previsualización por folio")
    p_lay.add_argument("--apply", action="store_true",
                       help="Guarda el JSON resultante (por defecto es simulación)")
    p_lay.add_argument("-o", "--output", help="Ruta del JSON de salida (con --apply)")
    p_lay.add_argument("--json", action="store_true", help="Salida en JSON")
    common(p_lay)
    p_lay.set_defaults(func=cmd_layout)

    p_doc = sub.add_parser("doctor", help="Diagnostica el entorno de trabajo")
    p_doc.add_argument("input", nargs="?", help="Proyecto a comprobar (opcional)")
    p_doc.add_argument("--json", action="store_true", help="Salida en JSON")
    common(p_doc)
    p_doc.set_defaults(func=cmd_doctor)

    p_srv = sub.add_parser("serve", help="Arranca el servidor MCP (stdio)")
    p_srv.add_argument("--fallback", action="store_true",
                       help="Fuerza el servidor propio (sin el SDK oficial)")
    common(p_srv)
    p_srv.set_defaults(func=cmd_serve)

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
