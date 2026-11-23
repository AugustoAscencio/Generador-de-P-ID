"""Utilidades compartidas por los tests.

Biblioteca de fixtures
----------------------
Los tests **no dependen** de que QElectroTech esté instalado: usan los 14
``.elmt`` reales versionados en ``tests/fixtures/qet_elements/`` (copia
byte-exacta de la biblioteca 0.100.0, 44 KB).

Así la suite es **hermética** y corre igual en Linux, macOS y Windows por
igual, y el CI verifica la geometría real en vez de no verificar nada.

La integridad de los fixtures está garantizada por
``tests/test_fixtures.py``: comprueba que cada uno es byte-idéntico
(SHA-256) al ``.elmt`` de la biblioteca instalada, cuando esta está
disponible.

La **producción** (CLI y servidor MCP) sigue usando siempre la biblioteca
instalada de QElectroTech (``sources.library_path``), nunca los fixtures.
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
if str(BASE / "src") not in sys.path:
    sys.path.insert(0, str(BASE / "src"))
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from qetgen.core.catalog import SymbolCatalog  # noqa: E402

#: Catálogo lógico → ``.elmt`` real (el del repositorio).
CATALOG_PATH = BASE / "resources" / "symbol_catalog.json"

#: Biblioteca de fixtures: los 14 ``.elmt`` reales, versionados.
FIXTURE_LIBRARY = Path(__file__).resolve().parent / "fixtures" / "qet_elements"

#: Biblioteca instalada de QElectroTech (si existe en esta máquina).
INSTALLED_LIBRARY = Path(r"C:\Program Files\QElectroTech\elements")


def make_catalog(library_path: Path | str | None = None) -> SymbolCatalog:
    """Catálogo de símbolos sobre la biblioteca de fixtures.

    Es el catálogo que usan todos los tests: geometría real, sin depender de
    la instalación local de QElectroTech.
    """
    return SymbolCatalog(CATALOG_PATH,
                         library_path=library_path or FIXTURE_LIBRARY)


def installed_library_available() -> bool:
    """``True`` si QElectroTech está instalado en esta máquina."""
    return INSTALLED_LIBRARY.is_dir()


__all__ = [
    "BASE",
    "CATALOG_PATH",
    "FIXTURE_LIBRARY",
    "INSTALLED_LIBRARY",
    "installed_library_available",
    "make_catalog",
]
