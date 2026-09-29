"""Tests de validación del modelo (FASE 12/13)."""

import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from generator.elements import SymbolCatalog                     # noqa: E402
from generator.model import (ConnectionSpec, ElementSpec,       # noqa: E402
                              FolioSpec, ProjectSpec, TextSpec)
from generator.validate import validate_spec                     # noqa: E402

CATALOG_PATH = BASE / "templates" / "symbol_catalog.json"


def make_spec(elements, connections=None, texts=None) -> ProjectSpec:
    return ProjectSpec(
        title="Test",
        folios=[FolioSpec(title="folio test",
                          elements=list(elements),
                          connections=list(connections or []),
                          texts=list(texts or []))],
    )


class CatalogBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG_PATH)


class TestValidaciones(CatalogBase):

    def spec_valido(self):
        return make_spec(
            [ElementSpec(id="F1", type="ac_source", x=100, y=100),
             ElementSpec(id="Q1", type="circuit_breaker_1p", x=100, y=220),
             ElementSpec(id="M1", type="motor_1p", x=100, y=340)],
            [ConnectionSpec(from_id="F1", to_id="Q1", from_terminal=1, to_terminal=0),
             ConnectionSpec(from_id="Q1", to_id="M1", from_terminal=1, to_terminal=1)],
            [TextSpec(x=400, y=500, text="texto")],
        )

    def test_spec_valido_sin_errores(self):
        self.assertEqual(validate_spec(self.spec_valido(), self.catalog), [])

    def test_id_duplicado(self):
        spec = make_spec([
            ElementSpec(id="F1", type="ac_source", x=100, y=100),
            ElementSpec(id="F1", type="ac_source", x=200, y=100),
        ])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("duplicado" in e.lower() for e in errors), errors)

    def test_id_duplicado_entre_folios(self):
        spec = ProjectSpec(title="T", folios=[
            FolioSpec(title="f1", elements=[ElementSpec(id="A", type="ac_source", x=1, y=1)]),
            FolioSpec(title="f2", elements=[ElementSpec(id="A", type="ac_source", x=2, y=2)]),
        ])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("duplicado" in e.lower() for e in errors), errors)

    def test_conexion_a_elemento_inexistente(self):
        spec = make_spec(
            [ElementSpec(id="F1", type="ac_source", x=100, y=100)],
            [ConnectionSpec(from_id="F1", to_id="NO_EXISTO", from_terminal=1, to_terminal=0)],
        )
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("inexistente" in e for e in errors), errors)

    def test_conexion_entre_folios_no_permitida(self):
        """Las conexiones se resuelven DENTRO del folio (limitación actual)."""
        spec = ProjectSpec(title="T", folios=[
            FolioSpec(title="f1", elements=[ElementSpec(id="A", type="ac_source", x=1, y=1)],
                      connections=[ConnectionSpec(from_id="A", to_id="B")]),
            FolioSpec(title="f2", elements=[ElementSpec(id="B", type="ac_source", x=2, y=2)]),
        ])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("inexistente en este folio" in e for e in errors), errors)

    def test_tipo_no_registrado(self):
        spec = make_spec([ElementSpec(id="X1", type="tipo_inventado", x=10, y=10)])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("no registrado" in e for e in errors), errors)

    def test_terminal_fuera_de_rango(self):
        spec = make_spec(
            [ElementSpec(id="F1", type="ac_source", x=100, y=100)],
            [ConnectionSpec(from_id="F1", to_id="F1", from_terminal=9, to_terminal=0)],
        )
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("fuera de rango" in e for e in errors), errors)

    def test_conexion_consigo_mismo(self):
        spec = make_spec(
            [ElementSpec(id="F1", type="ac_source", x=100, y=100)],
            [ConnectionSpec(from_id="F1", to_id="F1", from_terminal=1, to_terminal=0)],
        )
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("consigo mismo" in e for e in errors), errors)

    def test_texto_vacio(self):
        spec = make_spec([], texts=[TextSpec(x=10, y=10, text="   ")])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("texto vacío" in e for e in errors), errors)

    def test_fecha_mal_formato(self):
        spec = self.spec_valido()
        spec.folios[0].date = "28/09/2026"
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("AAAAMMDD" in e for e in errors), errors)

    def test_order_de_folio_duplicado(self):
        spec = ProjectSpec(title="T", folios=[
            FolioSpec(title="f1", order=1, elements=[ElementSpec(id="A", type="ac_source", x=1, y=1)]),
            FolioSpec(title="f2", order=1, elements=[ElementSpec(id="B", type="ac_source", x=2, y=2)]),
        ])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("duplicados" in e for e in errors), errors)

    def test_clave_info_desconocida(self):
        spec = make_spec([ElementSpec(id="F1", type="ac_source", x=1, y=1,
                                      info={"volts": "230"})])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("clave de info no reconocida" in e for e in errors), errors)

    def test_info_valida_aceptada(self):
        spec = make_spec([ElementSpec(
            id="F1", type="ac_source", x=1, y=1,
            info={"designation": "Fuente 24VDC", "manufacturer": "SUPUESTO", "quantity": "1"})])
        self.assertEqual(validate_spec(spec, self.catalog), [])


if __name__ == "__main__":
    unittest.main()
