"""mcp_server/dispatch.py — Despacho JSON-RPC 2.0 (independiente del canal).

Este módulo implementa el **núcleo del protocolo**: traduce una petición
JSON-RPC a una acción sobre la sesión y devuelve la respuesta. Lo usan tanto
el servidor con el SDK oficial como el **fallback propio** por ``stdio``, de
modo que ambos se comportan exactamente igual.

Métodos implementados:

======================  ============================================
``initialize``          negociación de protocolo y capacidades
``notifications/*``     notificaciones (sin respuesta)
``ping``                comprobación de vida
``tools/list``          catálogo de herramientas
``tools/call``          ejecución de una herramienta
``resources/list``      catálogo de recursos
``resources/read``      lectura de un recurso
``prompts/list``        catálogo de prompts
``prompts/get``         obtaining de un prompt
======================  ============================================
"""

from __future__ import annotations

import json
from typing import Any

from .prompts import get_prompt, list_prompts
from .resources import list_resources, read_resource
from .session import Session, ToolError
from .tools import call_tool, list_tools

#: Protocolo MCP implementado.
PROTOCOL_VERSION = "2024-11-05"

#: Códigos de error JSON-RPC 2.0 usados.
ERROR_PARSE = -32700
ERROR_INVALID_REQUEST = -32600
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_PARAMS = -32602
ERROR_INTERNAL = -32603


def _result(request_id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str,
           data: Any = None) -> dict:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


class Dispatcher:
    """Traduce peticiones JSON-RPC a acciones sobre la sesión."""

    def __init__(self, session: Session | None = None,
                 server_version: str = "0.0.0"):
        self.session = session or Session()
        self.server_version = server_version
        self.initialized = False

    # -- utilidades ---------------------------------------------------------

    @staticmethod
    def _is_notification(request: dict) -> bool:
        return "id" not in request or request.get("id") is None

    @staticmethod
    def _server_info(dispatcher: "Dispatcher") -> dict:
        return {
            "name": "qetgen",
            "version": dispatcher.server_version,
            "title": "qetgen — documentación eléctrica QElectroTech",
        }

    # -- despacho -----------------------------------------------------------

    def handle(self, request: dict) -> dict | None:
        """Maneja una petición; devuelve ``None`` si era una notificación."""
        if not isinstance(request, dict):
            return _error(None, ERROR_INVALID_REQUEST,
                          "La petición debe ser un objeto JSON-RPC")
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params") or {}
        if not isinstance(params, dict):
            return _error(request_id, ERROR_INVALID_PARAMS,
                          "Los parámetros deben ser un objeto")

        if self._is_notification(request):
            # Las notificaciones no tienen respuesta (regla del protocolo).
            if method == "notifications/initialized":
                self.initialized = True
            return None

        try:
            result = self._dispatch(method, params)
        except ToolError as exc:
            return _error(request_id, ERROR_INVALID_PARAMS, str(exc))
        except KeyError as exc:
            return _error(request_id, ERROR_INVALID_PARAMS,
                          f"Falta el parámetro {exc}")
        except Exception as exc:       # pragma: no cover - red de seguridad
            return _error(request_id, ERROR_INTERNAL,
                          f"Error interno: {exc}", type(exc).__name__)
        return _result(request_id, result)

    def _dispatch(self, method: str | None, params: dict) -> dict:
        if method == "initialize":
            version = params.get("protocolVersion")
            protocol = version if isinstance(version, str) and version else PROTOCOL_VERSION
            return {
                "protocolVersion": protocol,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                    "logging": {},
                },
                "serverInfo": self._server_info(self),
                "instructions": (
                    "Servidor de documentación eléctrica QElectroTech. "
                    "Consulta 'system_prompt' para el flujo de trabajo."),
            }

        if method == "ping":
            return {}

        if method == "tools/list":
            return {"tools": list_tools()}

        if method == "tools/call":
            name = params.get("name")
            if not name:
                raise ToolError("Falta el nombre de la herramienta.")
            arguments = params.get("arguments") or {}
            try:
                payload = call_tool(self.session, name, arguments)
            except ToolError as exc:
                # Un error de herramienta es un resultado con isError, no un
                # error de protocolo: el cliente debe poder leer el mensaje.
                return {
                    "content": [{"type": "text", "text": str(exc)}],
                    "isError": True,
                }
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(payload, ensure_ascii=False, indent=2),
                }],
                "structuredContent": payload,
                "isError": False,
            }

        if method == "resources/list":
            return {"resources": list_resources()}

        if method == "resources/read":
            uri = params.get("uri")
            if not uri:
                raise ToolError("Falta el URI del recurso.")
            return read_resource(self.session, uri)

        if method == "prompts/list":
            return {"prompts": list_prompts()}

        if method == "prompts/get":
            name = params.get("name")
            if not name:
                raise ToolError("Falta el nombre del prompt.")
            return get_prompt(self.session, name, params.get("arguments") or {})

        raise ToolError(
            f"Método no soportado: {method!r}. "
            f"Métodos disponibles: initialize, ping, tools/list, tools/call, "
            f"resources/list, resources/read, prompts/list, prompts/get.")


def handle_line(dispatcher: Dispatcher, line: str) -> dict | None:
    """Interpreta una línea JSON-RPC y devuelve la respuesta (o ``None``)."""
    try:
        request = json.loads(line)
    except json.JSONDecodeError as exc:
        return _error(None, ERROR_PARSE, f"JSON inválido: {exc}")
    return dispatcher.handle(request)


__all__ = ["Dispatcher", "ERROR_INTERNAL", "ERROR_INVALID_PARAMS",
           "ERROR_INVALID_REQUEST", "ERROR_METHOD_NOT_FOUND", "ERROR_PARSE",
           "PROTOCOL_VERSION", "handle_line"]
