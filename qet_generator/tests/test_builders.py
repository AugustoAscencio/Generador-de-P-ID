"""Tests de las plantillas paramétricas (builders.py — FASE 11)."""

import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from generator.builders import (build_module_folios,       # noqa: E402
                                create_aux_24vdc, create_dc_protection,
                                create_pv_string, folio_to_dict)
from generator.elements import SymbolCatalog                # noqa: E402
from generator.model import load_spec                       # noqa: E402
from generator.validate import validate_spec                # noqa: E402

CATALOG_PATH = BASE / "templates" / "symbol_catalog.json"


class TestBuilders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG_PATH)

    def test_create_pv_string_8(self):
        elements, connections = create_pv_string(count=8)
        self.assertEqual(len(elements), 8)
        self.assertEqual(len(connections), 7)
        self.assertEqual(elements[0].id, "PV1")
        self.assertEqual(elements[7].id, "PV8")
        self.assertEqual(connections[0].from_id, "PV1")
        self.assertEqual(connections[0].to_id, "PV2")

    def test_create_pv_string_parametrizable(self):
        elements, connections = create_pv_string(count=12, module="M042")
        self.assertEqual(len(elements), 12)
        self.assertEqual(elements[0].id, "M042-PV1")
        self.assertEqual(len(connections), 11)

    def test_create_dc_protection(self):
        elements, connections = create_dc_protection(module="M001")
        self.assertEqual([e.id for e in elements], ["M001-QDC1", "M001-X1"])
        self.assertEqual(len(connections), 1)

    def test_create_aux_24vdc(self):
        elements, connections = create_aux_24vdc(module="M001")
        self.assertEqual(len(elements), 4)
        self.assertEqual(len(connections), 3)

    def test_modulo_completo_valida_y_genera(self):
        folios = build_module_folios(module="M001", panel_count=8)
        self.assertEqual(len(folios), 2)
        spec_total_el = sum(len(f.elements) for f in folios)
        # 8 paneles + QDC + X1 + 4 auxiliares = 14
        self.assertEqual(spec_total_el, 14)

        from generator.model import ProjectSpec
        spec = ProjectSpec(title="Módulo M001", folios=folios)
        errors = validate_spec(spec, self.catalog)
        self.assertEqual(errors, [])

        from generator import project as project_mod
        root, results = project_mod.build_project(spec, self.catalog)
        self.assertEqual(len(root.findall("diagram")), 2)
        self.assertEqual(len(root.findall("diagram/elements/element")), 14)
        self.assertEqual(len(root.findall("diagram/conductors/conductor")), 12)

    def test_folio_to_dict_roundtrip(self):
        """El módulo serializado a JSON vuelve a cargar y valida igual."""
        import json
        import tempfile
        folios = build_module_folios(module="M001", panel_count=8)
        data = {"project": {"title": "Módulo M001"},
                "diagrams": [folio_to_dict(f) for f in folios]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                          encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            path = Path(f.name)
        self.addCleanup(path.unlink)
        spec = load_spec(path)
        self.assertEqual(len(spec.folios), 2)
        self.assertEqual(validate_spec(spec, self.catalog), [])


if __name__ == "__main__":
    unittest.main()
