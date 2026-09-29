"""Test integral: los 18 planos del proyecto FV 588 módulos.

Valida: 18 folios con orders 1..18, sin errores de validación, conductores
con referencias correctas, sin IDs duplicados en el proyecto, y generación
XML correcta (multi-folio, evidencia §11).
"""

import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from generator import project as project_mod                # noqa: E402
from generator.builders import folio_to_dict                # noqa: E402
from generator.elements import SymbolCatalog                # noqa: E402
from generator.model import ProjectSpec, load_spec          # noqa: E402
from generator.sheets import build_all                      # noqa: E402
from generator.validate import validate_spec                # noqa: E402

CATALOG_PATH = BASE / "templates" / "symbol_catalog.json"


class TestLos18Planos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG_PATH)
        cls.folios = build_all()
        cls.spec = ProjectSpec(
            title="PROYECTO FV 588 MÓDULOS — SEGUEIDOR BIAXIAL 8×650 Wp",
            author="Documentación eléctrica",
            folios=cls.folios,
        )
        cls.errors = validate_spec(cls.spec, cls.catalog)
        cls.root, cls.results = project_mod.build_project(cls.spec, cls.catalog)

    def test_18_folios_con_orders_secuenciales(self):
        self.assertEqual(len(self.folios), 18)
        self.assertEqual([f.order for f in self.folios], list(range(1, 19)))
        self.assertEqual(self.errors, [])

    def test_todos_los_titulos_D(self):
        for f in self.folios:
            self.assertTrue(f.title.startswith("D-0"), f.title)

    def test_xml_18_diagramas(self):
        diagrams = self.root.findall("diagram")
        self.assertEqual(len(diagrams), 18)
        self.assertEqual([d.get("order") for d in diagrams],
                          [str(i) for i in range(1, 19)])

    def test_conductores_con_referencias_validas(self):
        for d in self.root.findall("diagram"):
            terms = {t.get("uuid") for t in
                     d.findall("elements/element/terminals/terminal")}
            euids = {e.get("uuid") for e in d.findall("elements/element")}
            for c in d.findall("conductors/conductor"):
                self.assertIn(c.get("terminal1"), terms)
                self.assertIn(c.get("terminal2"), terms)
                self.assertIn(c.get("element1"), euids)
                self.assertIn(c.get("element2"), euids)

    def test_ids_unicos_en_proyecto(self):
        ids = [el.id for el in self.spec.elements]
        self.assertEqual(len(ids), len(set(ids)))

    def test_folios_con_elementos_elegidos(self):
        by_order = {f.order: f for f in self.folios}
        self.assertEqual(len(by_order[3].elements), 10)    # D-003 string
        self.assertEqual(len(by_order[4].elements), 7)    # D-004 X1,X2,QF,X3,X4,SPD,PE
        self.assertEqual(len(by_order[6].elements), 13)   # D-006 eje (13 elementos)
        self.assertEqual(len(by_order[8].elements), 26)   # D-008 entradas
        self.assertEqual(len(by_order[16].elements), 19)  # D-016 borneras

    def test_json_roundtrip_de_los_18(self):
        import json
        import tempfile
        data = {"project": {"title": "T"},
                "diagrams": [folio_to_dict(f) for f in self.folios]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            path = Path(f.name)
        self.addCleanup(path.unlink)
        spec = load_spec(path)
        self.assertEqual(len(spec.folios), 18)
        self.assertEqual(validate_spec(spec, self.catalog), [])


if __name__ == "__main__":
    unittest.main()
