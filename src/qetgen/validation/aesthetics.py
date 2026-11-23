"""validation/aesthetics.py — Auditoría estética del plano.

Comprueba lo que la validación estructural **no** puede ver:

* ¿el contenido cabe en la zona segura y respeta el cajetín?,
* ¿hay símbolos que se pisan?,
* ¿los textos son legibles y no se solapan?,
* ¿el cableado está trazado de forma ortogonal y sin cruces?,
* ¿las etiquetas de los símbolos se montan sobre otro elemento?,

Cada diagnóstico lleva un **código estable**, la severidad, los objetos
implicados y una **sugerencia accionable**. Es la salida que consumen la CLI
(``qetgen layout --check``), el servidor MCP (``validar_estetica``) y las
herramientas de CI.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.catalog import SymbolCatalog
from ..core.models import Project, Sheet
from ..core.sheet import get_sheet_format
from ..layout.collision import (
    analyze_sheet,
    component_bounds,
    component_label_bounds,
    label_bounds,
    shape_bounds,
)
from ..layout.grid import Grid
from ..layout.router import route_sheet
from ..layout.textmetrics import TextMeasurer

#: Códigos de diagnóstico (estables: pueden usarse en CI y en el MCP).
CODE_OUT_OF_SHEET = "OUT_OF_SHEET"
CODE_OUT_OF_SAFE_AREA = "OUT_OF_SAFE_AREA"
CODE_IN_TITLEBLOCK = "IN_TITLEBLOCK"
CODE_SYMBOL_OVERLAP = "SYMBOL_OVERLAP"
CODE_TEXT_OVERLAP = "TEXT_OVERLAP"
CODE_LABEL_OVERLAP = "LABEL_OVERLAP"
CODE_TINY_TEXT = "TINY_TEXT"
CODE_TEXT_TOO_WIDE = "TEXT_TOO_WIDE"
CODE_UNROUTED = "UNROUTED_CONNECTION"
CODE_ROUTE_CROSSING = "ROUTE_CROSSING"
CODE_ROUTE_TOO_CLOSE = "ROUTE_TOO_CLOSE"
CODE_EMPTY_SHEET = "EMPTY_SHEET"
CODE_BLOCK_CROSSING = "BLOCK_CROSSING"


@dataclass(frozen=True)
class AestheticIssue:
    """Diagnóstico estético con contexto suficiente para actuar."""

    code: str
    severity: str            # "error" | "warning" | "info"
    folio: str
    message: str
    suggestion: str = ""
    objects: tuple[str, ...] = ()
    coordinates: tuple[float, float] | None = None

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "severity": self.severity,
            "folio": self.folio,
            "message": self.message,
            "suggestion": self.suggestion,
            "objects": list(self.objects),
            "coordinates": list(self.coordinates) if self.coordinates else None,
        }


@dataclass
class AestheticReport:
    """Resultado de la auditoría estética de un proyecto."""

    issues: list[AestheticIssue] = field(default_factory=list)
    sheets_analyzed: int = 0

    @property
    def errors(self) -> list[AestheticIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[AestheticIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def infos(self) -> list[AestheticIssue]:
        return [i for i in self.issues if i.severity == "info"]

    @property
    def ok(self) -> bool:
        """``True`` si no hay errores (los avisos no bloquean)."""
        return not self.errors

    def summary(self) -> str:
        """Resumen de una línea."""
        if not self.issues:
            return "Auditoría estética: sin incidencias."
        return (f"Auditoría estética: {len(self.errors)} error(es), "
                f"{len(self.warnings)} aviso(s), {len(self.infos)} info.")

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "summary": self.summary(),
            "sheets_analyzed": self.sheets_analyzed,
            "issues": [i.as_dict() for i in self.issues],
        }


def _folio_name(sheet: Sheet) -> str:
    return sheet.title or f"folio {sheet.order}"


def _segments_cross(a1, a2, b1, b2) -> bool:
    """¿Se cruzan dos segmentos ortogonales (sin contar el contacto)?"""
    a_horizontal = abs(a1[1] - a2[1]) < 1e-6
    b_horizontal = abs(b1[1] - b2[1]) < 1e-6
    if a_horizontal == b_horizontal:
        return False
    if a_horizontal:
        hx1, hx2 = sorted((a1[0], a2[0]))
        hy = a1[1]
        vx = b1[0]
        vy1, vy2 = sorted((b1[1], b2[1]))
        return (hx1 + 1e-6 < vx < hx2 - 1e-6) and (vy1 + 1e-6 < hy < vy2 - 1e-6)
    hx = a1[0]
    vy1, vy2 = sorted((a1[1], a2[1]))
    hx1, hx2 = sorted((b1[0], b2[0]))
    vy = b1[1]
    return (vy1 + 1e-6 < vy < vy2 - 1e-6) and (hx1 + 1e-6 < hx < hx2 - 1e-6)


def _segments_distance(a1, a2, b1, b2) -> float:
    """Distancia mínima entre dos segmentos paralelos (∞ si no son paralelos)."""
    a_horizontal = abs(a1[1] - a2[1]) < 1e-6
    b_horizontal = abs(b1[1] - b2[1]) < 1e-6
    if a_horizontal != b_horizontal:
        return float("inf")
    if a_horizontal:
        ax1, ax2 = sorted((a1[0], a2[0]))
        bx1, bx2 = sorted((b1[0], b2[0]))
        if ax2 < bx1 or bx2 < ax1:
            return float("inf")
        return abs(a1[1] - b1[1])
    ay1, ay2 = sorted((a1[1], a2[1]))
    by1, by2 = sorted((b1[1], b2[1]))
    if ay2 < by1 or by2 < ay1:
        return float("inf")
    return abs(a1[0] - b1[0])


def _check_sheet(sheet: Sheet, catalog: SymbolCatalog, measurer: TextMeasurer,
                 grid: Grid, report: AestheticReport, *,
                 margin: float, min_font_size: int, min_separation: float,
                 route_manhattan: bool, edge_tolerance: float = 36.0) -> None:
    """Audita un folio y añade sus diagnósticos al informe.

    ``edge_tolerance`` es la tolerancia de borde, **calibrada con evidencia**
    (``tools/measure_sheet_geometry.py``): de los 416 textos reales de los 22
    proyectos de QElectroTech 0.100.0, solo 10 (2,40 %) se saldrían del folio
    con nuestra métrica, y 9 de esos 10 lo hacen en 36 px o menos. Un desborde
    menor es un aviso; por encima de 36 px, es un error (el texto se sale del
    folio de verdad).
    """
    folio = _folio_name(sheet)
    fmt = get_sheet_format(sheet.sheet_format)
    drawing = fmt.drawing_area
    safe = drawing.inset(margin)
    band = fmt.titleblock_area

    # -- contenido -----------------------------------------------------------
    if not sheet.elements and not sheet.texts and not sheet.shapes:
        report.issues.append(AestheticIssue(
            code=CODE_EMPTY_SHEET, severity="info", folio=folio,
            message="el folio está vacío",
            suggestion="añade contenido o elimina el folio del proyecto"))
        return

    # -- símbolos ------------------------------------------------------------
    for component in sheet.elements:
        if not catalog.has(component.type):
            continue
        symbol = catalog.get(component.type)
        box = component_bounds(component, symbol)
        if not drawing.contains(box):
            report.issues.append(AestheticIssue(
                code=CODE_OUT_OF_SHEET, severity="error", folio=folio,
                message=(f"el símbolo {component.id} sale del área del folio "
                         f"({box.x1:.0f},{box.y1:.0f})-({box.x2:.0f},{box.y2:.0f}) "
                         f"frente a {drawing.as_tuple()}"),
                suggestion="mueve el símbolo hacia dentro del folio o reduce el tamaño de hoja",
                objects=(component.id,),
                coordinates=(component.x, component.y)))
        elif not safe.contains(box):
            report.issues.append(AestheticIssue(
                code=CODE_OUT_OF_SAFE_AREA, severity="warning", folio=folio,
                message=(f"el símbolo {component.id} invade el margen de "
                         f"seguridad ({margin:g} px)"),
                suggestion=f"acerca {component.id} al centro del folio (margen {margin:g} px)",
                objects=(component.id,),
                coordinates=(component.x, component.y)))
        if box.y1 >= band.y1 - 1e-6:
            report.issues.append(AestheticIssue(
                code=CODE_IN_TITLEBLOCK, severity="error", folio=folio,
                message=f"el símbolo {component.id} invade la banda del cajetín",
                suggestion="sube el símbolo: la banda inferior pertenece al cajetín de QET",
                objects=(component.id,),
                coordinates=(component.x, component.y)))

        label_text = component.resolved_label()
        if label_text:
            label_box = component_label_bounds(component, symbol, measurer)
            if not drawing.contains(label_box):
                report.issues.append(AestheticIssue(
                    code=CODE_OUT_OF_SHEET, severity="warning", folio=folio,
                    message=f"la etiqueta de {component.id} sobresale del folio",
                    suggestion=("cambia el prefijo del símbolo o acorta la "
                                "etiqueta para que quepa en la hoja"),
                    objects=(component.id,), coordinates=(component.x, component.y)))

    # -- textos --------------------------------------------------------------
    for index, text in enumerate(sheet.texts):
        box = label_bounds(text, measurer)
        if text.size < min_font_size:
            report.issues.append(AestheticIssue(
                code=CODE_TINY_TEXT, severity="warning", folio=folio,
                message=(f"texto[{index}] usa {text.size} pt, por debajo del "
                         f"mínimo legible ({min_font_size} pt)"),
                suggestion=f"aumenta el tamaño a {min_font_size} pt o más",
                objects=(f"texto[{index}]",), coordinates=(text.x, text.y)))
        if box.width > fmt.width + edge_tolerance:
            report.issues.append(AestheticIssue(
                code=CODE_TEXT_TOO_WIDE, severity="warning", folio=folio,
                message=(f"texto[{index}] mide {box.width:.0f} px de ancho, "
                         f"más que el folio ({fmt.width:g} px)"),
                suggestion="divide el texto en varias líneas o acórtalo",
                objects=(f"texto[{index}]",), coordinates=(text.x, text.y)))
        overflow_x = max(0.0, box.x2 - fmt.width)
        overflow_y = max(0.0, box.y2 - fmt.usable_height)
        overflow = max(overflow_x, overflow_y)
        if overflow > edge_tolerance:
            report.issues.append(AestheticIssue(
                code=CODE_OUT_OF_SHEET, severity="error", folio=folio,
                message=(f"texto[{index}] se sale del folio por {overflow:.0f} px "
                         f"(borde derecho en {fmt.width:g}, "
                         f"borde inferior en {fmt.usable_height:g})"),
                suggestion=("divide el texto en varias líneas, acórtalo o "
                            "mueve su ancla a la izquierda"),
                objects=(f"texto[{index}]",), coordinates=(text.x, text.y)))
        elif overflow > 0:
            report.issues.append(AestheticIssue(
                code=CODE_OUT_OF_SHEET, severity="warning", folio=folio,
                message=(f"texto[{index}] roza el borde del folio "
                         f"({overflow:.0f} px)"),
                suggestion="mueve el texto hacia dentro o acórtalo",
                objects=(f"texto[{index}]",), coordinates=(text.x, text.y)))
        elif not drawing.contains(box):
            report.issues.append(AestheticIssue(
                code=CODE_OUT_OF_SHEET, severity="error", folio=folio,
                message=f"texto[{index}] sale del área del folio",
                suggestion="mueve el texto hacia dentro del área de dibujo",
                objects=(f"texto[{index}]",), coordinates=(text.x, text.y)))
        elif not safe.contains(box):
            report.issues.append(AestheticIssue(
                code=CODE_OUT_OF_SAFE_AREA, severity="warning", folio=folio,
                message=f"texto[{index}] invade el margen de seguridad",
                suggestion="mueve el texto hacia el interior del folio",
                objects=(f"texto[{index}]",), coordinates=(text.x, text.y)))

    # -- bloques -------------------------------------------------------------
    for index, shape in enumerate(sheet.shapes):
        box = shape_bounds(shape)
        if not drawing.contains(box):
            report.issues.append(AestheticIssue(
                code=CODE_OUT_OF_SHEET, severity="error", folio=folio,
                message=f"bloque[{index}] sale del área del folio",
                suggestion="redimensiona o mueve el bloque dentro de la hoja",
                objects=(f"bloque[{index}]",),
                coordinates=(shape.x1, shape.y1)))

    # -- colisiones ----------------------------------------------------------
    collisions = analyze_sheet(sheet, catalog, measurer)
    for collision in collisions.collisions:
        if collision.kind.endswith("-shape"):
            code = CODE_BLOCK_CROSSING
        else:
            code = {
                "component-component": CODE_SYMBOL_OVERLAP,
                "component-label": CODE_LABEL_OVERLAP,
                "label-label": CODE_LABEL_OVERLAP,
                "text-text": CODE_TEXT_OVERLAP,
                "component-text": CODE_TEXT_OVERLAP,
                "label-text": CODE_TEXT_OVERLAP,
            }.get(collision.kind, CODE_TEXT_OVERLAP)
        severity = collision.severity
        report.issues.append(AestheticIssue(
            code=code, severity=severity, folio=folio,
            message=collision.message, suggestion=collision.suggestion,
            objects=(collision.a, collision.b),
            coordinates=(collision.box.x1, collision.box.y1)))

    # -- cableado ------------------------------------------------------------
    if sheet.connections:
        routed, results = route_sheet(
            sheet, catalog, grid, safe,
            min_separation=min_separation,
            route_manhattan=route_manhattan)
        for connection, result in zip(routed.connections, results, strict=True):
            if not result.ok:
                report.issues.append(AestheticIssue(
                    code=CODE_UNROUTED, severity="warning", folio=folio,
                    message=f"no se pudo trazar {connection.key()}: {result.message}",
                    suggestion=("reduce el número de elementos de la línea, "
                                "usa otra distribución o libera espacio"),
                    objects=(connection.from_id, connection.to_id)))
                continue
            if not result.waypoints:
                report.issues.append(AestheticIssue(
                    code=CODE_UNROUTED, severity="warning", folio=folio,
                    message=f"el conductor {connection.key()} no tiene ruta calculada",
                    suggestion="ejecuta el auto-layout o ajusta la posición de los símbolos",
                    objects=(connection.from_id, connection.to_id)))

        # Cruces y paralelos entre rutas del mismo folio.
        segments: list[tuple[str, tuple, tuple]] = []
        for connection, result in zip(routed.connections, results, strict=True):
            for a, b in zip(result.waypoints, result.waypoints[1:], strict=False):
                segments.append((connection.key(), a, b))
        for i, (key_a, a1, a2) in enumerate(segments):
            for key_b, b1, b2 in segments[i + 1:]:
                if key_a == key_b:
                    continue
                if _segments_cross(a1, a2, b1, b2):
                    report.issues.append(AestheticIssue(
                        code=CODE_ROUTE_CROSSING, severity="warning", folio=folio,
                        message=f"las rutas {key_a} y {key_b} se cruzan",
                        suggestion=("reordena los elementos o usa una capa "
                                    "intermedia para separar los cables"),
                        objects=(key_a, key_b)))
                else:
                    distance = _segments_distance(a1, a2, b1, b2)
                    if distance < min_separation:
                        report.issues.append(AestheticIssue(
                            code=CODE_ROUTE_TOO_CLOSE, severity="warning", folio=folio,
                            message=(f"las rutas {key_a} y {key_b} pasan a "
                                     f"{distance:.0f} px (mínimo {min_separation:g} px)"),
                            suggestion="separa los cables o cambia el punto de entrada",
                            objects=(key_a, key_b)))


def validate_aesthetics(project: Project, catalog: SymbolCatalog,
                        config=None) -> AestheticReport:
    """Audita la estética de todos los folios del proyecto.

    ``config`` es un :class:`qetgen.config.QetGenConfig` (opcional): si no se
    pasa, se usan los valores por defecto documentados.
    """
    report = AestheticReport()
    if config is None:
        from ..config import QetGenConfig
        config = QetGenConfig()
    measurer = TextMeasurer(
        font_family=config.typography.font_family,
        default_size=config.typography.default_size,
        char_width_ratio=config.typography.char_width_ratio,
        line_height_ratio=config.typography.line_height_ratio,
        px_per_pt=getattr(config.typography, "px_per_pt", 4.0 / 3.0))
    grid = Grid(size=config.layout.grid_size, enabled=config.layout.snap_to_grid)

    for sheet in project.folios:
        report.sheets_analyzed += 1
        _check_sheet(
            sheet, catalog, measurer, grid, report,
            margin=config.sheet.margin,
            min_font_size=config.typography.min_size,
            min_separation=config.layout.min_separation,
            route_manhattan=config.layout.route_manhattan,
            edge_tolerance=config.sheet.edge_tolerance)
    return report


__all__ = [
    "CODE_EMPTY_SHEET",
    "CODE_IN_TITLEBLOCK",
    "CODE_LABEL_OVERLAP",
    "CODE_OUT_OF_SAFE_AREA",
    "CODE_OUT_OF_SHEET",
    "CODE_ROUTE_CROSSING",
    "CODE_ROUTE_TOO_CLOSE",
    "CODE_SYMBOL_OVERLAP",
    "CODE_TEXT_OVERLAP",
    "CODE_TEXT_TOO_WIDE",
    "CODE_TINY_TEXT",
    "CODE_UNROUTED",
    "AestheticIssue",
    "AestheticReport",
    "validate_aesthetics",
]
