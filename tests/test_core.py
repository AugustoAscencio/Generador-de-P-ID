"""Tests del núcleo: modelos estrictos, catálogo, geometría y E/S."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))  # para importar 'tests.support'
sys.path.insert(0, str(BASE / "src"))

from pydantic import ValidationError  # noqa: E402

from qetgen.core.catalog import SymbolCatalog  # noqa: E402
from qetgen.core.errors import CatalogError, SpecError  # noqa: E402
from qetgen.core.geometry import BBox, Vec2  # noqa: E402
from qetgen.core.io import load_spec, project_from_dict, project_to_dict, save_spec  # noqa: E402
from qetgen.core.models import Component, Connection, Project, Shape, Sheet  # noqa: E402
from qetgen.core.sheet import SHEET_FORMATS, get_sheet_format  # noqa: E402
from tests.support import CATALOG_PATH, FIXTURE_LIBRARY  # noqa: E402

CATALOG = CATALOG_PATH


class TestModelosEstrictos(unittest.TestCase):
    """Pydantic v2: el esquema es un contrato, no un dict disfrazado."""

    def test_componente_requiere_campos_obligatorios(self):
        with self.assertRaises(ValidationError):
            Component(id="X1", type="lamp")          # faltan x e y

    def test_clave_desconocida_rechazada(self):
        with self.assertRaises(ValidationError):
            Component(id="X1", type="lamp", x=0, y=0, color="rojo")

    def test_orientacion_fuera_de_rango_rechazada(self):
        with self.assertRaises(ValidationError):
            Component(id="X1", type="lamp", x=0, y=0, orientation=7)

    def test_orientacion_acepta_cadena_numerica(self):
        component = Component(id="X1", type="lamp", x=0, y=0, orientation="2")
        self.assertEqual(component.orientation, 2)

    def test_orientacion_booleana_rechazada(self):
        with self.assertRaises(ValidationError):
            Component(id="X1", type="lamp", x=0, y=0, orientation=True)

    def test_info_normaliza_a_texto(self):
        component = Component(id="X1", type="lamp", x=0, y=0,
                              info={"quantity": 1, "designation": "Lámpara"})
        self.assertEqual(component.info["quantity"], "1")
        self.assertEqual(component.info["designation"], "Lámpara")

    def test_info_descarta_valores_vacios(self):
        component = Component(id="X1", type="lamp", x=0, y=0,
                              info={"comment": "", "formula": None})
        self.assertEqual(component.info, {})

    def test_label_por_defecto_es_el_id(self):
        self.assertEqual(Component(id="F1", type="lamp", x=0, y=0).resolved_label(), "F1")
        self.assertEqual(
            Component(id="F1", type="lamp", x=0, y=0, label="F1-A").resolved_label(), "F1-A")

    def test_dash_cadena_false_no_se_convierte_en_true(self):
        """Regresión v0.1: bool('false') == True."""
        shape = Shape(x1=0, y1=0, x2=10, y2=10, dash="false")
        self.assertIs(shape.dash, False)
        shape = Shape(x1=0, y1=0, x2=10, y2=10, dash="true")
        self.assertIs(shape.dash, True)

    def test_color_invalido_rechazado(self):
        with self.assertRaises(ValidationError):
            Shape(x1=0, y1=0, x2=1, y2=1, color="rojo")

    def test_conexion_acepta_alias_from_y_to(self):
        connection = Connection(**{"from": "A", "to": "B", "from_terminal": 1})
        self.assertEqual(connection.from_id, "A")
        self.assertEqual(connection.to_id, "B")
        self.assertEqual(connection.key(), "A[1] -> B[0]")

    def test_conexion_acepta_nombres_internos(self):
        connection = Connection(from_id="A", to_id="B")
        self.assertEqual(connection.from_id, "A")

    def test_proyecto_exige_al_menos_un_folio(self):
        with self.assertRaises(ValidationError):
            Project(title="Vacío")

    def test_proyecto_titulo_no_vacio(self):
        with self.assertRaises(ValidationError):
            Project(title="   ")

    def test_hoja_expone_alias_sheets(self):
        sheet = Sheet(title="A")
        project = Project(title="P", folios=[sheet])
        self.assertIs(project.sheets[0], sheet)
        self.assertEqual(len(project.elements), 0)

    def test_json_schema_publicable_para_mcp(self):
        """El servidor MCP publica model_json_schema() como inputSchema."""
        schema = Component.model_json_schema()
        self.assertIn("properties", schema)
        self.assertIn("id", schema["properties"])
        self.assertEqual(schema["additionalProperties"], False)


class TestGeometria(unittest.TestCase):

    def test_bbox_desde_puntos(self):
        box = BBox.from_points([(10, 20), (30, 5), (0, 40)])
        self.assertEqual(box.as_tuple(), (0.0, 5.0, 30.0, 40.0))
        self.assertEqual(box.width, 30.0)
        self.assertEqual(box.height, 35.0)

    def test_bbox_vacio(self):
        self.assertIsNone(BBox.from_points([]))

    def test_interseccion_y_solape(self):
        a = BBox(0, 0, 10, 10)
        b = BBox(5, 5, 15, 15)
        self.assertTrue(a.intersects(b))
        self.assertEqual(a.overlap_area(b), 25.0)
        self.assertFalse(a.intersects(BBox(20, 20, 30, 30)))

    def test_contiene(self):
        self.assertTrue(BBox(0, 0, 100, 100).contains(BBox(10, 10, 20, 20)))
        self.assertFalse(BBox(0, 0, 100, 100).contains(BBox(90, 10, 120, 20)))

    def test_vec2_distancias(self):
        self.assertEqual(Vec2(0, 0).manhattan_to(Vec2(3, 4)), 7)
        self.assertAlmostEqual(Vec2(0, 0).distance_to(Vec2(3, 4)), 5.0)


class TestFormatosDeHoja(unittest.TestCase):

    def test_altura_confirmada_129_de_129(self):
        """Evidencia: height = rows*rowsize + 20 en el 100 % de los folios."""
        for fmt in SHEET_FORMATS.values():
            self.assertEqual(fmt.height, fmt.rows * fmt.rowsize + 20)

    def test_zona_segura_excluye_cajetin(self):
        fmt = get_sheet_format("A3_17x8")
        self.assertEqual(fmt.width, 1020)
        self.assertEqual(fmt.usable_height, 640)
        self.assertEqual(fmt.height, 660)
        self.assertEqual(fmt.safe_area.y2, 640)

    def test_margen_reduce_la_zona_segura(self):
        fmt = get_sheet_format("A3_17x8")
        margen = 20
        safe = fmt.drawing_area.inset(margen)
        self.assertEqual(safe.x1, margen)
        self.assertEqual(safe.x2, 1020 - margen)

    def test_formato_desconocido_error(self):
        with self.assertRaises(KeyError):
            get_sheet_format("A9_99x99")


class TestCatalogo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG, library_path=FIXTURE_LIBRARY)

    def test_tiene_14_simbolos(self):
        self.assertEqual(len(self.catalog.type_keys()), 14)

    def test_comentario_no_es_un_simbolo(self):
        """Regresión v0.1: '_comment' se cargaba como si fuera un símbolo."""
        self.assertNotIn("_comment", self.catalog.type_keys())
        self.assertFalse(self.catalog.has("_comment"))

    def test_resuelve_simbolo_real(self):
        symbol = self.catalog.get("pv_cell")
        self.assertTrue(symbol.file_path.is_file())
        self.assertTrue(symbol.embed_type.startswith("embed://import/"))

    def test_extrae_terminales_con_orientacion(self):
        symbol = self.catalog.get("pv_cell")
        self.assertEqual(symbol.terminal_count, 4)
        self.assertEqual(symbol.terminals[0].orientation, "w")
        self.assertEqual(symbol.terminals[2].orientation, "e")

    def test_extrae_caja_envolvente_real(self):
        """La caja se calcula de la geometría real del .elmt, no de constantes."""
        symbol = self.catalog.get("pv_cell")
        self.assertLess(symbol.bounds.x1, 0)
        self.assertGreater(symbol.bounds.x2, 0)
        self.assertGreater(symbol.bounds.height, 20)

    def test_lee_dimensiones_y_hotspot(self):
        symbol = self.catalog.get("pv_cell")
        self.assertEqual(symbol.width, 70)
        self.assertEqual(symbol.height, 60)
        self.assertEqual(symbol.hotspot_x, 33)
        self.assertEqual(symbol.hotspot_y, 34)

    def test_tipo_inexistente_error_claro(self):
        with self.assertRaises(CatalogError):
            self.catalog.get("tipo_inventado")

    def test_biblioteca_inexistente_error_claro(self):
        with self.assertRaises(CatalogError):
            SymbolCatalog(CATALOG, library_path="C:/no/existe")


class TestEntradaSalida(unittest.TestCase):

    def test_carga_multi_folio(self):
        project = load_spec(BASE / "examples" / "proyecto_fv_588.json")
        self.assertEqual(len(project.folios), 18)

    def test_carga_formato_plano_heredado(self):
        project = load_spec(BASE / "examples" / "basic_circuit.json")
        self.assertEqual(len(project.folios), 1)
        self.assertEqual(len(project.folios[0].elements), 3)

    def test_roundtrip_sin_perdidas(self):
        """project → dict → project conserva todos los campos."""
        original = load_spec(BASE / "examples" / "proyecto_fv_588.json")
        data = project_to_dict(original)
        restored = project_from_dict(data)
        self.assertEqual(len(restored.folios), len(original.folios))
        for a, b in zip(original.folios, restored.folios, strict=True):
            self.assertEqual(a.title, b.title)
            self.assertEqual(a.order, b.order)
            self.assertEqual(len(a.elements), len(b.elements))
            self.assertEqual(len(a.connections), len(b.connections))
            self.assertEqual(len(a.texts), len(b.texts))
            self.assertEqual(len(a.shapes), len(b.shapes))

    def test_roundtrip_conserva_metadatos_de_folio(self):
        """Regresión v0.1: folio_to_dict perdía author, date e indexrev."""
        sheet = Sheet(title="T", author="AUTOR", indexrev="B", date="20261122")
        project = Project(title="P", folios=[sheet])
        restored = project_from_dict(project_to_dict(project))
        self.assertEqual(restored.folios[0].author, "AUTOR")
        self.assertEqual(restored.folios[0].indexrev, "B")
        self.assertEqual(restored.folios[0].date, "20261122")

    def test_ida_y_vuelta_a_archivo(self):
        import tempfile
        project = load_spec(BASE / "examples" / "basic_circuit.json")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spec.json"
            save_spec(project, path)
            restored = load_spec(path)
        self.assertEqual(len(restored.folios[0].elements), 3)

    def test_error_claro_para_campo_desconocido(self):
        data = {
            "project": {"title": "T"},
            "diagrams": [{
                "title": "F",
                "elements": [{"id": "A", "type": "lamp", "x": 1, "y": 1,
                              "color": "rojo"}],
            }],
        }
        with self.assertRaises(SpecError) as ctx:
            project_from_dict(data)
        self.assertIn("elements[0]", str(ctx.exception))

    def test_json_mal_formado(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as handle:
            handle.write("{no es json")
            path = Path(handle.name)
        self.addCleanup(path.unlink)
        with self.assertRaises(SpecError):
            load_spec(path)

    def test_archivo_inexistente(self):
        with self.assertRaises(SpecError):
            load_spec("no_existe.json")


if __name__ == "__main__":
    unittest.main()
