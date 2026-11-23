"""Capa de compatibilidad con la API v0.1.

Permite que el código escrito contra ``qet_generator`` (v0.1) siga
funcionando mientras el motor vive en :mod:`qetgen`. Los alias son
**re-exportaciones reales**, no copias: no hay dos modelos que puedan
divergir.

.. code-block:: python

    from qetgen.legacy import ElementSpec, FolioSpec, ProjectSpec, load_spec

Uso previsto: la v0.1 queda congelada y este módulo se elimina en la v2.0.
"""

from __future__ import annotations

from ..core.catalog import INSTANCE_FONT, ORIENTATION_LETTER_TO_NUM, SymbolCatalog, SymbolDefinition
from ..core.errors import CatalogError, SpecError
from ..core.geometry import BBox, Vec2
from ..core.io import (
    component_to_dict,
    connection_to_dict,
    label_to_dict,
    load_spec,
    project_from_dict,
    project_to_dict,
    save_spec,
    shape_to_dict,
    sheet_to_dict,
)
from ..core.models import KNOWN_INFO_KEYS, Component, Connection, Label, Port, Project, Shape, Sheet
from ..core.sheet import SheetFormat, get_sheet_format
from ..exporters.qet import (
    DiagramBuildResult,
    build_conductor,
    build_diagram,
    build_element,
    build_project,
    build_rectangle,
    build_text,
    export_project,
    new_uuid,
    wrap_html,
)
from ..validation.structural import ValidationReport, validate_project, validate_spec

# -- Alias de los modelos v0.1 -------------------------------------------------
ElementSpec = Component
ConnectionSpec = Connection
TextSpec = Label
ShapeSpec = Shape
FolioSpec = Sheet
ProjectSpec = Project
TerminalInfo = Port


def folio_to_dict(folio: Sheet) -> dict:
    """Serializa un folio al esquema JSON canónico (simétrico con la carga)."""
    return sheet_to_dict(folio)


__all__ = [
    "BBox",
    "CatalogError",
    "Component",
    "Connection",
    "ConnectionSpec",
    "DiagramBuildResult",
    "ElementSpec",
    "FolioSpec",
    "INSTANCE_FONT",
    "KNOWN_INFO_KEYS",
    "Label",
    "ORIENTATION_LETTER_TO_NUM",
    "Port",
    "Project",
    "ProjectSpec",
    "Shape",
    "ShapeSpec",
    "Sheet",
    "SheetFormat",
    "SpecError",
    "SymbolCatalog",
    "SymbolDefinition",
    "TextSpec",
    "Vec2",
    "ValidationReport",
    "build_conductor",
    "build_diagram",
    "build_element",
    "build_project",
    "build_rectangle",
    "build_text",
    "component_to_dict",
    "connection_to_dict",
    "export_project",
    "folio_to_dict",
    "get_sheet_format",
    "label_to_dict",
    "load_spec",
    "new_uuid",
    "project_from_dict",
    "project_to_dict",
    "save_spec",
    "shape_to_dict",
    "sheet_to_dict",
    "validate_project",
    "validate_spec",
    "wrap_html",
]
