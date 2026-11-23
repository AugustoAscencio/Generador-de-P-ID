"""tools/check_version.py — Comprueba que la versión declarada es coherente.

El número de versión aparece en dos sitios que deben coincidir siempre:

* ``src/qetgen/__init__.py`` → ``__version__``
* ``pyproject.toml`` → ``version = "..."``

Un script en Python (en vez de un one-liner en el YAML) funciona igual en
``bash`` (Linux) y en ``pwsh`` (Windows), que es lo que hace que el CI
pueda correr la misma matriz en los dos sistemas.

Salida: 0 si son coherentes, 1 si no.
"""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def main() -> int:
    import qetgen

    version = qetgen.__version__
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    declared = match.group(1) if match else None

    if declared != version:
        print(f"ERROR: version incoherente: "
              f"__init__={version!r} vs pyproject={declared!r}")
        return 1
    print(f"OK: version declarada = {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
