"""layout/router.py — Routing ortogonal Manhattan con A*.

Por qué un router propio (y no el de QElectroTech):

* **Evidencia §4 del formato**: QET **recalcula** el trazado de los
  conductores al abrir el proyecto; el ``<segment>`` que se ve en los archivos
  reales es solo una caché de render. Escribir una polilínea en el ``.qet``
  sería inventar formato (prohibido).
* Por tanto, el motor calcula la **ruta de diseño** y la guarda en
  ``Connection.waypoints``: alimenta el exportador SVG, el validador
  estético y el auto-layout, mientras el ``.qet`` conserva la representación
  nativa terminal→terminal.

El algoritmo es A* sobre una rejilla, con el estado ``(nodo, dirección)`` para
poder penalizar los giros. Costes:

============================  ===========================================
Coste                         Significado
============================  ===========================================
longitud                      distancia recorrida (px)
``turn_penalty``              cada giro de 90° (evita trayectorias en zigzag)
``crossing_penalty``          cruzar un conductor ya trazado
separación mínima             paralelos demasiado juntos
============================  ===========================================
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from ..core.catalog import SymbolCatalog
from ..core.geometry import BBox
from ..core.models import Connection, Sheet
from .grid import Grid
from .placement import (component_ink_bounds, terminal_direction,
                        terminal_position)

#: Direcciones: 0=E(+x), 1=S(+y), 2=W(-x), 3=N(-y).
DIR_E, DIR_S, DIR_W, DIR_N = 0, 1, 2, 3
_DIR_VECTORS = ((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0))

#: Dirección de salida preferida por orientación de terminal.
_ORIENTATION_TO_DIR = {"e": DIR_E, "s": DIR_S, "w": DIR_W, "n": DIR_N}


@dataclass(frozen=True)
class RouteResult:
    """Resultado del trazado de un conductor."""

    key: str
    waypoints: tuple[tuple[float, float], ...] = ()
    ok: bool = False
    message: str = ""
    length: float = 0.0
    turns: int = 0
    crossings: int = 0

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "ok": self.ok,
            "message": self.message,
            "length": round(self.length, 2),
            "turns": self.turns,
            "crossings": self.crossings,
            "waypoints": [list(p) for p in self.waypoints],
        }


@dataclass
class _Segment:
    """Segmento axis-alineado de una ruta existente."""

    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def horizontal(self) -> bool:
        return abs(self.y1 - self.y2) < 1e-9

    @property
    def vertical(self) -> bool:
        return abs(self.x1 - self.x2) < 1e-9


def _segment_hits_box(x1: float, y1: float, x2: float, y2: float,
                       box: BBox) -> bool:
    """¿El segmento ``(x1,y1)-(x2,y2)`` toca la caja ``box``?

    Algoritmo de **Liang–Barsky** (recorte paramétrico): exacto para
    cualquier orientación del segmento, incluidos los tramos diagonales de
    acceso a la rejilla. Un segmento que **nace dentro** de la caja se
    considera intersección (así lo exige el routing: el cable no puede
    atravesar un símbolo).
    """
    dx = x2 - x1
    dy = y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - box.x1), (dx, box.x2 - x1),
                 (-dy, y1 - box.y1), (dy, box.y2 - y1)):
        if abs(p) < 1e-12:
            if q < 0.0:
                return False        # paralelo a la arista y fuera de la caja
            continue
        r = q / p
        if p < 0.0:
            if r > t1:
                return False
            t0 = max(t0, r)
        else:
            if r < t0:
                return False
            t1 = min(t1, r)
    return t0 <= t1


class ManhattanRouter:
    """Trazador ortogonal con A* y penalizaciones."""

    def __init__(self, bounds: BBox, grid: Grid, obstacles: list[BBox] | None = None,
                 *, turn_penalty: float = 20.0, crossing_penalty: float = 40.0,
                 min_separation: float = 12.0, max_nodes: int = 60000,
                 clearance: float = 6.0):
        self.bounds = bounds
        self.grid = grid
        self.obstacles = list(obstacles or [])
        self.turn_penalty = float(turn_penalty)
        self.crossing_penalty = float(crossing_penalty)
        self.min_separation = float(min_separation)
        self.max_nodes = int(max_nodes)
        self.clearance = float(clearance)
        self._horizontal: list[_Segment] = []
        self._vertical: list[_Segment] = []

    # -- registro de rutas existentes ---------------------------------------

    def register_route(self, waypoints) -> None:
        """Registra una ruta ya trazada (para penalizar cruces y paralelos)."""
        points = list(waypoints)
        for a, b in zip(points, points[1:]):
            if abs(a[0] - b[0]) < 1e-9 and abs(a[1] - b[1]) < 1e-9:
                continue
            segment = _Segment(a[0], a[1], b[0], b[1])
            if segment.horizontal:
                self._horizontal.append(segment)
            elif segment.vertical:
                self._vertical.append(segment)

    # -- obstáculos ---------------------------------------------------------

    def _blocked(self, x: float, y: float) -> bool:
        for obstacle in self.obstacles:
            if obstacle.contains_point(x, y):
                return True
        return False

    def _crosses_obstacle(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Comprueba si un tramo atraviesa algún obstáculo.

        El test es **exacto** (Liang–Barsky: recorte paramétrico del segmento
        contra la caja), no un muestreo: un muestreo puede dejar pasar
        obstáculos finos, que son los que más se cuelan en un cableado real.
        """
        return any(_segment_hits_box(x1, y1, x2, y2, obstacle)
                   for obstacle in self.obstacles)

    def _leg_blocked(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """¿El tramo de acceso a un nodo atraviesa un obstáculo?"""
        return self._crosses_obstacle(x1, y1, x2, y2)

    # -- penalizaciones -----------------------------------------------------

    def _crossings(self, x1: float, y1: float, x2: float, y2: float) -> int:
        """Número de cruces perpendiculares con rutas ya trazadas."""
        count = 0
        horizontal = abs(y1 - y2) < 1e-9
        if horizontal:
            lo, hi = sorted((x1, x2))
            for seg in self._vertical:
                if seg.x1 - 1e-9 > hi or seg.x2 + 1e-9 < lo:
                    continue
                if min(seg.y1, seg.y2) - 1e-9 <= y1 <= max(seg.y1, seg.y2) + 1e-9:
                    count += 1
        else:
            lo, hi = sorted((y1, y2))
            for seg in self._horizontal:
                if seg.y1 - 1e-9 > hi or seg.y2 + 1e-9 < lo:
                    continue
                if min(seg.x1, seg.x2) - 1e-9 <= x1 <= max(seg.x1, seg.x2) + 1e-9:
                    count += 1
        return count

    def _separation_penalty(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Penalización por paralelos demasiado próximos."""
        penalty = 0.0
        if abs(y1 - y2) < 1e-9:
            lo, hi = sorted((x1, x2))
            for seg in self._horizontal:
                s_lo, s_hi = sorted((seg.x1, seg.x2))
                if s_hi < lo - 1e-9 or s_lo > hi + 1e-9:
                    continue
                distance = abs(y1 - seg.y1)
                if distance < self.min_separation:
                    penalty += (self.min_separation - distance) * 2.0
        elif abs(x1 - x2) < 1e-9:
            lo, hi = sorted((y1, y2))
            for seg in self._vertical:
                s_lo, s_hi = sorted((seg.y1, seg.y2))
                if s_hi < lo - 1e-9 or s_lo > hi + 1e-9:
                    continue
                distance = abs(x1 - seg.x1)
                if distance < self.min_separation:
                    penalty += (self.min_separation - distance) * 2.0
        return penalty

    # -- búsqueda ------------------------------------------------------------

    def _nearest_free_node(self, x: float, y: float, max_radius: int = 6):
        """Nodo de rejilla libre más cercano a un punto.

        Un nodo solo es candidato si, además de estar libre, el **tramo de
        acceso** desde el punto original no atraviesa ningún obstáculo: de
        otro modo la ruta podría "entrar" en un símbolo por el lado ciego.
        """
        size = self.grid.size
        ix0 = int(round(x / size))
        iy0 = int(round(y / size))
        for radius in range(max_radius + 1):
            best = None
            best_dist = None
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if max(abs(dx), abs(dy)) != radius:
                        continue
                    ix, iy = ix0 + dx, iy0 + dy
                    nx, ny = ix * size, iy * size
                    if not (self.bounds.x1 - 1e-6 <= nx <= self.bounds.x2 + 1e-6
                            and self.bounds.y1 - 1e-6 <= ny <= self.bounds.y2 + 1e-6):
                        continue
                    if self._blocked(nx, ny):
                        continue
                    if self._leg_blocked(x, y, nx, ny):
                        continue
                    dist = abs(nx - x) + abs(ny - y)
                    if best_dist is None or dist < best_dist:
                        best, best_dist = (ix, iy), dist
            if best is not None:
                return best
        return None

    def route(self, start: tuple[float, float], end: tuple[float, float],
              start_dir: str | None = None, end_dir: str | None = None,
              key: str = "") -> RouteResult:
        """Trazada una ruta ortogonal de ``start`` a ``end``."""
        if abs(start[0] - end[0]) < 1e-9 and abs(start[1] - end[1]) < 1e-9:
            return RouteResult(key=key, waypoints=((start[0], start[1]),), ok=True)

        start_node = self._nearest_free_node(*start)
        goal_node = self._nearest_free_node(*end)
        if start_node is None or goal_node is None:
            return RouteResult(
                key=key, ok=False,
                message="no hay nodo de rejilla libre junto a uno de los extremos")

        size = self.grid.size
        goal = goal_node
        preferred = _ORIENTATION_TO_DIR.get(start_dir or "", None)

        def heuristic(node) -> float:
            return (abs(node[0] - goal[0]) + abs(node[1] - goal[1])) * size

        # El estado incluye la dirección de llegada para penalizar los giros.
        start_states = []
        if preferred is not None:
            start_states.append((start_node, preferred))
        else:
            start_states.extend((start_node, d) for d in range(4))

        open_set: list[tuple[float, float, int, tuple[int, int, int]]] = []
        counter = 0
        came_from: dict[tuple[int, int, int], tuple[int, int, int]] = {}
        cost: dict[tuple[int, int, int], float] = {}

        for node, direction in start_states:
            state = (node[0], node[1], direction)
            cost[state] = 0.0
            heapq.heappush(open_set, (heuristic(node), 0.0, counter, state))
            counter += 1

        visited = 0
        best_state = None
        while open_set:
            _, g_value, _, state = heapq.heappop(open_set)
            if g_value > cost.get(state, float("inf")) + 1e-9:
                continue          # entrada obsoleta del heap
            ix, iy, direction = state
            if (ix, iy) == goal:
                best_state = state
                break             # la heurística es admisible: es óptima
            visited += 1
            if visited > self.max_nodes:
                break

            for new_dir, (vx, vy) in enumerate(_DIR_VECTORS):
                nx, ny = ix + int(vx), iy + int(vy)
                px, py = nx * size, ny * size
                if not (self.bounds.x1 - 1e-6 <= px <= self.bounds.x2 + 1e-6
                        and self.bounds.y1 - 1e-6 <= py <= self.bounds.y2 + 1e-6):
                    continue
                if self._blocked(px, py):
                    continue
                if self._crosses_obstacle(ix * size, iy * size, px, py):
                    continue
                step_cost = size
                if new_dir != direction:
                    step_cost += self.turn_penalty
                crossings = self._crossings(ix * size, iy * size, px, py)
                step_cost += crossings * self.crossing_penalty
                step_cost += self._separation_penalty(ix * size, iy * size, px, py)
                new_state = (nx, ny, new_dir)
                new_cost = cost[state] + step_cost
                if new_cost < cost.get(new_state, float("inf")) - 1e-9:
                    cost[new_state] = new_cost
                    came_from[new_state] = state
                    heapq.heappush(
                        open_set,
                        (new_cost + heuristic((nx, ny)), new_cost, counter, new_state))
                    counter += 1

        if best_state is None:
            return RouteResult(
                key=key, ok=False,
                message=(f"sin ruta ortogonal entre {start} y {end} "
                         f"(nodos explorados: {visited})"))

        # Reconstrucción del camino
        path_states = [best_state]
        while path_states[-1] in came_from:
            path_states.append(came_from[path_states[-1]])
        path_states.reverse()

        points: list[tuple[float, float]] = [start]
        for ix, iy, _dir in path_states:
            point = (ix * size, iy * size)
            if not points or points[-1] != point:
                points.append(point)
        if points[-1] != end:
            points.append(end)

        simplified = _simplify(points)
        length = sum(abs(a[0] - b[0]) + abs(a[1] - b[1])
                     for a, b in zip(simplified, simplified[1:]))
        turns = _count_turns(simplified)
        crossings = self._count_route_crossings(simplified)
        return RouteResult(
            key=key, waypoints=tuple(simplified), ok=True,
            length=length, turns=turns, crossings=crossings,
            message=(f"ruta de {length:.0f} px, {turns} giro(s), "
                     f"{crossings} cruce(s)"))

    def _count_route_crossings(self, points) -> int:
        """Cruces de la propia ruta con las ya registradas."""
        total = 0
        for a, b in zip(points, points[1:]):
            total += self._crossings(a[0], a[1], b[0], b[1])
        return total


def _simplify(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Elimina puntos redundantes y colineales de una polilínea."""
    if len(points) < 3:
        return points
    result = [points[0]]
    for previous, point, following in zip(points, points[1:], points[2:]):
        collinear = ((previous[0] - point[0]) * (following[1] - point[1])
                     - (previous[1] - point[1]) * (following[0] - point[0]))
        if abs(collinear) > 1e-6:
            result.append(point)
    result.append(points[-1])
    return result


def _count_turns(points) -> int:
    """Número de giros de 90° de una polilínea."""
    turns = 0
    for a, b, c in zip(points, points[1:], points[2:]):
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        if abs(v1[0] * v2[1] - v1[1] * v2[0]) > 1e-6:
            turns += 1
    return turns


def route_sheet(sheet: Sheet, catalog: SymbolCatalog, grid: Grid,
                bounds: BBox, *, turn_penalty: float = 20.0,
                crossing_penalty: float = 40.0, min_separation: float = 12.0,
                max_nodes: int = 60000, clearance: float = 6.0,
                route_manhattan: bool = True) -> tuple[Sheet, list[RouteResult]]:
    """Traza todos los conductores de un folio y guarda los ``waypoints``.

    Devuelve una **copia** del folio con ``Connection.waypoints`` rellenados y
    la lista de resultados (uno por conductor).

    Los obstáculos de cada trazado excluyen los dos símbolos que se conectan:
    la terminal vive *sobre* el borde de su símbolo y debe poder salir.
    """
    updated = sheet.model_copy(deep=True)
    results: list[RouteResult] = []
    if not route_manhattan:
        return updated, results

    boxes: dict[str, BBox] = {}
    for component in updated.elements:
        if catalog.has(component.type):
            boxes[component.id] = component_ink_bounds(
                component, catalog.get(component.type))

    router = ManhattanRouter(
        bounds=bounds, grid=grid,
        obstacles=[box.inflated(clearance) for box in boxes.values()],
        turn_penalty=turn_penalty, crossing_penalty=crossing_penalty,
        min_separation=min_separation, max_nodes=max_nodes, clearance=clearance)

    for connection in updated.connections:
        if connection.locked and connection.waypoints:
            router.register_route(connection.waypoints)
            results.append(RouteResult(key=connection.key(),
                                       waypoints=tuple(connection.waypoints),
                                       ok=True, message="ruta fijada (locked)"))
            continue
        if connection.from_id not in boxes or connection.to_id not in boxes:
            results.append(RouteResult(key=connection.key(), ok=False,
                                       message="componente sin símbolo en el catálogo"))
            continue

        src = next(c for c in updated.elements if c.id == connection.from_id)
        dst = next(c for c in updated.elements if c.id == connection.to_id)
        src_symbol = catalog.get(src.type)
        dst_symbol = catalog.get(dst.type)

        try:
            start = terminal_position(src, src_symbol, connection.from_terminal)
            end = terminal_position(dst, dst_symbol, connection.to_terminal)
            start_dir = terminal_direction(src, src_symbol, connection.from_terminal)
            end_dir = terminal_direction(dst, dst_symbol, connection.to_terminal)
        except IndexError:
            results.append(RouteResult(key=connection.key(), ok=False,
                                       message="terminal fuera de rango"))
            continue

        # Obstáculos sin los dos extremos de esta conexión.
        router.obstacles = [
            boxes[cid].inflated(clearance)
            for cid in boxes if cid not in (connection.from_id, connection.to_id)
        ]
        result = router.route(start, end, start_dir=start_dir, end_dir=end_dir,
                              key=connection.key())
        results.append(result)
        if result.ok:
            connection.waypoints = list(result.waypoints)
            router.register_route(result.waypoints)
    return updated, results


__all__ = ["ManhattanRouter", "RouteResult", "route_sheet"]
