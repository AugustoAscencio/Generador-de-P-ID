"""main.py — CLI heredada de la v0.1 (deprecated).

> **Deprecated:** use el CLI de la v1.0:
>
> .. code-block:: bash
>
>     qetgen build entrada.json -o salida.qet
>
> Este script se mantiene para que los comandos antiguos sigan funcionando
 * y delega toda la lógica en :mod:`qetgen.cli`.
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR.parent / "src"))

from qetgen.cli.main import main as _new_main  # noqa: E402

#: Catálogo heredado (la v1.0 usa ``resources/symbol_catalog.json``).
_LEGACY_CATALOG = BASE_DIR.parent / "resources" / "symbol_catalog.json"


def main(argv=None) -> int:
    """Punto de entrada heredado: traduce los argumentos v0.1 a la v1.0."""
    argv = list(sys.argv[1:] if argv is None else argv)
    # v0.1: `python main.py entrada.json [-o salida.qet] [--catalog ...] [--library ...]`
    # v1.0: `qetgen build entrada.json [-o salida.qet] [--catalog ...]`
    if argv and argv[0] not in {"build", "validate", "export", "symbols",
                                "sheets", "fv588", "layout", "serve"}:
        argv = ["build"] + argv
    if "--catalog" not in argv and _LEGACY_CATALOG.is_file():
        argv += ["--catalog", str(_LEGACY_CATALOG)]
    return _new_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
