"""Primitivas geométricas puras (sin dependencias).

Viven en ``core`` porque el catálogo de símbolos necesita conocer la caja
del símbolo (para validar colisiones) y ``layout`` construye sobre ellas.
La dirección de dependencias es siempre ``core`` → ``layout``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Vec2:
    """Punto 2D en píxeles de folio."""

    x: float
    y: float

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def distance_to(self, other: "Vec2") -> float:
        """Distancia euclídea."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def manhattan_to(self, other: "Vec2") -> float:
        """Distancia Manhattan (L1) — la métrica natural del routing ortogonal."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


@dataclass(frozen=True)
class BBox:
    """Caja rectangular alineada a ejes (AABB), en píxeles de folio.

    Inmutable: las transformaciones devuelven cajas nuevas.
    """

    x1: float
    y1: float
    x2: float
    y2: float

    # -- construcción ------------------------------------------------------

    @classmethod
    def from_points(cls, points: list[tuple[float, float]]) -> "BBox | None":
        """Caja envolvente de un conjunto de puntos; ``None`` si está vacío."""
        if not points:
            return None
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return cls(min(xs), min(ys), max(xs), max(ys))

    @classmethod
    def from_size(cls, x: float, y: float, width: float, height: float) -> "BBox":
        """Caja desde un origen y un tamaño (con centro en el origen)."""
        return cls(x - width / 2.0, y - height / 2.0, x + width / 2.0, y + height / 2.0)

    # -- consultas ---------------------------------------------------------

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def center(self) -> Vec2:
        return Vec2((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)

    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    def contains_point(self, x: float, y: float) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def contains(self, other: "BBox") -> bool:
        """``True`` si ``other`` está completamente dentro de esta caja."""
        return (other.x1 >= self.x1 and other.y1 >= self.y1
                and other.x2 <= self.x2 and other.y2 <= self.y2)

    def intersects(self, other: "BBox", margin: float = 0.0) -> bool:
        """Intersección con margen de holgura (``margin`` en px)."""
        return not (
            self.x2 + margin < other.x1
            or other.x2 + margin < self.x1
            or self.y2 + margin < other.y1
            or other.y2 + margin < self.y1
        )

    def overlap_area(self, other: "BBox") -> float:
        """Área solapada con otra caja (0 si no se tocan)."""
        w = min(self.x2, other.x2) - max(self.x1, other.x1)
        h = min(self.y2, other.y2) - max(self.y1, other.y1)
        if w <= 0 or h <= 0:
            return 0.0
        return w * h

    # -- transformaciones --------------------------------------------------

    def translated(self, dx: float, dy: float) -> "BBox":
        return BBox(self.x1 + dx, self.y1 + dy, self.x2 + dx, self.y2 + dy)

    def inflated(self, margin: float) -> "BBox":
        """Caja ampliada (margen positivo) o reducida (margen negativo)."""
        return BBox(self.x1 - margin, self.y1 - margin,
                    self.x2 + margin, self.y2 + margin)

    def inset(self, margin: float) -> "BBox":
        """Caja **reducida** un margen interior (margen negativo = expande).

        Es la operación de "encoger hacia dentro", simétrica a
        :meth:`inflated`, para dejar claro el sentido del signo.
        """
        return BBox(self.x1 + margin, self.y1 + margin,
                    self.x2 - margin, self.y2 - margin)

    def clipped_to(self, bounds: "BBox") -> "BBox":
        """Caja recortada a otra caja (para limitar a la zona segura)."""
        return BBox(max(self.x1, bounds.x1), max(self.y1, bounds.y1),
                    min(self.x2, bounds.x2), min(self.y2, bounds.y2))

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x1, self.y1, self.x2, self.y2)


__all__ = ["Vec2", "BBox"]
