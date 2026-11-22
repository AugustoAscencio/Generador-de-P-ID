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

import math
from dataclasses import dataclass, field

from ..core.catalog import SymbolCatalog
from ..core.geometry import BBox, rotated_bbox
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


def _fit_to_grid(value: float, low: float, high: float, size: float) -> float:
    """Ajusta ``value`` al intervalo ``[low, high]`` **manteniendo la rejilla**.

    El ajuste se hace sobre los múltiplos de la rejilla que caben en el
    intervalo: así el símbolo nunca se sale del folio y, al mismo tiempo, sus
    coordenadas siguen alineadas (la rejilla es un contrato del motor).
    """
    if low > high:
        return value
    snapped_low = math.ceil(low / size - 1e-9) * size
    snapped_high = math.floor(high / size + 1e-9) * size
    if snapped_low > snapped_high:
        return value          # no cabe ningún múltiplo: se deja el valor
    return min(max(value, snapped_low), snapped_high)


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

    # Caja de cada símbolo **rotada**, relativa al hotspot. Es la que decide
    # dónde puede colocarse: el hotspot no es el centro del símbolo.
    local_boxes: dict[str, BBox] = {}
    for component in updated.elements:
        if not catalog.has(component.type):
            continue
        symbol = catalog.get(component.type)
        local_boxes[component.id] = rotated_bbox(
            symbol.placement_bounds, component.orientation)

    # Ancho máximo de símbolo por capa (para dimensionar las columnas).
    width_by_layer: dict[int, float] = {}
    for component in updated.elements:
        local = local_boxes.get(component.id)
        if local is None:
            continue
        layer = layers.get(component.id, 0)
        width_by_layer[layer] = max(width_by_layer.get(layer, 0.0), local.width)

    # Columnas: si no caben con el hueco pedido, se comprime el hueco (nunca
    # se saca un símbolo del folio).
    column_layers = sorted(width_by_layer)
    total_symbols = sum(width_by_layer.values())
    gaps = max(0, len(column_layers) - 1)
    gap = column_gap
    if gaps and total_symbols + gap * gaps > usable.width:
        gap = max(grid.size, (usable.width - total_symbols) / gaps)

    column_x: dict[int, float] = {}
    cursor = usable.x1
    for layer in column_layers:
        width = width_by_layer[layer]
        column_x[layer] = cursor + width / 2.0
        cursor += width + gap

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

    # Flujo de columnas: si una capa no cabe en una sola columna (demasiados
    # elementos), los sobrantes **envuelven** a una columna nueva a la
    # derecha, en vez de quedarse sin colocar.
    extra_columns: list[float] = []
    next_extra_x = cursor

    def _place_in_column(center: float, start_y: float, local: BBox,
                         min_x: float, max_x: float, min_y: float, max_y: float,
                         occupied: list[BBox]):
        """Coloca un símbolo en una columna; ``None`` si no cabe."""
        target_x = center - (local.x1 + local.x2) / 2.0
        target_y = start_y - local.y1
        for _attempt in range(201):
            new_x, new_y = grid.snap_point(target_x, target_y)
            new_x = _fit_to_grid(new_x, min_x, max_x, grid.size)
            new_y = _fit_to_grid(new_y, min_y, max_y, grid.size)
            candidate_box = local.translated(new_x, new_y)
            if candidate_box.y2 > usable.y2 + 1e-6:
                return None              # no cabe en esta columna
            if not any(candidate_box.intersects(other) for other in occupied):
                return (new_x, new_y, candidate_box)
            target_y += max(grid.size, row_gap)
        return None

    for layer in sorted(by_layer):
        components = sorted(by_layer[layer], key=lambda c: (c.y, c.id))
        column_center = column_x.get(layer)
        cursor_y = usable.y1
        for component in components:
            if respect_locked and component.locked:
                local = local_boxes.get(component.id)
                if local is not None:
                    cursor_y = max(cursor_y, component.y + local.y2 + row_gap)
                continue
            local = local_boxes.get(component.id)
            if local is None:
                continue

            # Límites de posición del hotspot para que la caja completa
            # quepa en el área útil.
            min_x = usable.x1 - local.x1
            max_x = usable.x2 - local.x2
            min_y = usable.y1 - local.y1
            max_y = usable.y2 - local.y2

            centers = ([column_center] if column_center is not None else []) \
                + extra_columns
            placed = None
            used_center = None
            for center in centers:
                placed = _place_in_column(center, cursor_y, local, min_x, max_x,
                                          min_y, max_y, occupied)
                if placed is not None:
                    used_center = center
                    break

            if placed is None:
                # La columna se ha llenado: se abre una columna nueva a la
                # derecha y se empieza por arriba.
                width = local.width
                new_center = next_extra_x + width / 2.0
                if new_center + width / 2.0 > usable.x2 + 1e-6:
                    report.unresolved.append(component.id)
                    continue
                next_extra_x = new_center + width / 2.0 + gap
                extra_columns.append(new_center)
                placed = _place_in_column(new_center, usable.y1, local, min_x,
                                          max_x, min_y, max_y, occupied)
                if placed is None:
                    report.unresolved.append(component.id)
                    continue
                used_center = new_center

            new_x, new_y, candidate_box = placed
            old_position = (component.x, component.y)
            component.x = new_x
            component.y = new_y
            report.moved.append((component.id, old_position, (new_x, new_y)))
            occupied.append(candidate_box.inflated(clearance))
            if used_center == column_center:
                cursor_y = candidate_box.y2 + row_gap
            else:
                cursor_y = candidate_box.y2 + row_gap

    updated.layout_applied = True
    return updated, report


__all__ = ["LayoutReport", "auto_layout", "compute_layers"]
