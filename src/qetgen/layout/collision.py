"""layout/collision.py — Detección de colisiones con cajas envolventes reales.

Reglas del proyecto (fundamentales para no producir falsos positivos):

1. La caja de un símbolo es la **caja declarada por su ``.elmt``**
   (``width``×``height`` con el hotspot en ``hotspot_x``/``hotspot_y``),
   verificada como envolvente de todas las primitivas reales del símbolo.
   Se rota según ``orientation`` (0..3 = 0°, 90°, 180°, 270°).
2. La caja de un texto se **mide** con :mod:`layout.textmetrics`.
3. **Contención ≠ solape**: un texto dentro de un bloque, o un panel dentro de
   un marco, es una composición intencional y no se reporta. Solo se reporta
   el solape **parcial** (dos cajas que se cruzan sin que una contenga a la
   otra).
4. Los bloques con papel ``background`` o ``decoration`` son puramente
   decorativos: nunca generan avisos.

Cada colipse detectada es un :class:`Collision` con mensaje **accionable**
(elementos implicatedados, caja, severidad y qué hacer).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.catalog import SymbolCatalog
from ..core.geometry import BBox
from ..core.models import Sheet
from .placement import (component_bounds, component_ink_bounds,
                        component_label_bounds, label_bounds, shape_bounds,
                        transform_box)
from .textmetrics import TextMeasurer

#: Papeles de bloque que nunca generan colisiones.
_NON_COLLIDING_ROLES = frozenset({"background", "decoration"})

#: Tolerancia (px) para considerar que dos cajas se tocan sin solaparse.
_EPS = 1e-6


# --------------------------------------------------------------------------
# Construcción de cajas
# --------------------------------------------------------------------------
# Las funciones viven en layout/placement.py (fuente única de verdad):
#   transform_box, component_bounds, component_label_bounds,
#   label_bounds, shape_bounds
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Ocupantes
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Occupant:
    """Objeto con caja que participa en los tests de colisión."""

    key: str
    kind: str                     # "component" | "label" | "text" | "shape"
    box: BBox
    role: str = ""                # papel del bloque (solo kind == "shape")
    label: str = ""               # descripción legible

    @property
    def collidable(self) -> bool:
        """``False`` para los bloques puramente decorativos."""
        return not (self.kind == "shape" and self.role in _NON_COLLIDING_ROLES)


@dataclass(frozen=True)
class Collision:
    """Colisión detectada entre dos objetos del folio."""

    kind: str
    a: str
    b: str
    box: BBox
    area: float
    severity: str = "warning"      # "error" | "warning"
    detail: str = ""
    suggestion: str = ""

    @property
    def message(self) -> str:
        """Mensaje accionable (una línea)."""
        base = (f"{self.kind}: {self.a} ↔ {self.b} "
                f"(solape {self.area:.0f} px²)")
        if self.detail:
            base += f" — {self.detail}"
        return base

    def as_dict(self) -> dict:
        """Representación serializable (CLI JSON / MCP)."""
        return {
            "kind": self.kind,
            "a": self.a,
            "b": self.b,
            "box": list(self.box.as_tuple()),
            "area": round(self.area, 2),
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
        }


# --------------------------------------------------------------------------
# Tests geométricos
# --------------------------------------------------------------------------

def overlap_area(a: BBox, b: BBox) -> float:
    """Área de intersección **excluyendo la contención** y el simple contacto.

    Contención ≠ solape: un texto dentro de un bloque, o un panel dentro de
    un marco, es una composición intencional. La única excepción son las
    cajas **idénticas**: dos objetos montados exactamente en el mismo sitio
    sí se solapan por completo (en cajas alineadas a ejes, contención con
    la misma área implica identidad).
    """
    contained = a.contains(b) or b.contains(a)
    if contained and abs(a.area - b.area) > _EPS:
        return 0.0
    w = min(a.x2, b.x2) - max(a.x1, b.x1)
    h = min(a.y2, b.y2) - max(a.y1, b.y1)
    if w <= _EPS or h <= _EPS:
        return 0.0
    return w * h


def _pair_kind(kind_a: str, kind_b: str) -> str:
    """Nombre canónico del tipo de colisión."""
    order = ["component", "label", "text", "shape"]
    pair = sorted((kind_a, kind_b), key=lambda k: order.index(k) if k in order else 99)
    return "-".join(pair)


def _is_self_label(first: Occupant, second: Occupant) -> bool:
    """``True`` si un par es (símbolo, etiqueta de ese mismo símbolo)."""
    if first.kind == "label" and second.kind == "component":
        return first.key.rsplit(":label", 1)[0] == second.key
    if second.kind == "label" and first.kind == "component":
        return second.key.rsplit(":label", 1)[0] == first.key
    return False


def detect_collisions(occupants: list[Occupant]) -> list[Collision]:
    """Detecta colisiones reales entre los ocupantes de un folio.

    Severidad:

    * ``error``   → dos **símbolos** se solapan (nunca es intencionado).
    * ``warning`` → textos que se pisan, o una etiqueta que se monta sobre
      otro objeto.
    * ``info``    → composición: un símbolo cruza el borde de un bloque.

    Dos objetos quedan **excluidos** del análisis cuando la relación es
    inherente al diseño: la etiqueta de un símbolo contra su propio símbolo,
    y un texto contra un bloque funcional (los títulos de bloque se apoyan
    sobre el borde por estilo de dibujo).
    """
    collisions: list[Collision] = []
    active = [occ for occ in occupants if occ.collidable]
    for i, first in enumerate(active):
        for second in active[i + 1:]:
            if _is_self_label(first, second):
                continue          # la etiqueta de un símbolo no choca consigo mismo

            if first.kind == "shape" and second.kind == "shape":
                # Dos bloques que se cruzan: aviso (p. ej. cabecera sobre tabla).
                area = overlap_area(first.box, second.box)
                if area > 0:
                    collisions.append(Collision(
                        kind="shape-shape", a=first.label or first.key,
                        b=second.label or second.key, box=first.box, area=area,
                        severity="warning",
                        detail="dos bloques se cruzan sin containment",
                        suggestion="anida un bloque dentro del otro o separa sus bordes",
                    ))
                continue

            if first.kind == "shape" or second.kind == "shape":
                shape = first if first.kind == "shape" else second
                other = second if first.kind == "shape" else first
                if other.kind == "text":
                    continue      # composición: títulos apoyados en el borde
                area = overlap_area(shape.box, other.box)
                if area > 0:
                    collisions.append(Collision(
                        kind=f"{other.kind}-shape", a=other.label or other.key,
                        b=shape.label or shape.key, box=other.box, area=area,
                        severity="info",
                        detail=f"el objeto cruza el borde del bloque ({shape.role})",
                        suggestion=("mueve el objeto dentro del bloque o "
                                    "redimensiona el bloque"),
                    ))
                continue

            area = overlap_area(first.box, second.box)
            if area <= 0:
                continue
            kind = _pair_kind(first.kind, second.kind)
            if first.kind == "component" and second.kind == "component":
                severity = "error"
                suggestion = ("separa los símbolos (mueve el componente o "
                              "activa locked para fijar su posición)")
            else:
                severity = "warning"
                suggestion = ("ajusta la posición del texto o del símbolo para "
                              "dejar al menos el margen de separación configurado")
            collisions.append(Collision(
                kind=kind, a=first.label or first.key, b=second.label or second.key,
                box=first.box, area=area, severity=severity,
                detail="las cajas se cruzan parcialmente",
                suggestion=suggestion,
            ))
    return collisions


# --------------------------------------------------------------------------
# Construcción de los ocupantes de un folio
# --------------------------------------------------------------------------

def sheet_occupants(sheet: Sheet, catalog: SymbolCatalog,
                    measurer: TextMeasurer,
                    include_labels: bool = True) -> list[Occupant]:
    """Construye la lista de ocupantes de un folio."""
    occupants: list[Occupant] = []
    for component in sheet.elements:
        if not catalog.has(component.type):
            continue
        symbol = catalog.get(component.type)
        occupants.append(Occupant(
            key=component.id, kind="component",
            box=component_ink_bounds(component, symbol),
            label=f"{component.id} ({component.type})",
        ))
        if include_labels:
            label_text = component.resolved_label()
            if label_text:
                occupants.append(Occupant(
                    key=f"{component.id}:label", kind="label",
                    box=component_label_bounds(component, symbol, measurer),
                    label=f"etiqueta de {component.id}",
                ))
    for index, text in enumerate(sheet.texts):
        occupants.append(Occupant(
            key=f"texto[{index}]", kind="text", box=label_bounds(text, measurer),
            label=f"texto[{index}] “{text.text[:24]}”",
        ))
    for index, shape in enumerate(sheet.shapes):
        occupants.append(Occupant(
            key=f"bloque[{index}]", kind="shape", box=shape_bounds(shape),
            role=shape.role, label=f"bloque[{index}] ({shape.role})",
        ))
    return occupants


@dataclass
class CollisionReport:
    """Resultado del análisis de colisiones de un folio."""

    collisions: list[Collision] = field(default_factory=list)
    occupants: int = 0

    @property
    def errors(self) -> list[Collision]:
        return [c for c in self.collisions if c.severity == "error"]

    @property
    def warnings(self) -> list[Collision]:
        return [c for c in self.collisions if c.severity == "warning"]

    @property
    def ok(self) -> bool:
        """``True`` si no hay colisiones de severidad ``error``."""
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "occupants": self.occupants,
            "errors": [c.as_dict() for c in self.errors],
            "warnings": [c.as_dict() for c in self.warnings],
        }


def analyze_sheet(sheet: Sheet, catalog: SymbolCatalog,
                  measurer: TextMeasurer,
                  include_labels: bool = True) -> CollisionReport:
    """Analiza las colisiones de un folio completo."""
    occupants = sheet_occupants(sheet, catalog, measurer, include_labels=include_labels)
    collisions = detect_collisions(occupants)
    return CollisionReport(collisions=collisions, occupants=len(occupants))


__all__ = [
    "Collision",
    "CollisionReport",
    "Occupant",
    "analyze_sheet",
    "component_bounds",
    "component_label_bounds",
    "detect_collisions",
    "label_bounds",
    "overlap_area",
    "shape_bounds",
    "sheet_occupants",
    "transform_box",
]
