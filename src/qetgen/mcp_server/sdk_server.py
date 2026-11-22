"""mcp_server/sdk_server.py — Transporte con el SDK oficial de MCP.

Si el paquete ``mcp`` está instalado, el servidor usa su API (``Server`` +
``stdio_server``) para PubSub,协商 de protocolo y tipos oficiales. El
comportamiento observable (herramientas, recursos y prompts) es **idéntico**
al del fallback propio: ambos delegan en :mod:`qetgen.mcp_server.dispatch`.

Si el SDK no está disponible, la importación falla limpiamente y
:mod:`qetgen.mcp_server.main` arranca el fallback.
"""

from __future__ import annotations

import json

from .. import __version__
from .dispatch import Dispatcher
from .session import Session


def sdk_available() -> bool:
    """``True`` si el SDK oficial ``mcp`` está importable."""
    try:
        import mcp.types  # noqa: F401
        import mcp.server  # noqa: F401
    except ImportError:
        return False
    return True


def serve_sdk(session: Session | None = None) -> int:      # pragma: no cover
    """Arranca el servidor con el SDK oficial (requiere ``mcp`` instalado)."""
    import anyio
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server

    dispatcher = Dispatcher(session or Session(), server_version=__version__)
    server = Server("qetgen")

    @server.list_tools()
    async def _list_tools() -> list[types.Tool]:
        from .tools import list_tools
        return [
            types.Tool(
                name=tool["name"],
                title=tool.get("title", tool["name"]),
                description=tool["description"],
                inputSchema=tool["inputSchema"],
            )
            for tool in list_tools()
        ]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
        from .tools import call_tool
        try:
            payload = call_tool(dispatcher.session, name, arguments or {})
        except Exception as exc:
            return [types.TextContent(type="text", text=str(exc))]
        return [types.TextContent(
            type="text",
            text=json.dumps(payload, ensure_ascii=False, indent=2))]

    @server.list_resources()
    async def _list_resources() -> list[types.Resource]:
        from .resources import list_resources
        return [
            types.Resource(
                uri=resource["uri"],
                name=resource["name"],
                description=resource["description"],
                mimeType=resource["mimeType"],
            )
            for resource in list_resources()
        ]

    @server.read_resource()
    async def _read_resource(uri: Any) -> str:
        from .resources import read_resource
        payload = read_resource(dispatcher.session, str(uri))
        return payload["contents"][0]["text"]

    @server.list_prompts()
    async def _list_prompts() -> list[types.Prompt]:
        from .prompts import list_prompts
        return [
            types.Prompt(
                name=prompt["name"],
                title=prompt.get("title", prompt["name"]),
                description=prompt["description"],
                arguments=[],
            )
            for prompt in list_prompts()
        ]

    @server.get_prompt()
    async def _get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
        from .prompts import get_prompt
        payload = get_prompt(dispatcher.session, name, arguments or {})
        return types.GetPromptResult(
            description=payload.get("description", ""),
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=message["content"]["text"]),
                )
                for message in payload["messages"]
            ],
        )

    async def _run() -> None:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream,
                             server.create_initialization_options())

    anyio.run(_run)
    return 0


__all__ = ["sdk_available", "serve_sdk"]
