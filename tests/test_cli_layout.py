"""Tests de la CLI profesional: ``qetgen layout`` y ``qetgen doctor``.

Fase 4 del plan: el motor de layout y el diagnóstico del entorno deben ser
usables desde la línea de comandos, con salidas accionables, códigos de salida
correctos y salida JSON para integraciones.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))  # para importar 'tests.support'
sys.path.insert(0, str(BASE / "src"))

from qetgen.cli.main import main as cli_main  # noqa: E402
from tests.support import FIXTURE_LIBRARY  # noqa: E402

FV588 = BASE / "examples" / "proyecto_fv_588.json"


def run_cli(*args: str) -> tuple[int, str]:
    """Ejecuta la CLI y devuelve ``(código_de_salida, salida)``.

    ``stderr`` se combina con ``stdout`` para poder comprobar tanto el
    informe como los mensajes de error.

    Se pasa siempre ``--library`` con la biblioteca de fixtures: así los
    tests no dependen de que QElectroTech esté instalado en la máquina.
    """
    buffer = io.StringIO()
    with redirect_stdout(buffer), redirect_stderr(buffer):
        code = cli_main([*args, "--library", str(FIXTURE_LIBRARY)])
    return code, buffer.getvalue()


class TestLayoutCLI(unittest.TestCase):

    def test_la_simulacion_no_escribe_nada(self):
        """Sin --apply, el comando informa pero no modifica nada."""
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run_cli("layout", str(FV588), "--folio", "3")
            self.assertEqual(code, 0)
            self.assertIn("simulación", out)
            self.assertIn("Folio  3", out)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_salida_json_valida(self):
        code, out = run_cli("layout", str(FV588), "--folio", "3", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn("folios", data)
        self.assertIn("summary", data)
        self.assertEqual(len(data["folios"]), 1)
        self.assertEqual(data["folios"][0]["folio"], 3)

    def test_check_devuelve_error_si_hay_defectos(self):
        """El caso FV 588 tiene 8 textos desbordados: debe salir con error."""
        code, out = run_cli("layout", str(FV588), "--folio", "8", "--check")
        self.assertEqual(code, 1)
        self.assertIn("OUT_OF_SHEET", out)

    def test_check_pasa_en_un_proyecto_limpio(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "limpio.json"
            spec.write_text(json.dumps({
                "project": {"title": "Proyecto limpio"},
                "diagrams": [{
                    "title": "F1",
                    "elements": [
                        {"id": "A", "type": "lamp", "x": 200, "y": 200},
                        {"id": "B", "type": "lamp", "x": 500, "y": 200},
                    ],
                    "connections": [
                        {"from": "A", "to": "B", "from_terminal": 0,
                         "to_terminal": 0},
                    ],
                }],
            }, ensure_ascii=False), encoding="utf-8")
            code, out = run_cli("layout", str(spec), "--check")
            self.assertEqual(code, 0, out)
            self.assertIn("Auditoría estética", out)

    def test_apply_guarda_un_json_valido(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "layout.json"
            code, out = run_cli("layout", str(FV588), "--folio", "3",
                                "--snap", "--apply", "-o", str(target))
            self.assertEqual(code, 0)
            self.assertTrue(target.is_file())
            data = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(len(data["diagrams"]), 18)

    def test_snap_alinea_a_la_rejilla(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "snap.json"
            run_cli("layout", str(FV588), "--folio", "3", "--snap",
                    "--apply", "-o", str(target))
            data = json.loads(target.read_text(encoding="utf-8"))
            folio = data["diagrams"][2]
            for element in folio["elements"]:
                self.assertEqual(element["x"] % 10, 0)
                self.assertEqual(element["y"] % 10, 0)

    def test_auto_layout_respeta_los_bloqueados(self):
        """Modo híbrido: un elemento con locked:true no se mueve."""
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "hibrido.json"
            spec.write_text(json.dumps({
                "project": {"title": "Híbrido"},
                "diagrams": [{
                    "title": "F1",
                    "elements": [
                        {"id": "A", "type": "lamp", "x": 123, "y": 456,
                         "locked": True},
                        {"id": "B", "type": "lamp", "x": 200, "y": 100},
                    ],
                }],
            }, ensure_ascii=False), encoding="utf-8")
            code, out = run_cli("layout", str(spec), "--auto-layout", "--json")
            self.assertEqual(code, 0)
            data = json.loads(out)
            self.assertEqual(data["locked"], 1)
            self.assertEqual(data["folios"][0]["kept_locked"], ["A"])

    def test_preview_escribe_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "svg"
            code, out = run_cli("layout", str(FV588), "--folio", "3",
                                "--preview", str(target))
            self.assertEqual(code, 0)
            written = list(target.glob("*.svg"))
            self.assertEqual(len(written), 1)
            self.assertTrue(written[0].read_text(encoding="utf-8").startswith(
                "<svg"))

    def test_el_preview_respeta_el_folio(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "svg"
            run_cli("layout", str(FV588), "--preview", str(target))
            self.assertEqual(len(list(target.glob("*.svg"))), 18)

    def test_un_folio_inexistente_es_un_error_claro(self):
        code, out = run_cli("layout", str(FV588), "--folio", "99")
        self.assertEqual(code, 2)
        self.assertIn("no existe", out)

    def test_los_errores_van_a_stderr(self):
        """Los errores de la CLI no se mezclan con el informe normal."""
        out_buffer = io.StringIO()
        err_buffer = io.StringIO()
        with redirect_stdout(out_buffer), redirect_stderr(err_buffer):
            code = cli_main(["layout", str(FV588), "--folio", "99",
                             "--library", str(FIXTURE_LIBRARY)])
        self.assertEqual(code, 2)
        self.assertEqual(out_buffer.getvalue(), "")
        self.assertIn("no existe", err_buffer.getvalue())


class TestDoctorCLI(unittest.TestCase):

    def test_doctor_sin_proyecto_es_correcto(self):
        code, out = run_cli("doctor")
        self.assertEqual(code, 0, out)
        self.assertIn("python", out)
        self.assertIn("catalog", out)
        self.assertIn("Todo operativo", out)

    def test_doctor_json_es_valido(self):
        code, out = run_cli("doctor", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        names = {check["check"] for check in data["checks"]}
        self.assertIn("python", names)
        self.assertIn("pydantic", names)
        self.assertIn("config", names)
        self.assertIn("catalog", names)

    def test_doctor_detecta_los_defectos_del_proyecto(self):
        """El proyecto FV 588 tiene 8 errores de texto desbordado."""
        code, out = run_cli("doctor", str(FV588), "--json")
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertFalse(data["ok"])
        project = [c for c in data["checks"] if c["check"] == "project"][0]
        self.assertEqual(project["status"], "error")

    def test_doctor_con_config_inexistente_falla(self):
        code, out = run_cli("doctor", "--config", "no_existe.yaml", "--json")
        self.assertEqual(code, 1)
        data = json.loads(out)
        config = [c for c in data["checks"] if c["check"] == "config"][0]
        self.assertEqual(config["status"], "error")


if __name__ == "__main__":
    unittest.main()
