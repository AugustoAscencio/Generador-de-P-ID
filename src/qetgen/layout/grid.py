"""layout/grid.py — Cuadrícula de alineación (*snap-to-grid*).

La rejilla de QElectroTech (``colsize``/``rowsize``) es **metadato de
presentación** del folio: QET la dibuja, pero no la usa para mover nada.
Este módulo es una rejilla de trabajo propia del motor, configurable desde
``config/default.yaml`` (``layout.grid_size``), independiente de la rejilla
visual de QET.

Regla de oro: el *snap* **nunca** mueve un elemento ``locked: true`` ni
altera la semántica del plano; solo cuantiza coordenadas para que el
resultado sea reproducible y legible.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..core.geometry import BBox


@dataclass(frozen=True)
class Grid:
    """Rejilla ortogonal de paso ``size`` píxeles."""

    size: float = 10.0
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.size <= 0:
            raise ValueError(f"el paso de la cuadrícula debe ser > 0 (recibido {self.size})")

    # -- cuantización -------------------------------------------------------

    def snap(self, value: float) -> float:
        """Cuantiza ``value`` al múltiplo de ``size`` más cercano."""
        if not self.enabled:
            return float(value)
        steps = round(float(value) / self.size)
        snapped = steps * self.size
        # Evita ruido binario (300.00000000000006 → 300.0).
        if abs(snapped - round(snapped)) < 1e-9:
            return float(round(snapped))
        return snapped

    def snap_x(self, x: float) -> float:
        """Cuantiza la coordenada X."""
        return self.snap(x)

    def snap_y(self, y: float) -> float:
        """Cuantiza la coordenada Y."""
        return self.snap(y)

    def snap_point(self, x: float, y: float) -> tuple[float, float]:
        """Cuantiza un punto completo."""
        return (self.snap_x(x), self.snap_y(y))

    def snap_box(self, box: BBox) -> BBox:
        """Cuantiza las esquinas de una caja (expansión al alza)."""
        if not self.enabled:
            return box
        return BBox(min(self.snap(box.x1), self.snap(box.x2)),
                    min(self.snap(box.y1), self.snap(box.y2)),
                    max(self.snap(box.x1), self.snap(box.x2)),
                    max(self.snap(box.y1), self.snap(box.y2)))

    # -- consultas ----------------------------------------------------------

    def is_aligned(self, value: float) -> bool:
        """``True`` si ``value`` ya cae en la rejilla."""
        if not self.enabled:
            return True
        remainder = abs(float(value) / self.size - round(float(value) / self.size))
        return remainder < 1e-6

    def is_box_aligned(self, box: BBox) -> bool:
        """``True`` si las cuatro esquinas de la caja están alineadas."""
        return (self.is_aligned(box.x1) and self.is_aligned(box.y1)
                and self.is_aligned(box.x2) and self.is_aligned(box.y2))

    def offset(self, value: float) -> float:
        """Distancia (con signo) de ``value`` al múltiplo de rejilla más cercano."""
        return float(value) - self.snap(value)

    def index(self, value: float) -> int:
        """Índice de celda de la rejilla que contiene ``value``."""
        return int(math.floor(float(value) / self.size))

    def cells(self, bounds: BBox):
        """Itera los índices de celda (``ix, iy``) que caen dentro de ``bounds``."""
        x0, x1 = self.index(bounds.x1), self.index(bounds.x2)
        y0, y1 = self.index(bounds.y1), self.index(bounds.y2)
        for iy in range(y0, y1 + 1):
            for ix in range(x0, x1 + 1):
                yield (ix, iy)

    def point(self, ix: int, iy: int) -> tuple[float, float]:
        """Coordenada del nodo de rejilla ``(ix, iy)``."""
        return (ix * self.size, iy * self.size)


__all__ = ["Grid"]
