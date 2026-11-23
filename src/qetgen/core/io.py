"""Entrada/salida del modelo en JSON.

Un **único** esquema canónico, validado con Pydantic:

.. code-block:: json

    {
      "project": { "title": "...", "author": "...", "filename": "..." },
      "diagrams": [
        { "title": "D-001", "order": 1,
          "elements":    [ {"id": "...", "type": "...", "x": 0, "y": 0} ],
          "connections": [ {"from": "...", "from_terminal": 0,
                            "to": "...", "to_terminal": 0} ],
          "texts":       [ {"x": 0, "y": 0, "text": "..."} ],
          "shapes":      [ {"x1": 0, "y1": 0, "x2": 10, "y2": 10} ] }
      ]
    }

Se mantiene la **compatibilidad del formato plano heredado** (v0.1):
``project`` + ``diagram`` + ``elements``/``connections``/``texts`` en la raíz,
que se transforma al esquema multi-folio antes de validarse.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .errors import SpecError
from .models import Component, Connection, Label, Project, Shape, Sheet

# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------

def _format_validation_error(exc: ValidationError, ctx: str) -> str:
    """Convierte los errores de Pydantic en mensajes accionables."""
    lines = [f"{ctx}: esquema inválido"]
    for issue in exc.errors():
        parts = []
        for part in issue.get("loc", ()):
            if isinstance(part, int):
                parts.append(f"[{part}]")
            elif parts:
                parts.append(f".{part}")
            else:
                parts.append(str(part))
        location = "".join(parts) or "(raíz)"
        message = issue.get("msg", "valor inválido")
        lines.append(f"  - {location}: {message}")
    return "\n".join(lines)


def _legacy_flat_to_multi(data: dict) -> dict:
    """Convierte el formato plano heredado (v0.1) al esquema multi-folio."""
    diagram = data.get("diagram") or {}
    if not isinstance(diagram, dict):
        raise SpecError("'diagram' debe ser un objeto")
    folio = {
        "title": diagram.get("title", ""),
        "author": diagram.get("author", ""),
        "indexrev": diagram.get("indexrev", "A"),
        "date": diagram.get("date"),
        "order": diagram.get("order", 1),
        "elements": data.get("elements") or [],
        "connections": data.get("connections") or [],
        "texts": data.get("texts") or [],
        "shapes": data.get("shapes") or [],
    }
    return {"project": data.get("project") or {}, "diagrams": [folio]}


def project_from_dict(data: dict) -> Project:
    """Construye un :class:`Project` desde un diccionario ya leído.

    Aplica el esquema estricto y convierte los errores de validación en
    :class:`SpecError` con el camino exacto del campo problemático.
    """
    if not isinstance(data, dict):
        raise SpecError("El documento JSON debe ser un objeto")
    if "project" not in data:
        raise SpecError("Falta la clave 'project' en la raíz del documento")
    if "diagrams" not in data:
        data = _legacy_flat_to_multi(data)

    # `project` se valida por separado para dar un error más claro.
    project_raw = data.get("project")
    if not isinstance(project_raw, dict):
        raise SpecError("'project' debe ser un objeto")

    diagrams_raw = data.get("diagrams")
    if not isinstance(diagrams_raw, list):
        raise SpecError("'diagrams' debe be una lista de folios")

    sheets: list[Sheet] = []
    for i, raw in enumerate(diagrams_raw, start=1):
        if not isinstance(raw, dict):
            raise SpecError(f"diagrams[{i}] debe ser un objeto")
        try:
            sheets.append(Sheet(**raw))
        except ValidationError as exc:
            raise SpecError(_format_validation_error(exc, f"diagrams[{i}]")) from exc

    payload = dict(project_raw)
    payload["folios"] = sheets
    try:
        return Project(**payload)
    except ValidationError as exc:
        raise SpecError(_format_validation_error(exc, "project")) from exc


def load_spec(path: str | Path) -> Project:
    """Lee y valida un JSON de especificación desde disco."""
    path = Path(path)
    if not path.is_file():
        raise SpecError(f"No existe el archivo: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SpecError(f"No se pudo leer {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecError(f"JSON mal formado en {path}: {exc}") from exc
    return project_from_dict(data)


# --------------------------------------------------------------------------
# Serialización (canónica y simétrica con la carga)
# --------------------------------------------------------------------------

def component_to_dict(component: Component) -> dict:
    """Serializa un componente omitiendo los valores por defecto."""
    out: dict[str, Any] = {
        "id": component.id,
        "type": component.type,
        "x": component.x,
        "y": component.y,
    }
    if component.label is not None:
        out["label"] = component.label
    if component.orientation:
        out["orientation"] = component.orientation
    if component.info:
        out["info"] = dict(component.info)
    if component.locked:
        out["locked"] = True
    return out


def connection_to_dict(connection: Connection) -> dict:
    """Serializa una conexión."""
    out: dict[str, Any] = {
        "from": connection.from_id,
        "from_terminal": connection.from_terminal,
        "to": connection.to_id,
        "to_terminal": connection.to_terminal,
    }
    if connection.kind != "cable":
        out["kind"] = connection.kind
    if connection.number:
        out["number"] = connection.number
    if connection.locked:
        out["locked"] = True
    return out


def label_to_dict(label: Label) -> dict:
    """Serializa un texto independiente."""
    out: dict[str, Any] = {"x": label.x, "y": label.y, "text": label.text}
    if label.size != 9:
        out["size"] = label.size
    if label.rotation:
        out["rotation"] = label.rotation
    if label.align != "left":
        out["align"] = label.align
    if label.locked:
        out["locked"] = True
    return out


def shape_to_dict(shape: Shape) -> dict:
    """Serializa un bloque funcional."""
    out: dict[str, Any] = {
        "x1": shape.x1, "y1": shape.y1, "x2": shape.x2, "y2": shape.y2,
    }
    if shape.fill:
        out["fill"] = shape.fill
    if shape.dash:
        out["dash"] = True
    if shape.color != "#004080":
        out["color"] = shape.color
    if shape.width != 1.0:
        out["width"] = shape.width
    if shape.title:
        out["title"] = shape.title
    if shape.role != "group":
        out["role"] = shape.role
    if shape.locked:
        out["locked"] = True
    return out


def sheet_to_dict(sheet: Sheet) -> dict:
    """Serializa un folio completo (simétrico con :class:`Sheet`)."""
    out: dict[str, Any] = {
        "title": sheet.title,
        "order": sheet.order,
        "elements": [component_to_dict(el) for el in sheet.elements],
        "connections": [connection_to_dict(cn) for cn in sheet.connections],
        "texts": [label_to_dict(tx) for tx in sheet.texts],
        "shapes": [shape_to_dict(sh) for sh in sheet.shapes],
    }
    if sheet.author:
        out["author"] = sheet.author
    if sheet.indexrev != "A":
        out["indexrev"] = sheet.indexrev
    if sheet.date:
        out["date"] = sheet.date
    if sheet.sheet_format != "A3_17x8":
        out["sheet_format"] = sheet.sheet_format
    return out


def project_to_dict(project: Project) -> dict:
    """Serializa el proyecto completo al esquema canónico."""
    project_out: dict[str, Any] = {"title": project.title}
    if project.author:
        project_out["author"] = project.author
    if project.filename:
        project_out["filename"] = project.filename
    if project.library_path:
        project_out["library_path"] = project.library_path
    return {
        "project": project_out,
        "diagrams": [sheet_to_dict(sheet) for sheet in project.folios],
    }


def save_spec(project: Project, path: str | Path) -> Path:
    """Escribe el proyecto como JSON (UTF-8, sin BOM, con saltos ``\\n``)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = project_to_dict(project)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


__all__ = [
    "component_to_dict",
    "connection_to_dict",
    "label_to_dict",
    "load_spec",
    "project_from_dict",
    "project_to_dict",
    "save_spec",
    "sheet_to_dict",
    "shape_to_dict",
]
