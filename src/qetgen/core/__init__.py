"""Núcleo del dominio: modelos estrictos, catálogo, geometría y E/S.

No depende de XML, ni de QElectroTech, ni de la capa de presentación.
"""

from .catalog import SymbolCatalog, SymbolDefinition
from .errors import (CatalogError, GeometryError, QetGenError, SpecError,
                     ValidationError)
from .geometry import BBox, Vec2
from .io import (load_spec, project_from_dict, project_to_dict, save_spec,
                 sheet_to_dict)
from .models import (Connection, Component, Label, Port, Project, Shape, Sheet,
                     component, connection, label, shape)
from .sheet import SHEET_FORMATS, SheetFormat, get_sheet_format

__all__ = [
    "BBox",
    "CatalogError",
    "Component",
    "Connection",
    "GeometryError",
    "Label",
    "Port",
    "Project",
    "QetGenError",
    "SHEET_FORMATS",
    "Shape",
    "Sheet",
    "SheetFormat",
    "SpecError",
    "SymbolCatalog",
    "SymbolDefinition",
    "ValidationError",
    "Vec2",
    "component",
    "connection",
    "get_sheet_format",
    "label",
    "load_spec",
    "project_from_dict",
    "project_to_dict",
    "save_spec",
    "shape",
    "sheet_to_dict",
]
