"""layout/__init__.py — Motor geométrico de qetgen.

Capas del motor, de la más pura a la más aplicada:

``grid``
    Cuadrícula de alineación (*snap-to-grid*).
``placement``
    Geometría de colocación: cajas reales de símbolos, terminales rotadas,
    cajas de texto.
``collision``
    Detección de solapes distinguiendo contención intencional.
``textmetrics``
    Métrica tipográfica aproximada pero reproducible.
``labels``
    Colocación de etiquetas junto a los símbolos.
``router``
    Routing ortogonal Manhattan con A*.
``autolayout``
    Reubicación automática en modo híbrido (``locked``).
"""

from .autolayout import LayoutReport, auto_layout, compute_layers
from .collision import (Collision, CollisionReport, Occupant, analyze_sheet,
                        detect_collisions, overlap_area, sheet_occupants)
from .grid import Grid
from .labels import CANDIDATE_SIDES, PlacedLabel, place_labels
from .pipeline import (FolioResult, LayoutOptions, LayoutOutcome, apply_layout,
                       snap_sheet)
from .placement import (component_bounds, component_ink_bounds,
                        component_label_bounds, label_bounds, shape_bounds,
                        terminal_direction, terminal_position, transform_box)
from .router import ManhattanRouter, RouteResult, route_sheet
from .textmetrics import TextBox, TextMeasurer

__all__ = [
    "CANDIDATE_SIDES",
    "Collision",
    "CollisionReport",
    "FolioResult",
    "Grid",
    "LayoutOptions",
    "LayoutOutcome",
    "LayoutReport",
    "ManhattanRouter",
    "Occupant",
    "PlacedLabel",
    "RouteResult",
    "TextBox",
    "TextMeasurer",
    "analyze_sheet",
    "apply_layout",
    "auto_layout",
    "component_bounds",
    "component_ink_bounds",
    "component_label_bounds",
    "compute_layers",
    "detect_collisions",
    "label_bounds",
    "overlap_area",
    "place_labels",
    "route_sheet",
    "shape_bounds",
    "snap_sheet",
    "sheet_occupants",
    "terminal_direction",
    "terminal_position",
    "transform_box",
]
