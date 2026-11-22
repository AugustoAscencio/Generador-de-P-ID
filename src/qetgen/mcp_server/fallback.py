"""mcp_server/fallback.py — Servidor MCP por ``stdio`` sin dependencias.

Si el SDK oficial ``mcp`` no está instalado, el servidor **sigue siendo
funcional**: este módulo implementa el transporte ``stdio`` del protocolo
MCP con la biblioteca estándar.

Formato: una petición JSON-RPC 2.0 **por línea** (JSON Lines) por la entrada
estándar; una respuesta JSON por línea por la salida estándar. Es el mismo
formato que usa el SDK oficial, así que un cliente MCP cualquiera funciona con
ambos transportes.

Ventaja: ``pip install qetgen`` sin extras ya da un servidor MCP usable;
instalando ``qetgen[mcp]`` se usa el SDK oficial (con su gestión de
capacidades y registros).
"""

from __future__ import annotations

import json
import sys
from typing import TextIO

from .. import __version__
from .dispatch import Dispatcher, handle_line
from .session import Session


def serve_stdio(session: Session | None = None,
                stdin: TextIO | None = None,
                stdout: TextIO | None = None) -> int:
    """Bucle del servidor MCP por ``stdio`` (JSON Lines).

    Lee peticiones de ``stdin`` y escribe las respuestas en ``stdout``.
    Devuelve el número de peticiones atendidas.
    """
    dispatcher = Dispatcher(session or Session(), server_version=__version__)
    source = stdin if stdin is not None else sys.stdin
    sink = stdout if stdout is not None else sys.stdout
    handled = 0

    for line in source:
        line = line.strip()
        if not line:
            continue
        response = handle_line(dispatcher, line)
        if response is None:
            continue
        sink.write(json.dumps(response, ensure_ascii=False) + "\n")
        sink.flush()
        handled += 1
    return handled


__all__ = ["serve_stdio"]
