"""mcp_server/main.py — Punto de entrada del servidor MCP.

``qetgen serve`` arranca el servidor MCP por ``stdio``:

* con el **SDK oficial** instalado (``pip install 'qetgen[mcp]'``), se usa su
  API completa;
* sin él, arranca el **fallback propio** (JSON-RPC 2.0 sobre JSON Lines),
  que implementa el mismo protocolo y las mismas herramientas.

En ambos casos el cliente MCP ve **exactamente la misma interfaz**.
"""

from __future__ import annotations

import sys

from .. import __version__
from ..core.errors import QetGenError
from .session import Session, ToolError


def build_session(config_path: str | None = None,
                  catalog_path: str | None = None,
                  library_path: str | None = None) -> Session:
    """Crea la sesión del servidor (catálogo + configuración)."""
    try:
        return Session.create(config_path=config_path,
                              catalog_path=catalog_path,
                              library_path=library_path)
    except QetGenError as exc:
        raise ToolError(str(exc)) from exc


def main(argv: list[str] | None = None) -> int:
    """Arranca el servidor MCP (punto de entrada de ``qetgen serve``)."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="qetgen serve",
        description=f"Servidor MCP de qetgen v{__version__} (stdio)")
    parser.add_argument("--config", help="Configuración (YAML/JSON)")
    parser.add_argument("--catalog", help="Catálogo de símbolos (JSON)")
    parser.add_argument("--library", help="Biblioteca de elementos de QET")
    parser.add_argument("--fallback", action="store_true",
                        help="Fuerza el servidor propio (sin el SDK oficial)")
    args = parser.parse_args(argv)

    try:
        session = build_session(args.config, args.catalog, args.library)
    except ToolError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    from .sdk_server import sdk_available
    use_sdk = sdk_available() and not args.fallback

    if use_sdk:                                   # pragma: no cover
        from .sdk_server import serve_sdk
        try:
            return serve_sdk(session)
        except ImportError as exc:
            print(f"AVISO: SDK de MCP no utilizable ({exc}); "
                  f"se usa el servidor propio.", file=sys.stderr)

    from .fallback import serve_stdio
    try:
        serve_stdio(session)
    except KeyboardInterrupt:                     # pragma: no cover
        return 130
    return 0


__all__ = ["build_session", "main"]
