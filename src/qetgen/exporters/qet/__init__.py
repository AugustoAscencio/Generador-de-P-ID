"""Exportador QElectroTech (.qet)."""

from .xml import (DiagramBuildResult, QET_VERSION, build_conductor, build_diagram,
                  build_element, build_project, build_rectangle, build_text,
                  export_project, new_uuid, wrap_html)


def export_qet(project, catalog, output_path):
    """Construye y escribe un proyecto ``.qet`` en una sola llamada.

    Parameters
    ----------
    project : qetgen.core.models.Project
    catalog : qetgen.core.catalog.SymbolCatalog
    output_path : str | pathlib.Path

    Returns
    -------
    tuple[pathlib.Path, list[DiagramBuildResult]]
        Ruta escrita y resultados por folio.
    """
    from pathlib import Path

    root, results = build_project(project, catalog)
    path = export_project(root, output_path)
    return Path(path), results


__all__ = [
    "DiagramBuildResult",
    "QET_VERSION",
    "build_conductor",
    "build_diagram",
    "build_element",
    "build_project",
    "build_rectangle",
    "build_text",
    "export_project",
    "export_qet",
    "new_uuid",
    "wrap_html",
]
