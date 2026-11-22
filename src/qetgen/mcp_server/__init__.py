"""mcp_server/ — Servidor MCP universal de qetgen.

Expone el motor de documentación eléctrica como **herramientas MCP** por
``stdio``:

* 8 herramientas atómicas y tipadas (``crear_diagrama``, ``listar_simbolos``,
  ``agregar_elemento``, ``conectar_elementos``, ``ejecutar_auto_layout``,
  ``validar_estetica``, ``obtener_resumen_canvas``, ``exportar_archivo``);
* 4 recursos (``qetgen://catalogo``, ``qetgen://config``,
  ``qetgen://formatos-hoja``, ``qetgen://proyecto``);
* 2 prompts (``system_prompt``, ``revisar_plano``).

Funciona con el **SDK oficial** de MCP si está instalado y con un **fallback
propio** (JSON-RPC 2.0) si no: la interfaz es la misma en ambos casos.
"""

from .dispatch import Dispatcher
from .prompts import PROMPTS, get_prompt, list_prompts
from .resources import RESOURCES, list_resources, read_resource
from .session import Session, ToolError
from .tools import TOOLS, TOOLS_BY_NAME, Tool, call_tool, list_tools

__all__ = [
    "PROMPTS",
    "RESOURCES",
    "TOOLS",
    "TOOLS_BY_NAME",
    "Dispatcher",
    "Session",
    "Tool",
    "ToolError",
    "call_tool",
    "get_prompt",
    "list_prompts",
    "list_resources",
    "list_tools",
    "read_resource",
]
