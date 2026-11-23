"""exporters/svg/ — Previsualización SVG de un folio.

Por qué un exportador SVG: QElectroTech **no** tiene modo headless ni
expone el trazado de los conductores (los recalcula al abrir, evidencia §4
del formato). Para poder revisar un plano sin instalar QET, este exportador
dibuja:

* la hoja real (rejilla, borde y banda del cajetín),
* los bloques funcionales,
* los **símbolos reales** renderizados desde las primitivas de su ``.elmt``,
* los textos con la métrica tipográfica del motor,
* las **rutas ortogonales calculadas** por :mod:`qetgen.layout.router`
  (la intención de diseño del cableado).

El SVG es un **preview**, no un formato de entrega: el entregable sigue siendo
el ``.qet`` editable.
"""

from __future__ import annotations

import html
from pathlib import Path

from ...core.catalog import SymbolCatalog
from ...core.geometry import BBox
from ...core.models import Project, Sheet
from ...core.sheet import SheetFormat, get_sheet_format
from .elmt import render_symbol

#: Colores por defecto del preview.
BACKGROUND = "#ffffff"
GRID_COLOR = "#e6e6e6"
BORDER_COLOR = "#000000"
TITLEBLOCK_FILL = "#f2f2f2"
TEXT_COLOR = "#000000"


def _escape(text: str) -> str:
    return html.escape(str(text), quote=True)


def sheet_to_svg(sheet: Sheet, catalog: SymbolCatalog,
                 fmt: SheetFormat | None = None, *, show_grid: bool = True,
                 show_routes: bool = True, background: str = BACKGROUND,
                 wire_color: str = "#000000", px_per_pt: float = 4.0 / 3.0,
                 font_family: str = "Sans Serif") -> str:
    """Genera el SVG de un folio completo."""
    fmt = fmt or get_sheet_format(sheet.sheet_format)
    width = fmt.width
    usable = fmt.usable_height
    height = fmt.height

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
        f'width="{width:g}" height="{height:g}" '
        f'viewBox="0 0 {width:g} {height:g}" '
        f'font-family="{_escape(font_family)}">')
    out.append(f'  <title>{_escape(sheet.title or f"Folio {sheet.order}")}</title>')
    out.append(f'  <rect x="0" y="0" width="{width:g}" height="{usable:g}" '
               f'fill="{background}" />')

    # -- rejilla visible de QET (60 × 80 por defecto) ------------------------
    if show_grid:
        out.append('  <g stroke="' + GRID_COLOR + '" stroke-width="0.5">')
        x = fmt.colsize
        while x < width:
            out.append(f'    <line x1="{x}" y1="0" x2="{x}" y2="{usable:g}" />')
            x += fmt.colsize
        y = fmt.rowsize
        while y < usable:
            out.append(f'    <line x1="0" y1="{y}" x2="{width:g}" y2="{y}" />')
            y += fmt.rowsize
        out.append('  </g>')

    # -- cajetín (banda inferior) --------------------------------------------
    out.append(f'  <rect x="0" y="{usable:g}" width="{width:g}" '
               f'height="{fmt.titleblock_height:g}" fill="{TITLEBLOCK_FILL}" '
               f'stroke="{BORDER_COLOR}" stroke-width="1" />')
    out.append(f'  <rect x="0" y="0" width="{width:g}" height="{usable:g}" '
               f'fill="none" stroke="{BORDER_COLOR}" stroke-width="1" />')

    # -- bloques funcionales --------------------------------------------------
    out.append('  <g id="shapes">')
    for shape in sheet.shapes:
        x = min(shape.x1, shape.x2)
        y = min(shape.y1, shape.y2)
        w = abs(shape.x2 - shape.x1)
        h = abs(shape.y2 - shape.y1)
        fill = shape.fill or "none"
        dash = ' stroke-dasharray="6 4"' if shape.dash else ""
        out.append(f'    <rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
                   f'fill="{fill}" stroke="{shape.color}" '
                   f'stroke-width="{shape.width:g}"{dash} />')
    out.append('  </g>')

    # -- símbolos (primitivas reales del .elmt) ------------------------------
    out.append('  <g id="components">')
    for component in sheet.elements:
        if not catalog.has(component.type):
            continue
        symbol = catalog.get(component.type)
        rotation = component.orientation * 90
        out.append(f'    <g id="{_escape(component.id)}" '
                   f'transform="translate({component.x:g},{component.y:g}) '
                   f'rotate({rotation})">')
        body = render_symbol(symbol, px_per_pt=px_per_pt)
        if body:
            out.append(f'      {body}')
        label = component.resolved_label()
        if label:
            lx, ly = symbol.label_pos
            out.append(f'      <text x="{lx:g}" y="{ly:g}" font-size="12" '
                       f'fill="{TEXT_COLOR}" dominant-baseline="text-before-edge">'
                       f'{_escape(label)}</text>')
        out.append('    </g>')
    out.append('  </g>')

    # -- rutas ortogonales (intención de diseño del cableado) ----------------
    if show_routes:
        out.append(f'  <g id="routes" fill="none" stroke="{wire_color}" '
                   f'stroke-width="1.2">')
        for connection in sheet.connections:
            if not connection.waypoints:
                continue
            points = " ".join(f"{x:g},{y:g}" for x, y in connection.waypoints)
            out.append(f'    <polyline points="{points}" />')
        out.append('  </g>')

    # -- textos independientes ------------------------------------------------
    out.append('  <g id="texts">')
    for text in sheet.texts:
        size = text.size * px_per_pt
        anchor = "start"
        if text.align == "center":
            anchor = "middle"
        elif text.align == "right":
            anchor = "end"
        rotation = f' transform="rotate({text.rotation} {text.x:g} {text.y:g})"' \
            if text.rotation else ""
        out.append(f'    <text x="{text.x:g}" y="{text.y:g}" font-size="{size:g}" '
                   f'text-anchor="{anchor}" fill="{TEXT_COLOR}" '
                   f'dominant-baseline="text-before-edge"{rotation}>'
                   f'{_escape(text.text)}</text>')
    out.append('  </g>')

    out.append('</svg>')
    return "\n".join(out)


def export_sheet_svg(sheet: Sheet, catalog: SymbolCatalog,
                     output_path: str | Path, **kwargs) -> Path:
    """Escribe el SVG de un folio en disco."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(sheet_to_svg(sheet, catalog, **kwargs),
                           encoding="utf-8", newline="\n")
    return output_path


def export_project_svg(project: Project, catalog: SymbolCatalog,
                       output_dir: str | Path, **kwargs) -> list[Path]:
    """Escribe un SVG por folio del proyecto y devuelve las rutas escritas."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, sheet in enumerate(project.folios, start=1):
        name = f"folio_{index:02d}.svg"
        written.append(export_sheet_svg(sheet, catalog, output_dir / name, **kwargs))
    return written


def sheet_bounds(sheet: Sheet) -> BBox:
    """Caja envolvente de todo el contenido del folio."""
    fmt = get_sheet_format(sheet.sheet_format)
    return fmt.drawing_area


__all__ = [
    "export_project_svg",
    "export_sheet_svg",
    "sheet_bounds",
    "sheet_to_svg",
]
