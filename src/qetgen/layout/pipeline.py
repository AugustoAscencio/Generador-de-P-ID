"""layout/pipeline.py — Orquestación del motor de layout sobre un proyecto.

El motor tiene piezas independientes (rejilla, colocación, colisiones,
etiquetas, routing, auto-layout). Este módulo las **compone** en un flujo
único y reversible, que es exactamente lo que necesitan tanto la CLI
(``qetgen layout``) como el servidor MCP (``ejecutar_auto_layout``):

1. **snap** — cuantiza a la rejilla lo que el ingeniero no ha bloqueado.
2. **auto-layout** — reubica en columnas lógicas respetando ``locked``.
3. **routing** — calcula la ruta Manhattan de cada conductor.

Reglas del proyecto:

* ``locked: true`` significa **"esto no se toca"**: ni el snap, ni el
  auto-layout, ni el router recalculan ese elemento.
* Ninguna etapa **decide ingeniería**: solo mueve lo que el usuario pide
  mover y deja constancia de lo que hizo.
* El resultado es un **informe** de lo movido, lo bloqueado y lo no resuelto:
  ninguna transformación es silenciosa.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..config import QetGenConfig
from ..core.catalog import SymbolCatalog
from ..core.models import Project, Sheet
from ..core.sheet import get_sheet_format
from .autolayout import auto_layout
from .grid import Grid
from .router import RouteResult, route_sheet


@dataclass(frozen=True)
class LayoutOptions:
    """Opciones del pipeline de layout."""

    snap: bool = False
    """Cuantizar las coordenadas a la rejilla."""

    auto_layout: bool = False
    """Reubicar los componentes en columnas lógicas (modo híbrido)."""

    route: bool = True
    """Calcular las rutas ortogonales de los conductores."""

    snap_texts: bool = False
    """Cuantizar también los textos (por defecto no: suelen estar afinados)."""

    respect_locked: bool = True
    """Respetar ``locked: true`` (modo híbrido)."""

    folio: int | None = None
    """Limitar la operación a un folio (1..N); ``None`` = todos."""


@dataclass
class FolioResult:
    """Resultado del layout sobre un folio."""

    folio: int
    title: str
    snapped: int = 0
    moved: list[tuple[str, tuple[float, float], tuple[float, float]]] = field(
        default_factory=list)
    kept_locked: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    routes: list[RouteResult] = field(default_factory=list)

    @property
    def routes_ok(self) -> int:
        return sum(1 for route in self.routes if route.ok)

    @property
    def routes_failed(self) -> int:
        return sum(1 for route in self.routes if not route.ok)

    @property
    def changed(self) -> bool:
        return bool(self.snapped or self.moved)

    def as_dict(self) -> dict:
        return {
            "folio": self.folio,
            "title": self.title,
            "snapped": self.snapped,
            "moved": [
                {"id": mid, "from": list(old), "to": list(new)}
                for mid, old, new in self.moved
            ],
            "kept_locked": list(self.kept_locked),
            "unresolved": list(self.unresolved),
            "routes_ok": self.routes_ok,
            "routes_failed": self.routes_failed,
            "routes": [route.as_dict() for route in self.routes],
        }


@dataclass
class LayoutOutcome:
    """Resultado global del pipeline."""

    project: Project
    folios: list[FolioResult] = field(default_factory=list)

    @property
    def moved_count(self) -> int:
        return sum(len(folio.moved) for folio in self.folios)

    @property
    def snapped_count(self) -> int:
        return sum(folio.snapped for folio in self.folios)

    @property
    def locked_count(self) -> int:
        return sum(len(folio.kept_locked) for folio in self.folios)

    @property
    def unresolved(self) -> list[str]:
        return [cid for folio in self.folios for cid in folio.unresolved]

    @property
    def routes_ok(self) -> int:
        return sum(folio.routes_ok for folio in self.folios)

    @property
    def routes_failed(self) -> int:
        return sum(folio.routes_failed for folio in self.folios)

    @property
    def ok(self) -> bool:
        """``True`` si no quedó nada sin resolver ni rutas sin trazar."""
        return not self.unresolved and not self.routes_failed

    def summary(self) -> str:
        """Resumen de una línea."""
        return (f"Layout: {self.moved_count} movido(s), "
                f"{self.snapped_count} alineado(s), "
                f"{self.locked_count} bloqueado(s), "
                f"{self.routes_ok}/{self.routes_ok + self.routes_failed} ruta(s) OK")

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "summary": self.summary(),
            "moved": self.moved_count,
            "snapped": self.snapped_count,
            "locked": self.locked_count,
            "routes_ok": self.routes_ok,
            "routes_failed": self.routes_failed,
            "unresolved": self.unresolved,
            "folios": [folio.as_dict() for folio in self.folios],
        }


def snap_sheet(sheet: Sheet, grid: Grid, *, respect_locked: bool = True,
               snap_texts: bool = False) -> int:
    """Cuantiza a la rejilla las coordenadas de un folio.

    Devuelve el número de elementos movidos. Los elementos con
    ``locked: true`` no se tocan (salvo que se pida explícitamente lo
    contrario con ``respect_locked=False``).
    """
    moved = 0
    for component in sheet.elements:
        if respect_locked and component.locked:
            continue
        x, y = grid.snap_point(component.x, component.y)
        if x != component.x or y != component.y:
            component.x = x
            component.y = y
            moved += 1
    if snap_texts:
        for text in sheet.texts:
            if respect_locked and text.locked:
                continue
            x, y = grid.snap_point(text.x, text.y)
            if x != text.x or y != text.y:
                text.x = x
                text.y = y
                moved += 1
    return moved


def apply_layout(project: Project, catalog: SymbolCatalog,
                 config: QetGenConfig | None = None,
                 options: LayoutOptions | None = None) -> LayoutOutcome:
    """Aplica el pipeline de layout a un proyecto y devuelve el informe.

    El proyecto original **no** se modifica: se trabaja sobre una copia.
    """
    if config is None:
        from ..config import QetGenConfig as _Config
        config = _Config()
    if options is None:
        options = LayoutOptions()

    working = project.model_copy(deep=True)
    grid = Grid(size=config.layout.grid_size, enabled=config.layout.snap_to_grid)
    outcome = LayoutOutcome(project=working)

    for index, sheet in enumerate(working.folios, start=1):
        if options.folio is not None and index != options.folio:
            continue
        result = FolioResult(folio=index, title=sheet.title or f"Folio {index}")
        fmt = get_sheet_format(sheet.sheet_format)
        safe = fmt.drawing_area.inset(config.sheet.margin)

        if options.snap:
            result.snapped = snap_sheet(
                sheet, grid, respect_locked=options.respect_locked,
                snap_texts=options.snap_texts)

        if options.auto_layout:
            sheet, report = auto_layout(
                sheet, catalog, grid, safe,
                respect_locked=options.respect_locked,
                column_gap=config.layout.column_gap,
                row_gap=config.layout.row_gap,
                clearance=config.layout.clearance,
                margin=config.sheet.margin)
            result.moved = list(report.moved)
            result.kept_locked = list(report.kept_locked)
            result.unresolved = list(report.unresolved)

        if options.route and config.layout.route_manhattan:
            sheet, results = route_sheet(
                sheet, catalog, grid, safe,
                turn_penalty=config.layout.turn_penalty,
                crossing_penalty=config.layout.crossing_penalty,
                min_separation=config.layout.min_separation,
                max_nodes=config.layout.max_search_nodes,
                clearance=config.layout.route_clearance,
                route_manhattan=True)
            result.routes = list(results)

        working.folios[index - 1] = sheet
        outcome.folios.append(result)

    return outcome


__all__ = [
    "FolioResult",
    "LayoutOptions",
    "LayoutOutcome",
    "apply_layout",
    "snap_sheet",
]
