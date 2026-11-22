"""layout/autolayout.py — Reubicación automática con **modo híbrido**.

Filosofía: el auto-layout **no** es un botón de "destruir y rehacer". Es un
motor que:

* respeta los elementos con ``locked: true`` (decisión del ingeniero o de la
  IA: no se tocan),
* respeta la intención vertical del autor (el orden Y dentro de cada capa se
  conserva),
* calcula el flujo lógico de izquierda a derecha a partir del grafo de
  conexiones (capas por camino más largo),
* evita colisiones comprobando la caja real de cada símbolo,
* es **reversible**: informa de qué movió y de qué no pudo resolver.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.catalog import SymbolCatalog
from ..core.geometry import BBox
from ..core.models import Sheet
from .grid import Grid
from .placement import component_bounds


@dataclass
class LayoutReport:
    """Informe de lo que hizo el auto-layout."""

    moved: list[tuple[str, tuple[float, float], tuple[float, float]]] = field(default_factory=list)
    kept_locked: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    layers: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """``True`` si no quedó ningún símbolo sin colocar."""
        return not self.unresolved

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "moved": [
                {"id": mid, "from": list(old), "to": list(new)}
                for mid, old, new in self.moved
            ],
            "kept_locked": list(self.kept_locked),
            "unresolved": list(self.unresolved),
            "layers": dict(self.layers),
        }


def compute_layers(sheet: Sheet) -> dict[str, int]:
    """Calcula la capa (columna) de cada componente a partir del grafo.

    Se usa el algoritmo del camino más largo: la capa de un componente es
    ``1 + max(capa de sus predecesores)``. Los ciclos se rompen de forma
    determinista (orden lexicográfico) para que el resultado sea reproducible.
    """
    ids = [component.id for component in sheet.elements]
    incoming: dict[str, list[str]] = {cid: [] for cid in ids}
    outgoing: dict[str, list[str]] = {cid: [] for cid in ids}
    for connection in sheet.connections:
        if connection.from_id in incoming and connection.to_id in incoming:
            incoming[connection.to_id].append(connection.from_id)
            outgoing[connection.from_id].append(connection.to_id)

    layer: dict[str, int] = {}
    visiting: set[str] = set()

    def resolve(cid: str) -> int:
        if cid in layer:
            return layer[cid]
        if cid in visiting:                 # ciclo: se corta aquí
            return 0
        visiting.add(cid)
        best = 0
        for parent in sorted(incoming[cid]):
            best = max(best, resolve(parent) + 1)
        visiting.discard(cid)
        layer[cid] = best
        return best

    for cid in sorted(ids):
        resolve(cid)
    return layer


def auto_layout(sheet: Sheet, catalog: SymbolCatalog, grid: Grid,
                bounds: BBox, *, respect_locked: bool = True,
                column_gap: float = 70.0, row_gap: float = 35.0,
                clearance: float = 18.0, margin: float = 10.0) -> tuple[Sheet, LayoutReport]:
    """Reubica los componentes del folio en columnas lógicas.

    Devuelve una **copia** del folio ya reubicado y el informe de cambios.
    """
    updated = sheet.model_copy(deep=True)
    report = LayoutReport()

    usable = bounds.inset(margin)
    layers = compute_layers(updated)
    report.layers = dict(layers)

    # Ancho máximo de símbolo por capa (para dimensionar las columnas).
    width_by_layer: dict[int, float] = {}
    for component in updated.elements:
        if not catalog.has(component.type):
            continue
        symbol = catalog.get(component.type)
        box = component_bounds(component, symbol)
        layer = layers.get(component.id, 0)
        width_by_layer[layer] = max(width_by_layer.get(layer, 0.0), box.width)

    column_x: dict[int, float] = {}
    cursor = usable.x1
    for layer in sorted(width_by_layer):
        column_x[layer] = cursor + width_by_layer[layer] / 2.0
        cursor += width_by_layer[layer] + column_gap

    # Cajas ya ocupadas: los elementos bloqueados no se mueven.
    occupied: list[BBox] = []
    for component in updated.elements:
        if respect_locked and component.locked:
            if catalog.has(component.type):
                occupied.append(component_bounds(
                    component, catalog.get(component.type)).inflated(clearance))
            report.kept_locked.append(component.id)

    by_layer: dict[int, list] = {}
    for component in updated.elements:
        by_layer.setdefault(layers.get(component.id, 0), []).append(component)

    for layer in sorted(by_layer):
        components = sorted(by_layer[layer], key=lambda c: (c.y, c.id))
        if respect_locked:
            movable = [c for c in components if not c.locked]
        else:
            movable = list(components)
        cursor_y = usable.y1
        for component in components:
            if respect_locked and component.locked:
                cursor_y = max(cursor_y, component.y + 10)
                continue
            if not catalog.has(component.type):
                continue
            symbol = catalog.get(component.type)
            box = component_bounds(component, symbol)
            target_x = column_x.get(layer, component.x)
            target_y = max(cursor_y, usable.y1)
            new_x, new_y = grid.snap_point(target_x, target_y)
            candidate = component.model_copy(update={"x": new_x, "y": new_y})
            candidate_box = component_bounds(candidate, symbol)

            attempts = 0
            while any(candidate_box.intersects(other) for other in occupied) \
                    and attempts < 200:
                target_y += max(grid.size, row_gap)
                new_x, new_y = grid.snap_point(target_x, target_y)
                candidate = component.model_copy(update={"x": new_x, "y": new_y})
                candidate_box = component_bounds(candidate, symbol)
                attempts += 1

            if any(candidate_box.intersects(other) for other in occupied):
                report.unresolved.append(component.id)
                continue

            old_position = (component.x, component.y)
            component.x = new_x
            component.y = new_y
            report.moved.append((component.id, old_position, (new_x, new_y)))
            occupied.append(candidate_box.inflated(clearance))
            cursor_y = new_y + box.height / 2.0 + row_gap

    updated.layout_applied = True
    return updated, report


__all__ = ["LayoutReport", "auto_layout", "compute_layers"]
