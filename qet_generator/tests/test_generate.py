"""Tests de generación estructural del .qet (FASE 5/13).

Generan proyectos reales desde los ejemplos y comprueban que el XML
producido cumple el formato observado en QET 0.100.0
(incluye multi-folio, evidencia §11 de QET_FORMAT_NOTES.md).
"""

import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from generator import project as project_mod                  # noqa: E402
from generator.elements import SymbolCatalog                   # noqa: E402
from generator.model import load_spec                          # noqa: E402
from generator.validate import validate_spec                    # noqa: E402

EXAMPLE = BASE / "examples" / "basic_circuit.json"
PV_EXAMPLE = BASE / "examples" / "pv_8_panels.json"
CATALOG_PATH = BASE / "templates" / "symbol_catalog.json"


class GeneracionBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG_PATH)


class TestGeneracionBasica(GeneracionBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.spec = load_spec(EXAMPLE)
        cls.errors = validate_spec(cls.spec, cls.catalog)
        cls.root, cls.results = project_mod.build_project(cls.spec, cls.catalog)

    def test_el_ejemplo_valida(self):
        self.assertEqual(self.errors, [])

    def test_raiz_del_proyecto(self):
        self.assertEqual(self.root.tag, "project")
        self.assertEqual(self.root.get("version"), "0.100.0")
        self.assertEqual(self.root.get("title"), "QET Generator Test")
        for child_tag in ("properties", "newdiagrams", "diagram", "collection"):
            self.assertIsNotNone(self.root.find(child_tag),
                                 f"falta <{child_tag}> en <project>")

    def test_hijos_del_diagram_en_orden_observado(self):
        d = self.root.find("diagram")
        seq = [c.tag for c in d]
        self.assertEqual(seq, ["properties", "defaultconductor",
                               "elements", "conductors", "inputs", "shapes"])

    def test_tres_elementos_con_estructura_completa(self):
        elems = self.root.findall("diagram/elements/element")
        self.assertEqual(len(elems), 3)
        for el in elems:
            for attr in ("uuid", "orientation", "type", "x", "y",
                         "z", "freezeLabel", "prefix"):
                self.assertIsNotNone(el.get(attr), f"element sin atributo {attr}")
            self.assertTrue(el.get("type", "").startswith("embed://import/"))
            for child in ("terminals", "inputs", "elementInformations",
                          "dynamic_texts", "texts_groups"):
                self.assertIsNotNone(el.find(child), f"element sin <{child}>")

    def test_etiquetas_escritas_como_elementinformation(self):
        labels = {}
        for el in self.root.findall("diagram/elements/element"):
            for info in el.findall("elementInformations/elementInformation"):
                if info.get("name") == "label":
                    labels[el.get("uuid")] = (info.text or "")
        self.assertIn("F1", labels.values())
        self.assertIn("Q1", labels.values())
        self.assertIn("M1", labels.values())

    def test_conductores_referencian_uuids_existentes(self):
        placed_terms = {t.get("uuid") for t in
                       self.root.findall("diagram/elements/element/terminals/terminal")}
        placed_elems = {el.get("uuid") for el in
                        self.root.findall("diagram/elements/element")}
        conductors = self.root.findall("diagram/conductors/conductor")
        self.assertEqual(len(conductors), 2)
        for c in conductors:
            for end in ("1", "2"):
                self.assertIn(c.get(f"terminal{end}"), placed_terms)
                self.assertIn(c.get(f"element{end}"), placed_elems)
            self.assertEqual(c.get("type"), "multi")

    def test_texto_independiente_presente(self):
        inputs = self.root.findall("diagram/inputs/input")
        self.assertEqual(len(inputs), 1)
        self.assertIn("PRUEBA DE CONCEPTO", inputs[0].get("text", ""))

    def test_coleccion_embebida_contiene_definiciones(self):
        coll = self.root.find("collection")
        defs = coll.findall(".//definition")
        self.assertEqual(len(defs), 3, "deben embeberse 3 definiciones")

    def test_exportar_y_releer(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "roundtrip.qet"
            project_mod.export_project(self.root, out)
            raw = out.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertTrue(raw.startswith(b"<project"))
            reparsed = ET.fromstring(raw.decode("utf-8"))
            self.assertEqual(reparsed.tag, "project")
            self.assertEqual(len(reparsed.findall("diagram/elements/element")), 3)


class TestGeneracionPV8(GeneracionBase):
    """FASE 8: string de 8 paneles + protección DC + borne."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.spec = load_spec(PV_EXAMPLE)
        cls.root, cls.results = project_mod.build_project(cls.spec, cls.catalog)

    def test_10_elementos_9_conductores(self):
        self.assertEqual(len(self.root.findall("diagram/elements/element")), 10)
        self.assertEqual(len(self.root.findall("diagram/conductors/conductor")), 9)

    def test_todas_las_referencias_de_conductor_validas(self):
        terms = {t.get("uuid") for t in
                 self.root.findall("diagram/elements/element/terminals/terminal")}
        for c in self.root.findall("diagram/conductors/conductor"):
            self.assertIn(c.get("terminal1"), terms)
            self.assertIn(c.get("terminal2"), terms)

    def test_info_bom_escrita(self):
        """Los metadatos del folio PV (designation) van en elementInformation."""
        texts = [i.text for i in self.root.iter("elementInformation")
                 if i.get("name") == "designation" and i.text]
        self.assertTrue(any("Panel FV" in t for t in texts), texts)


class TestMultiFolio(GeneracionBase):
    """Evidencia §11: varios <diagram>, orders 1..N, ids de terminal POR FOLIO."""

    def _build_two_folio(self):
        from generator.model import (ConnectionSpec, ElementSpec,
                                     FolioSpec, ProjectSpec, TextSpec)
        spec = ProjectSpec(title="Multi", folios=[
            FolioSpec(title="folio A", order=1,
                      elements=[ElementSpec(id="A1", type="ac_source", x=100, y=100),
                                ElementSpec(id="A2", type="lamp", x=100, y=220)],
                      connections=[ConnectionSpec(from_id="A1", from_terminal=1,
                                                  to_id="A2", to_terminal=0)]),
            FolioSpec(title="folio B", order=2,
                      elements=[ElementSpec(id="B1", type="lamp", x=200, y=100)],
                      texts=[TextSpec(x=50, y=50, text="folio B")]),
        ])
        root, results = project_mod.build_project(spec, self.catalog)
        return root, results

    def test_dos_diagramas_con_orders_secuenciales(self):
        root, results = self._build_two_folio()
        diagrams = root.findall("diagram")
        self.assertEqual(len(diagrams), 2)
        self.assertEqual([d.get("order") for d in diagrams], ["1", "2"])
        self.assertEqual([d.get("title") for d in diagrams], ["folio A", "folio B"])

    def test_ids_de_terminal_reinician_por_folio(self):
        """Evidencia §11: cada folio reinicia ids 0.. (como archivos reales)."""
        root, _ = self._build_two_folio()
        per_folio = []
        for d in root.findall("diagram"):
            ids = [t.get("id") for t in
                   d.findall("elements/element/terminals/terminal")]
            per_folio.append(ids)
        self.assertEqual(per_folio[0], ["0", "1", "2", "3"])  # A1 2 terms + A2 2 terms
        self.assertEqual(per_folio[1], ["0", "1"])            # B1 2 terms, reinicia

    def test_una_sola_coleccion_compartida(self):
        root, _ = self._build_two_folio()
        self.assertEqual(len(root.findall("collection")), 1)
        # ac_source y lamp usados en ambos folios -> embebidos UNA vez
        defs = root.findall("collection//definition")
        self.assertEqual(len(defs), 2)

    def test_uuids_de_instancia_unicos_en_proyecto(self):
        root, _ = self._build_two_folio()
        uuids = [el.get("uuid") for el in root.findall("diagram/elements/element")]
        self.assertEqual(len(uuids), len(set(uuids)))


if __name__ == "__main__":
    unittest.main()
