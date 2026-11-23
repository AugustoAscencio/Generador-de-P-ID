"""Integridad de los fixtures de la biblioteca de símbolos.

Los tests usan ``tests/fixtures/qet_elements/`` —los 14 ``.elmt`` reales de
QElectroTech 0.100.0— para ser **herméticos** y poder correr en Linux,
macOS y Windows por igual.

Este módulo garantiza que esos fixtures:

1. cubren **exactamente** los símbolos del catálogo (ni uno de más, ni uno
   de menos);
2. son **byte-idénticos** (SHA-256) a los ``.elmt`` de la biblioteca
   instalada — cuando QElectroTech está disponible en la máquina.

Si QElectroTech no está instalado, la comparación se omite (skip): el resto
de la suite sigue siendo válida porque los fixtures son la evidencia
versionada.
"""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))  # para importar 'tests.support'
sys.path.insert(0, str(BASE / "src"))

from tests.support import (  # noqa: E402
    CATALOG_PATH,
    FIXTURE_LIBRARY,
    INSTALLED_LIBRARY,
    installed_library_available,
)


def catalog_entries() -> dict[str, str]:
    """``{tipo_logico: elmt_path_relativo}`` del catálogo del repositorio."""
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return {
        key: str(value["elmt_path"]).replace("\\", "/").strip("/")
        for key, value in data.items()
        if not key.startswith("_")
    }


def sha256(path: Path) -> str:
    """SHA-256 de un archivo."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestCoberturaDeLosFixtures(unittest.TestCase):
    """Los fixtures cubren el catálogo completo, ni más ni menos."""

    def setUp(self):
        self.entries = catalog_entries()

    def test_el_catalogo_tiene_los_14_simbolos_conocidos(self):
        self.assertEqual(len(self.entries), 14)

    def test_todo_simbolo_del_catalogo_tiene_su_fixture(self):
        faltan = [key for key, rel in self.entries.items()
                  if not (FIXTURE_LIBRARY / rel).is_file()]
        self.assertEqual(faltan, [],
                         f"faltan fixtures para: {', '.join(faltan)}")

    def test_no_hay_fixtures_sobrantes(self):
        esperados = {(FIXTURE_LIBRARY / rel).resolve()
                     for rel in self.entries.values()}
        encontrados = {path.resolve() for path
                       in FIXTURE_LIBRARY.rglob("*.elmt")}
        self.assertEqual(encontrados - esperados, set(),
                         "hay fixtures que no corresponden al catálogo")

    def test_la_biblioteca_de_fixtures_carga(self):
        from qetgen.core.catalog import SymbolCatalog
        catalog = SymbolCatalog(CATALOG_PATH, library_path=FIXTURE_LIBRARY)
        self.assertEqual(len(catalog.type_keys()), 14)


@unittest.skipUnless(installed_library_available(),
                     "QElectroTech no está instalado en esta máquina")
class TestIntegridadContraLaBibliotecaInstalada(unittest.TestCase):
    """Los fixtures son byte-idénticos a la biblioteca real (SHA-256)."""

    def test_cada_fixture_coincide_con_el_elmt_instalado(self):
        entradas = catalog_entries()
        for key, rel in entradas.items():
            with self.subTest(simbolo=key):
                fixture = FIXTURE_LIBRARY / rel
                instalado = INSTALLED_LIBRARY / rel
                self.assertTrue(instalado.is_file(),
                                f"{key}: no existe en la biblioteca instalada")
                self.assertEqual(sha256(fixture), sha256(instalado),
                                 f"{key}: el fixture ha derivado "
                                 f"(ejecuta tools/sync_fixtures.py)")

    def test_la_biblioteca_real_tiene_los_14_simbolos(self):
        for key, rel in catalog_entries().items():
            with self.subTest(simbolo=key):
                self.assertTrue((INSTALLED_LIBRARY / rel).is_file())


if __name__ == "__main__":
    unittest.main()
