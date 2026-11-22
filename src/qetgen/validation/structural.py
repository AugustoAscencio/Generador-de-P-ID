"""Validación estructural del modelo (reglas de dominio).

Separa dos conceptos que antes estaban mezclados:

* **Esquema** (tipos, campos obligatorios, rangos obvios) → lo garantiza
  Pydantic en :mod:`qetgen.core.models`.
* **Reglas de dominio** (unicidad de identificadores, coherencia de
  conexiones, fechas, límites de folio) → se evalúan aquí y se reportan
  como **diagnósticos accionables**, no como excepciones.

Un error bloquea la exportación. Un aviso no: informa y deja decidir al
usuario o a la IA.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field

from ..core.catalog import SymbolCatalog
from ..core.models import KNOWN_INFO_KEYS, Project
from ..core.sheet import get_sheet_format

#: Rango de tamaño de fuente admitido por proyecto (pt).
MIN_FONT_SIZE = 5
MAX_FONT_SIZE = 24


@dataclass
class ValidationReport:
    """Resultado de una validación completa."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """``True`` si no hay errores (los avisos no bloquean)."""
        return not self.errors

    def summary(self) -> str:
        """Resumen de una línea para la CLI y el servidor MCP."""
        if self.ok and not self.warnings:
            return "Sin errores ni avisos."
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(es)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} aviso(s)")
        return ", ".join(parts) + "."

    def as_dict(self) -> dict:
        """Representación serializable (CLI JSON / MCP)."""
        return {
            "ok": self.ok,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "summary": self.summary(),
        }


def _folio_name(folio) -> str:
    return folio.title or f"folio {folio.order}"


def validate_spec(spec: Project, catalog: SymbolCatalog) -> list[str]:
    """Errores que **bloquean** la exportación.

    Se mantiene la firma y los mensajes de la v0.1 para no romper el código
    existente; :func:`validate_project` amplía el análisis.
    """
    report = validate_project(spec, catalog)
    return report.errors


def validate_project(project: Project, catalog: SymbolCatalog) -> ValidationReport:
    """Validación completa: errores bloqueantes + avisos informativos."""
    report = ValidationReport()
    global_ids: set[str] = set()
    by_folio: list[dict] = []

    # ------------------------------------------------------------------
    # Elementos
    # ------------------------------------------------------------------
    for folio in project.folios:
        by_id: dict = {}
        for i, element in enumerate(folio.elements):
            ctx = (f"folio '{_folio_name(folio)}' elements[{i}] "
                   f"(id={element.id!r})")
            if not element.id:
                report.errors.append(f"{ctx}: id vacío")
                continue
            if element.id in global_ids:
                report.errors.append(f"ID duplicado en el proyecto: {element.id!r}")
            global_ids.add(element.id)
            by_id[element.id] = element

            if not catalog.has(element.type):
                report.errors.append(
                    f"{ctx}: tipo no registrado en el catálogo: {element.type!r}")
                continue
            symbol = catalog.get(element.type)
            if element.orientation not in (0, 1, 2, 3):
                report.errors.append(
                    f"{ctx}: orientation debe ser 0-3, llegó {element.orientation}")
            if element.x < 0 or element.y < 0:
                report.errors.append(
                    f"{ctx}: posición negativa ({element.x}, {element.y})")
            for key in element.info:
                if key not in KNOWN_INFO_KEYS:
                    report.errors.append(
                        f"{ctx}: clave de info no reconocida: {key!r} "
                        f"(válidas: {', '.join(sorted(KNOWN_INFO_KEYS))})")
            if not symbol.terminals and any(
                    cn.from_id == element.id or cn.to_id == element.id
                    for cn in folio.connections):
                report.errors.append(
                    f"{ctx}: el símbolo no tiene terminales conectables")
        by_folio.append(by_id)

    # ------------------------------------------------------------------
    # Conexiones
    # ------------------------------------------------------------------
    for folio, by_id in zip(project.folios, by_folio):
        seen_links: set[tuple] = set()
        terminal_use: dict[tuple[str, int], int] = {}
        for i, connection in enumerate(folio.connections):
            ctx = f"folio '{_folio_name(folio)}' connections[{i}] {connection.key()}"
            if connection.from_id not in by_id:
                report.errors.append(
                    f"{ctx}: 'from' hace referencia a un elemento inexistente "
                    f"en este folio")
                continue
            if connection.to_id not in by_id:
                report.errors.append(
                    f"{ctx}: 'to' hace referencia a un elemento inexistente "
                    f"en este folio")
                continue
            if connection.from_id == connection.to_id:
                report.errors.append(
                    f"{ctx}: un conductor no puede conectar un elemento consigo mismo")
            src, dst = by_id[connection.from_id], by_id[connection.to_id]
            for end, element, tname in (
                    (connection.from_terminal, src, "from_terminal"),
                    (connection.to_terminal, dst, "to_terminal")):
                if catalog.has(element.type):
                    count = len(catalog.get(element.type).terminals)
                    if not (0 <= end < count):
                        report.errors.append(
                            f"{ctx}: {tname}={end} fuera de rango "
                            f"({element.type!r} tiene {count} terminales: "
                            f"0..{count - 1})")

            link = (connection.from_id, connection.from_terminal,
                    connection.to_id, connection.to_terminal)
            if link in seen_links:
                report.warnings.append(
                    f"{ctx}: conexión duplicada (mismo par de terminales)")
            seen_links.add(link)
            for key in ((connection.from_id, connection.from_terminal),
                        (connection.to_id, connection.to_terminal)):
                terminal_use[key] = terminal_use.get(key, 0) + 1

        for (element_id, terminal), count in sorted(terminal_use.items()):
            if count > 1:
                report.warnings.append(
                    f"folio '{_folio_name(folio)}': la terminal "
                    f"{element_id}[{terminal}] se usa en {count} conductores")

    # ------------------------------------------------------------------
    # Textos
    # ------------------------------------------------------------------
    for folio in project.folios:
        for i, text in enumerate(folio.texts):
            if not str(text.text).strip():
                report.errors.append(
                    f"folio '{_folio_name(folio)}' texts[{i}]: texto vacío")
            if not (MIN_FONT_SIZE <= text.size <= MAX_FONT_SIZE):
                report.errors.append(
                    f"folio '{_folio_name(folio)}' texts[{i}]: size debe estar "
                    f"entre {MIN_FONT_SIZE} y {MAX_FONT_SIZE} pt, llegó {text.size}")

    # ------------------------------------------------------------------
    # Bloques (shapes)
    # ------------------------------------------------------------------
    for folio in project.folios:
        fmt = get_sheet_format(folio.sheet_format)
        for i, shape in enumerate(folio.shapes):
            ctx = f"folio '{_folio_name(folio)}' shapes[{i}]"
            if shape.x2 <= shape.x1 or shape.y2 <= shape.y1:
                report.errors.append(
                    f"{ctx}: coordenadas invertidas "
                    f"({shape.x1},{shape.y1})-({shape.x2},{shape.y2})")
            if (shape.x1 < 0 or shape.y1 < 0
                    or shape.x2 > fmt.width or shape.y2 > fmt.height):
                report.errors.append(
                    f"{ctx}: fuera del área del folio "
                    f"{int(fmt.width)}×{int(fmt.height)}")
            if not (0.5 <= shape.width <= 10):
                report.errors.append(
                    f"{ctx}: width de línea irrazonable: {shape.width}")

    # ------------------------------------------------------------------
    # Folios
    # ------------------------------------------------------------------
    orders = [f.order if f.order is not None else i + 1
              for i, f in enumerate(project.folios)]
    if len(orders) != len(set(orders)):
        report.errors.append(f"orders de folio duplicados: {sorted(orders)}")
    if orders != list(range(1, len(orders) + 1)):
        report.warnings.append(
            f"los orders de folio no son contiguos 1..N: {orders}")
    for folio in project.folios:
        if folio.date is not None:
            if not (len(folio.date) == 8 and folio.date.isdigit()):
                report.errors.append(
                    f"folio '{_folio_name(folio)}': date debe ser AAAAMMDD, "
                    f"llegó: {folio.date!r}")
            else:
                try:
                    _dt.datetime.strptime(folio.date, "%Y%m%d")
                except ValueError:
                    report.errors.append(
                        f"folio '{_folio_name(folio)}': date no es una fecha "
                        f"real: {folio.date!r}")

    return report


__all__ = [
    "MAX_FONT_SIZE",
    "MIN_FONT_SIZE",
    "ValidationReport",
    "validate_project",
    "validate_spec",
]
