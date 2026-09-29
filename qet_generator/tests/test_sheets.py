"""Tests de shapes (bloques) y de las hojas D-002/D-003 del proyecto FV."""

import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from generator import project as project_mod                # noqa: E402
from generator.builders import build_d002, build_d003       # noqa: E402
from generator.elements import SymbolCatalog                # noqa: E402
from generator.model import ProjectSpec, load_spec          # noqa: E402
from generator.validate import validate_spec                # noqa: E402

CATALOG_PATH = BASE / "templates" / "symbol_catalog.json"


class TestShapes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG_PATH)

    def test_d002_valida_y_genera(self):
        folio = build_d002()
        spec = ProjectSpec(title="T", folios=[folio])
        self.assertEqual(validate_spec(spec, self.catalog), [])
        root, results = project_mod.build_project(spec, self.catalog)
        self.assertEqual(len(folio.shapes), 13)      # 13 bloques rectangulares
        self.assertEqual(len(folio.texts), 44)        # encabezado+interiores+flechas+notas
        # el XML lleva los shapes con pen/brush según evidencia
        shapes_xml = root.findall("diagram/shapes/shape")
        self.assertEqual(len(shapes_xml), 13)
        for sh in shapes_xml:
            self.assertEqual(sh.get("type"), "Rectangle")
            self.assertIsNotNone(sh.find("pen"))
            self.assertIsNotNone(sh.find("brush"))

    def test_d003_valida_y_genera(self):
        folio = build_d003()
        spec = ProjectSpec(title="T", folios=[folio])
        self.assertEqual(validate_spec(spec, self.catalog), [])
        root, results = project_mod.build_project(spec, self.catalog)
        self.assertEqual(len(folio.elements), 10)      # 8 paneles + X1 + X2
        self.assertEqual(len(folio.connections), 9)    # 7 serie + 2 salidas
        # conductores referencian terminales existentes
        terms = {t.get("uuid") for t in
                 root.findall("diagram/elements/element/terminals/terminal")}
        for c in root.findall("diagram/conductors/conductor"):
            self.assertIn(c.get("terminal1"), terms)
            self.assertIn(c.get("terminal2"), terms)

    def test_d003_etiquetas_y_bom(self):
        folio = build_d003()
        labels = [el.label for el in folio.elements]
        self.assertEqual(labels, ["PV-01", "PV-02", "PV-03", "PV-04",
                                  "PV-05", "PV-06", "PV-07", "PV-08",
                                  "X1", "X2"])
        desigs = [el.info.get("designation", "") for el in folio.elements
                  if el.id.startswith("PV")]
        self.assertTrue(all("650 Wp" in d for d in desigs))

    def test_shapes_json_roundtrip(self):
        """Bloques serializados en el JSON vuelven a cargar y validar."""
        import json
        import tempfile
        from generator.builders import folio_to_dict
        folio = build_d002()
        data = {"project": {"title": "T"},
                "diagrams": [folio_to_dict(folio)]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            path = Path(f.name)
        self.addCleanup(path.unlink)
        spec = load_spec(path)
        self.assertEqual(len(spec.folios[0].shapes), 13)

    def test_text_size_fuera_de_rango_rechazado(self):
        from generator.model import FolioSpec, SpecError, TextSpec
        # size inválido se detecta al validar
        folio = FolioSpec(title="t", texts=[TextSpec(x=1, y=1, text="x", size=99)])
        spec = ProjectSpec(title="T", folios=[folio])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("size" in e for e in errors))

    def test_shape_coordenadas_invertidas_rechazadas(self):
        from generator.model import FolioSpec, ShapeSpec
        folio = FolioSpec(title="t", shapes=[ShapeSpec(x1=100, y1=100,
                                                       x2=50, y2=150)])
        spec = ProjectSpec(title="T", folios=[folio])
        errors = validate_spec(spec, self.catalog)
        self.assertTrue(any("invertidas" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
