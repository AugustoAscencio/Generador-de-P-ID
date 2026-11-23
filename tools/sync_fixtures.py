"""tools/sync_fixtures.py — Refresca los fixtures de la biblioteca de QET.

Copia los ``.elmt`` reales que usa ``resources/symbol_catalog.json`` desde
la biblioteca instalada de QElectroTech a
``tests/fixtures/qet_elements/``, conservando la estructura de carpetas
relativa, y verifica sus SHA-256.

Los fixtures son lo que permite que la suite de tests sea **hermética** y
corra en Linux, macOS y Windows sin instalar QElectroTech. Este script es
la forma soportada de actualizarlos cuando cambia la versión de QET.

Uso::

    python -X utf8 tools/sync_fixtures.py            # sincroniza y verifica
    python -X utf8 tools/sync_fixtures.py --check    # solo verifica

Requiere QElectroTech instalado (``sources.library_path`` de la
configuración central).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from qetgen.config import default_config_path, load_config  # noqa: E402

CATALOG = REPO / "resources" / "symbol_catalog.json"
FIXTURES = REPO / "tests" / "fixtures" / "qet_elements"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entries() -> dict[str, str]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {
        key: str(value["elmt_path"]).replace("\\", "/").strip("/")
        for key, value in data.items()
        if not key.startswith("_")
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    check_only = "--check" in argv

    config_path = None
    if "--config" in argv:
        index = argv.index("--config")
        if index + 1 >= len(argv):
            print("ERROR: --config necesita una ruta")
            return 2
        config_path = argv[index + 1]

    config = load_config(config_path or default_config_path())
    library = Path(config.sources.library_path)
    if not library.is_dir():
        if check_only:
            # Sin QElectroTech no se puede comparar: se informa y se sale
            # con éxito. La integridad la cubre `tests/test_fixtures.py`,
            # que se omite (skip) en el mismo caso.
            print(f"AVISO: QElectroTech no está instalado ({library}); "
                  f"no se puede verificar la sincronía de los fixtures.")
            return 0
        print(f"ERROR: no se encuentra la biblioteca de QElectroTech: {library}")
        print("Instala QElectroTech o corrige sources.library_path.")
        return 2

    problems: list[str] = []
    total = 0
    for key, rel in entries().items():
        src = library / rel
        dst = FIXTURES / rel
        if not src.is_file():
            problems.append(f"{key}: no existe en la biblioteca ({src})")
            continue
        if not check_only:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        if not dst.is_file():
            problems.append(f"{key}: falta el fixture ({dst})")
            continue
        if sha256(src) != sha256(dst):
            problems.append(
                f"{key}: el fixture NO coincide con la biblioteca "
                f"(ejecuta este script sin --check)")
            continue
        total += dst.stat().st_size
        print(f"OK  {key:22} {dst.stat().st_size:>7} bytes  "
              f"sha256:{sha256(dst)[:16]}")

    print()
    if problems:
        print("Problemas:")
        for problem in problems:
            print("  -", problem)
        return 1
    print(f"{len(entries())} fixtures verificados ({total} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
