"""mcp_server/resources.py — Recursos MCP (lectura del contexto).

Los recursos son la vía por la que la IA **consulta** el estado del motor sin
inventar nada: el catálogo real de símbolos, la configuración vigente, el
formato del folio y el proyecto actual.

URI:

* ``qetgen://catalogo`` — catálogo de símbolos lógicos → ``.elmt``.
* ``qetgen://config`` — configuración central vigente.
* ``qetgen://formatos-hoja`` — presets de folio con su geometría.
* ``qetgen://proyecto`` — el proyecto en memoria, en JSON canónico.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from ..core.io import project_to_dict
from ..core.sheet import SHEET_FORMATS
from .session import Session, ToolError

#: Tipo MIME de los recursos JSON.
MIME_JSON = "application/json"


@dataclass(frozen=True)
class Resource:
    """Recurso publicado por el servidor."""

    uri: str
    name: str
    description: str
    mime_type: str = MIME_JSON

    def as_dict(self) -> dict:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type,
        }


RESOURCES: list[Resource] = [
    Resource(
        uri="qetgen://catalogo",
        name="Catálogo de símbolos",
        description="Símbolos reales de la biblioteca de QElectroTech con "
                    "terminales y geometría."),
    Resource(
        uri="qetgen://config",
        name="Configuración vigente",
        description="Hoja, cuadrícula, tipografía, cableado y estilos."),
    Resource(
        uri="qetgen://formatos-hoja",
        name="Formatos de hoja",
        description="Presets de folio con su tamaño y zona segura."),
    Resource(
        uri="qetgen://proyecto",
        name="Proyecto actual",
        description="El proyecto en memoria, en JSON canónico."),
]

RESOURCES_BY_URI: dict[str, Resource] = {resource.uri: resource for resource in RESOURCES}


def list_resources() -> list[dict]:
    """Descripción de todos los recursos (formato MCP)."""
    return [resource.as_dict() for resource in RESOURCES]


def read_resource(session: Session, uri: str) -> dict:
    """Lee un recurso y devuelve su contenido (formato MCP)."""
    if uri not in RESOURCES_BY_URI:
        raise ToolError(
            f"Recurso desconocido: {uri!r}. "
            f"Disponibles: {', '.join(sorted(RESOURCES_BY_URI))}")

    if uri == "qetgen://catalogo":
        catalog = session.catalog
        if catalog is None:
            raise ToolError("El catálogo de símbolos no está cargado.")
        payload = {
            symbol.type_key: {
                "descripcion": symbol.description,
                "prefijo": symbol.prefix,
                "terminales": symbol.terminal_count,
                "caja_reservada": list(symbol.placement_bounds.as_tuple()),
                "caja_tinta": list(symbol.ink_bounds.as_tuple()),
                "posicion_etiqueta": list(symbol.label_pos),
            }
            for symbol in (catalog.get(key) for key in catalog.type_keys())
        }
    elif uri == "qetgen://config":
        if session.config is None:
            raise ToolError("La configuración no está cargada.")
        payload = session.config.to_dict()
    elif uri == "qetgen://formatos-hoja":
        payload = {name: fmt.to_dict() for name, fmt in SHEET_FORMATS.items()}
    else:   # qetgen://proyecto
        project = session.require_project()
        payload = project_to_dict(project)

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    return {
        "contents": [{
            "uri": uri,
            "mimeType": MIME_JSON,
            "text": text,
        }]
    }


__all__ = ["MIME_JSON", "RESOURCES", "RESOURCES_BY_URI", "Resource",
           "list_resources", "read_resource"]
