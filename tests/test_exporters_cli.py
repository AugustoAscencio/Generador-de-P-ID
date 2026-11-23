"""Tests del exportador QET, la validación y la CLI."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))  # para importar 'tests.support'
sys.path.insert(0, str(BASE / "src"))

from qetgen.cli.main import main as cli_main  # noqa: E402
from qetgen.core.catalog import SymbolCatalog  # noqa: E402
from qetgen.core.io import load_spec  # noqa: E402
from qetgen.core.models import Project  # noqa: E402
from qetgen.exporters.qet import build_project, export_project  # noqa: E402
from qetgen.validation.structural import validate_project  # noqa: E402
from tests.support import CATALOG_PATH, FIXTURE_LIBRARY  # noqa: E402

CATALOG = CATALOG_PATH


class TestExportadorQet(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG, library_path=FIXTURE_LIBRARY)
        cls.spec = load_spec(BASE / "examples" / "basic_circuit.json")
        cls.root, cls.results = build_project(cls.spec, cls.catalog)

    def test_raiz_y_version(self):
        self.assertEqual(self.root.tag, "project")
        self.assertEqual(self.root.get("version"), "0.100.0")

    def test_orden_de_hijos_del_folio(self):
        diagram = self.root.find("diagram")
        self.assertEqual([c.tag for c in diagram],
                         ["properties", "defaultconductor", "elements",
                          "conductors", "inputs", "shapes"])

    def test_una_sola_coleccion(self):
        self.assertEqual(len(self.root.findall("collection")), 1)

    def test_conductores_referencian_uuids_existentes(self):
        terms = {t.get("uuid") for t in
                 self.root.findall("diagram/elements/element/terminals/terminal")}
        elems = {e.get("uuid") for e in
                 self.root.findall("diagram/elements/element")}
        for conductor in self.root.findall("diagram/conductors/conductor"):
            self.assertIn(conductor.get("terminal1"), terms)
            self.assertIn(conductor.get("terminal2"), terms)
            self.assertIn(conductor.get("element1"), elems)
            self.assertIn(conductor.get("element2"), elems)

    def test_exportar_releer_sin_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "proyecto.qet"
            export_project(self.root, out)
            raw = out.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertTrue(raw.startswith(b"<project"))
            reparsed = ET.fromstring(raw.decode("utf-8"))
            self.assertEqual(reparsed.tag, "project")

    def test_exportacion_atomica_no_deja_temporales(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "proyecto.qet"
            export_project(self.root, out)
            self.assertFalse(out.with_name(out.name + ".tmp").exists())

    def test_texto_html_escapado(self):
        """Regresión v0.1: el texto se insertaba sin escapar en el HTML."""
        from qetgen.exporters.qet.xml import wrap_html
        html = wrap_html("Q1 & Q2 < 10")
        self.assertIn("&", html)
        self.assertIn("<", html)

    def test_ids_de_terminal_reinician_por_folio(self):
        project = load_spec(BASE / "examples" / "proyecto_fv_588.json")
        root, _ = build_project(project, self.catalog)
        folios_con_elementos = 0
        for diagram in root.findall("diagram"):
            ids = [t.get("id") for t in
                   diagram.findall("elements/element/terminals/terminal")]
            if not ids:
                continue          # folio sin símbolos (p. ej. el índice D-001)
            folios_con_elementos += 1
            self.assertEqual(ids[0], "0")
            self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(folios_con_elementos, 10)

    def test_atributos_de_hoja_segun_formato(self):
        project = Project(
            title="P",
            folios=[__import__("qetgen.core.models", fromlist=["Sheet"]).Sheet(
                title="F", order=1, sheet_format="A4_11x7")],
        )
        root, _ = build_project(project, self.catalog)
        diagram = root.find("diagram")
        self.assertEqual(diagram.get("cols"), "11")
        self.assertEqual(diagram.get("rows"), "7")
        self.assertEqual(diagram.get("height"), "580")


class TestValidacion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG, library_path=FIXTURE_LIBRARY)

    def test_proyecto_real_sin_errores(self):
        project = load_spec(BASE / "examples" / "proyecto_fv_588.json")
        report = validate_project(project, self.catalog)
        self.assertEqual(report.errors, [])
        self.assertTrue(report.ok)

    def test_detecta_terminal_reutilizada(self):
        project = load_spec(BASE / "examples" / "proyecto_fv_588.json")
        report = validate_project(project, self.catalog)
        self.assertTrue(any("se usa en" in w for w in report.warnings),
                        report.warnings)

    def test_informe_serializable(self):
        project = load_spec(BASE / "examples" / "basic_circuit.json")
        report = validate_project(project, self.catalog)
        data = report.as_dict()
        self.assertIn("ok", data)
        self.assertIn("errors", data)
        json.dumps(data)          # debe ser serializable

    def test_fecha_no_real_detectada(self):
        from qetgen.core.models import Project, Sheet
        project = Project(title="P", folios=[Sheet(title="F", date="20261345")])
        report = validate_project(project, self.catalog)
        self.assertTrue(any("fecha real" in e for e in report.errors), report.errors)

    def test_orden_no_contiguo_es_aviso(self):
        from qetgen.core.models import Project, Sheet
        project = Project(title="P", folios=[Sheet(title="F", order=1),
                                             Sheet(title="G", order=5)])
        report = validate_project(project, self.catalog)
        self.assertTrue(any("contiguos" in w for w in report.warnings), report.warnings)


class TestCli(unittest.TestCase):

    def _run(self, argv):
        """Ejecuta la CLI con la biblioteca de fixtures.

        Así los tests no dependen de que QElectroTech esté instalado en la
        máquina que ejecuta la suite.
        """
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = cli_main([*argv, "--library", str(FIXTURE_LIBRARY)])
        return code, buffer.getvalue()

    def test_build_desde_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "salida.qet"
            code, text = self._run([
                "build", str(BASE / "examples" / "basic_circuit.json"),
                "-o", str(out)])
            self.assertEqual(code, 0)
            self.assertTrue(out.is_file())
            self.assertIn("Proyecto generado", text)

    def test_validate_devuelve_codigo_de_error_si_falla(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({
                "project": {"title": "T"},
                "diagrams": [{"title": "F", "elements": [
                    {"id": "A", "type": "no_existe", "x": 1, "y": 1}]}],
            }), encoding="utf-8")
            code, _ = self._run(["validate", str(bad)])
            self.assertEqual(code, 1)

    def test_validate_ok(self):
        code, text = self._run([
            "validate", str(BASE / "examples" / "basic_circuit.json")])
        self.assertEqual(code, 0)

    def test_symbols_json(self):
        code, text = self._run(["symbols", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(text)
        self.assertEqual(len(data), 14)
        self.assertIn("bounds", data[0])

    def test_sheets_json(self):
        code, text = self._run(["sheets", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(text)
        self.assertEqual(data["A3_17x8"]["width"], 1020)

    def test_export_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "spec.json"
            code, _ = self._run([
                "export", str(BASE / "examples" / "basic_circuit.json"),
                "-f", "json", "-o", str(out)])
            self.assertEqual(code, 0)
            self.assertTrue(out.is_file())


if __name__ == "__main__":
    unittest.main()
