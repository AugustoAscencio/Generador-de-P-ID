"""layout/labels.py — Colocación de etiquetas junto a los símbolos.

En QElectroTech la etiqueta de un elemento se coloca según el
``<dynamic_text>`` que declara su ``.elmt`` (posición fija relativa al
hotspot). Esa posición **no** se puede cambiar sin editar el símbolo.

Este módulo resuelve el problema equivalente en nuestro motor: propone
posiciones candidatas alrededor del símbolo (N/E/S/O y diagonales) y elige la
primera que **no colisiona** con nada. Se usa para:

* la previsualización SVG (dónde leería mejor el ojo),
* el validador estético (una etiqueta que pisa a otro símbolo es un aviso
  accionable),
* las herramientas MCP que limpian y reordenan un plano.

No modifica el ``.qet``: es una capa de diseño, como el routing.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..core.catalog import SymbolCatalog
from ..core.geometry import BBox
from ..core.models import Sheet
from .placement import component_bounds, label_bounds
from .textmetrics import TextMeasurer

#: Candidatos en orden de preferencia: E, W, N, S y diagonales.
CANDIDATE_SIDES = ("e", "w", "n", "s", "ne", "nw", "se", "sw")


@dataclass(frozen=True)
class PlacedLabel:
    """Etiqueta colocada junto a un componente."""

    component_id: str
    text: str
    x: float
    y: float
    side: str
    box: BBox
    free: bool = True

    def as_dict(self) -> dict:
        return {
            "component_id": self.component_id,
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "side": self.side,
            "free": self.free,
            "box": list(self.box.as_tuple()),
        }


def _candidate_anchor(side: str, box: BBox, width: float, height: float,
                       margin: float) -> tuple[float, float]:
    """Ancla (esquina superior izquierda) de la etiqueta en una posición candidata."""
    cx = (box.x1 + box.x2) / 2.0
    cy = (box.y1 + box.y2) / 2.0
    if side == "e":
        return (box.x2 + margin, cy - height / 2.0)
    if side == "w":
        return (box.x1 - margin - width, cy - height / 2.0)
    if side == "n":
        return (cx - width / 2.0, box.y1 - margin - height)
    if side == "s":
        return (cx - width / 2.0, box.y2 + margin)
    if side == "ne":
        return (box.x2 + margin, box.y1 - margin - height)
    if side == "nw":
        return (box.x1 - margin - width, box.y1 - margin - height)
    if side == "se":
        return (box.x2 + margin, box.y2 + margin)
    if side == "sw":
        return (box.x1 - margin - width, box.y2 + margin)
    return (box.x2 + margin, cy - height / 2.0)


def place_labels(sheet: Sheet, catalog: SymbolCatalog, measurer: TextMeasurer,
                 occupied: list[BBox] | None = None, margin: float = 4.0,
                 max_candidates: int = 8) -> list[PlacedLabel]:
    """Coloca la etiqueta de cada componente buscando una posición libre.

    ``occupied`` son cajas que ya están ocupadas (símbolos, textos y bloques
    del folio). Las candidatas que chocan con ellas se descartan.
    """
    obstacles: list[BBox] = list(occupied or [])
    for text in sheet.texts:
        obstacles.append(label_bounds(text, measurer))
    for shape in sheet.shapes:
        obstacles.append(BBox(min(shape.x1, shape.x2), min(shape.y1, shape.y2),
                              max(shape.x1, shape.x2), max(shape.y1, shape.y2)))

    placed: list[PlacedLabel] = []
    for component in sheet.elements:
        if not catalog.has(component.type):
            continue
        text = component.resolved_label()
        if not text:
            continue
        symbol = catalog.get(component.type)
        box = component_bounds(component, symbol)
        width, height = measurer.measure(text).as_tuple()
        best: PlacedLabel | None = None
        for side in CANDIDATE_SIDES[:max(1, max_candidates)]:
            x, y = _candidate_anchor(side, box, width, height, margin)
            candidate = BBox(x, y, x + width, y + height)
            clash = any(candidate.intersects(other, margin) for other in obstacles)
            if best is None:
                best = PlacedLabel(component.id, text, x, y, side, candidate, not clash)
            if not clash:
                best = PlacedLabel(component.id, text, x, y, side, candidate, True)
                break
        if best is not None:
            placed.append(best)
            obstacles.append(best.box)
    return placed


__all__ = ["CANDIDATE_SIDES", "PlacedLabel", "place_labels"]
