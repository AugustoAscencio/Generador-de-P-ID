"""Test del modelo JSON (FASE 13)."""

import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from generator.model import SpecError, load_spec  # noqa: E402

EXAMPLE = BASE / "examples" / "basic_circuit.json"
PV_EXAMPLE = BASE / "examples" / "pv_8_panels.json"


class TestModel(unittest.TestCase):

    def test_carga_formato_plano_legacy(self):
        """El formato original (diagram+elements planos) sigue funcionando."""
        spec = load_spec(EXAMPLE)
        self.assertEqual(spec.title, "QET Generator Test")
        self.assertEqual(len(spec.folios), 1)
        f = spec.folios[0]
        self.assertEqual(len(f.elements), 3)
        self.assertEqual(len(f.connections), 2)
        self.assertEqual(len(f.texts), 1)
        self.assertEqual(f.elements[0].id, "F1")
        self.assertEqual(f.elements[2].type, "motor_1p")
        self.assertEqual(f.order, 1)

    def test_label_por_defecto_es_el_id(self):
        spec = load_spec(EXAMPLE)
        self.assertEqual(spec.folios[0].elements[0].resolved_label(), "F1")

    def test_elementos_agregados_del_proyecto(self):
        spec = load_spec(EXAMPLE)
        self.assertEqual(len(spec.elements), 3)   # property: todos los folios

    def test_info_bom_se_parsea(self):
        spec = load_spec(PV_EXAMPLE)
        info = spec.folios[0].elements[0].info
        self.assertIn("designation", info)
        self.assertIn("SUPUESTO", info["designation"])

    def test_archivo_inexistente(self):
        with self.assertRaises(SpecError):
            load_spec(BASE / "examples" / "archivo_que_no_existe.json")

    def test_json_mal_formado(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False, encoding="utf-8") as f:
            f.write("{ esto no es json ")
            bad = Path(f.name)
        self.addCleanup(bad.unlink)
        with self.assertRaises(SpecError):
            load_spec(bad)

    def test_falta_project_title(self):
        import json
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False, encoding="utf-8") as f:
            json.dump({"project": {"title": ""}}, f)
            bad = Path(f.name)
        self.addCleanup(bad.unlink)
        with self.assertRaises(SpecError):
            load_spec(bad)


if __name__ == "__main__":
    unittest.main()
