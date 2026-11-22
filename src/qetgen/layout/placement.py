"""layout/placement.py — Geometría de colocación en el folio.

Concentra las preguntas de *dónde está cada cosa*:

* ¿qué caja ocupa un componente colocado (con su rotación)?,
* ¿dónde queda exactamente una terminal después de rotar el símbolo?,
* ¿qué caja ocupa un texto?,
* ¿qué caja ocupa un bloque?

La rotación usa la convención de QElectroTech: ``orientation`` 0..3 =
0°, 90°, 180°, 270° en **sentido horario** (Y crece hacia abajo).
"""

from __future__ import annotations

from ..core.catalog import SymbolDefinition
from ..core.geometry import BBox, rotate_point
from ..core.models import Component, Label, Shape
from .textmetrics import TextMeasurer


def transform_box(box: BBox, dx: float, dy: float, quarters: int = 0) -> BBox:
    """Rota una caja alrededor del origen y la desplaza a ``(dx, dy)``."""
    corners = ((box.x1, box.y1), (box.x2, box.y1),
               (box.x2, box.y2), (box.x1, box.y2))
    moved = []
    for x, y in corners:
        rx, ry = rotate_point(x, y, quarters)
        moved.append((rx + dx, ry + dy))
    result = BBox.from_points(moved)
    return result if result is not None else box


def component_bounds(component: Component, symbol: SymbolDefinition) -> BBox:
    """Caja **reservada** de un componente colocado (rotación incluida).

    Es la caja declarada por el ``.elmt`` (``width``×``height`` con el
    hotspot en ``hotspot_x``/``hotspot_y``). Se usa para comprobar que el
    símbolo cabe en la zona segura de la hoja.
    """
    return transform_box(symbol.placement_bounds, component.x, component.y,
                         component.orientation)


def component_ink_bounds(component: Component, symbol: SymbolDefinition) -> BBox:
    """Caja de la **tinta real** de un componente colocado.

    Es la caja de las primitivas del ``<description>`` del ``.elmt``. Se usa
    para detectar colisiones: lo que se pisa visualmente es la tinta, no el
    espacio en blanco que el símbolo reserva a su alrededor.
    """
    return transform_box(symbol.ink_bounds, component.x, component.y,
                         component.orientation)


def terminal_position(component: Component, symbol: SymbolDefinition,
                      terminal_index: int) -> tuple[float, float]:
    """Posición absoluta de una terminal en el folio (rotación incluida).

    Las coordenadas de la terminal en el ``.elmt`` son relativas al hotspot y
    rotan con el símbolo, igual que en QElectroTech.
    """
    port = symbol.terminals[terminal_index]
    dx, dy = rotate_point(port.x, port.y, component.orientation)
    return (component.x + dx, component.y + dy)


def terminal_direction(component: Component, symbol: SymbolDefinition,
                       terminal_index: int) -> str:
    """Dirección de salida preferida de una terminal: ``n``/``e``/``s``/``w``.

    La orientación de la terminal en el ``.elmt`` rota con el componente.
    """
    port = symbol.terminals[terminal_index]
    order = {"n": 0, "e": 1, "s": 2, "w": 3}
    index = order.get(port.orientation, 0)
    rotated = ["n", "e", "s", "w"][(index + component.orientation) % 4]
    return rotated


def label_bounds(label: Label, measurer: TextMeasurer) -> BBox:
    """Caja envolvente de un texto independiente del folio."""
    left, top, right, bottom = measurer.measure_box(
        label.text, label.x, label.y, size=label.size,
        rotation=label.rotation, align=label.align)
    return BBox(left, top, right, bottom)


def shape_bounds(shape: Shape) -> BBox:
    """Caja envolvente de un bloque funcional."""
    return BBox(min(shape.x1, shape.x2), min(shape.y1, shape.y2),
                max(shape.x1, shape.x2), max(shape.y1, shape.y2))


def component_label_bounds(component: Component, symbol: SymbolDefinition,
                            measurer: TextMeasurer) -> BBox:
    """Caja de la etiqueta dinámica que QET coloca junto al símbolo.

    La posición viene del ``<dynamic_text>`` real del ``.elmt``
    (``label_pos``), que es relativa al hotspot, igual que las terminales.
    """
    text = component.resolved_label()
    if not text:
        return BBox(component.x, component.y, component.x, component.y)
    width, height = measurer.measure(text).as_tuple()
    local = BBox(symbol.label_pos[0], symbol.label_pos[1],
                 symbol.label_pos[0] + width, symbol.label_pos[1] + height)
    return transform_box(local, component.x, component.y, component.orientation)


__all__ = [
    "component_bounds",
    "component_ink_bounds",
    "component_label_bounds",
    "label_bounds",
    "shape_bounds",
    "terminal_direction",
    "terminal_position",
    "transform_box",
]
