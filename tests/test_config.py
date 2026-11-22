"""Tests de la configuración central (``config/default.yaml``).

La configuración es el **único** sitio donde se ajustan hoja, cuadrícula,
tipografía y routing. Estos tests garantizan dos cosas:

1. el archivo que se entrega se carga sin errores y valida contra el modelo,
2. **no se desincroniza** del código: si alguien cambia un valor por defecto
   en el modelo y olvida el YAML (o al revés), el test falla.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))

from qetgen.config import (QetGenConfig, default_config_path,  # noqa: E402
                           load_config)
from qetgen.core.errors import SpecError                   # noqa: E402


class TestConfiguracionCentral(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path = default_config_path()
        cls.config = load_config(cls.path)

    def test_el_archivo_por_defecto_existe(self):
        self.assertTrue(self.path.is_file(), f"falta {self.path}")
        self.assertEqual(self.path.name, "default.yaml")

    def test_el_archivo_se_carga_sin_errores(self):
        self.assertIsInstance(self.config, QetGenConfig)

    def test_los_valores_por_defecto_coinciden_con_el_yaml(self):
        """El YAML entregado debe reflejar exactamente el modelo."""
        defaults = QetGenConfig()
        self.assertEqual(self.config.to_dict(), defaults.to_dict())

    def test_las_claves_clave_estan_presentes(self):
        data = self.config.to_dict()
        self.assertIn("edge_tolerance", data["sheet"])
        self.assertIn("px_per_pt", data["typography"])
        self.assertIn("grid_size", data["layout"])
        self.assertIn("min_separation", data["layout"])
        self.assertIn("respect_locked", data["layout"])

    def test_la_tolerancia_de_borde_es_la_calibrada(self):
        """36 px: 9 de los 10 desbordes reales de QET están por debajo."""
        self.assertEqual(self.config.sheet.edge_tolerance, 36.0)

    def test_los_px_por_punto_son_96_dpi(self):
        self.assertAlmostEqual(self.config.typography.px_per_pt, 4.0 / 3.0)

    def test_un_archivo_inexistente_da_error_claro(self):
        with self.assertRaises(SpecError) as ctx:
            load_config(BASE / "no_existe.yaml")
        self.assertIn("no_existe.yaml", str(ctx.exception))

    def test_una_clave_desconocida_es_rechazada(self):
        """Pydantic estricto: ``extra="forbid"`` en todas las secciones."""
        import json
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as handle:
            json.dump({"sheet": {"clave_inventada": 1}}, handle)
            path = handle.name
        with self.assertRaises(SpecError):
            load_config(path)
        Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
