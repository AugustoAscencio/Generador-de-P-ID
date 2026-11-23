"""Exportadores: salida desacoplada de la lógica matemática.

Cada exportador consume el modelo del núcleo y produce un formato de salida.
Añadir un formato nuevo (DXF, HTML, PDF…) no toca ni el núcleo ni el motor
de layout.
"""

from .json import export_json, project_to_json
from .qet import build_project, export_project, export_qet
from .svg import export_project_svg, export_sheet_svg, sheet_to_svg

__all__ = [
    "build_project",
    "export_json",
    "export_project",
    "export_project_svg",
    "export_qet",
    "export_sheet_svg",
    "project_to_json",
    "sheet_to_svg",
]
