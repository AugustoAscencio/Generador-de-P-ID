"""model — Fachada de compatibilidad (deprecated → ``qetgen.core.models``).

> **Deprecated:** use ``qetgen.core.models`` / ``qetgen.core.io``.
"""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.legacy import (KNOWN_INFO_KEYS, Component, Connection, ElementSpec,
                           ConnectionSpec, FolioSpec, Label, Port, Project,
                           ProjectSpec, Shape, ShapeSpec, Sheet, SpecError,
                           TextSpec, load_spec, project_from_dict,
                           project_to_dict, save_spec)

__all__ = [
    "KNOWN_INFO_KEYS",
    "Component",
    "Connection",
    "ConnectionSpec",
    "ElementSpec",
    "FolioSpec",
    "Label",
    "Port",
    "Project",
    "ProjectSpec",
    "Shape",
    "ShapeSpec",
    "Sheet",
    "SpecError",
    "TextSpec",
    "load_spec",
    "project_from_dict",
    "project_to_dict",
    "save_spec",
]
