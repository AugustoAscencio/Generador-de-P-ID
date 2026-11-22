"""Tests del motor geométrico (Fase 3): rejilla, métrica, colisiones,
colocación de etiquetas, routing Manhattan, auto-layout, SVG y auditoría
estética.
"""

from __future__ import annotations

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))

from qetgen.config import QetGenConfig                                  # noqa: E402
from qetgen.core.catalog import SymbolCatalog, default_catalog_path     # noqa: E402
from qetgen.core.geometry import BBox, rotate_point, rotated_bbox       # noqa: E402
from qetgen.core.io import load_spec                                    # noqa: E402
from qetgen.core.models import (Connection, Component, Label, Project,  # noqa: E402
                                Shape, Sheet)
from qetgen.core.sheet import get_sheet_format                          # noqa: E402
from qetgen.exporters.svg import sheet_to_svg                           # noqa: E402
from qetgen.layout.autolayout import auto_layout, compute_layers        # noqa: E402
from qetgen.layout.collision import (analyze_sheet, detect_collisions,  # noqa: E402
                                     overlap_area, sheet_occupants)
from qetgen.layout.grid import Grid                                     # noqa: E402
from qetgen.layout.labels import place_labels                           # noqa: E402
from qetgen.layout.placement import (component_bounds, component_ink_bounds,
                                     terminal_position)                  # noqa: E402
from qetgen.layout.router import ManhattanRouter, route_sheet           # noqa: E402
from qetgen.layout.textmetrics import TextMeasurer                      # noqa: E402
from qetgen.validation.aesthetics import validate_aesthetics            # noqa: E402

CATALOG = default_catalog_path()


class TestGrid(unittest.TestCase):

    def test_snap_cuantiza(self):
        grid = Grid(size=10)
        self.assertEqual(grid.snap(103), 100)
        self.assertEqual(grid.snap(107), 110)
        self.assertEqual(grid.snap(-3), 0)

    def test_snap_sin_ruido_binario(self):
        grid = Grid(size=10)
        self.assertEqual(grid.snap(300), 300.0)

    def test_snap_desactivado_no_altera(self):
        grid = Grid(size=10, enabled=False)
        self.assertEqual(grid.snap(103.7), 103.7)

    def test_is_aligned(self):
        grid = Grid(size=10)
        self.assertTrue(grid.is_aligned(120))
        self.assertFalse(grid.is_aligned(123))

    def test_snap_box_expande(self):
        box = BBox(11, 11, 19, 19)
        snapped = Grid(size=10).snap_box(box)
        self.assertEqual(snapped.as_tuple(), (10.0, 10.0, 20.0, 20.0))

    def test_point_de_celda(self):
        self.assertEqual(Grid(size=10).point(3, 4), (30, 40))


class TestTextMetrics(unittest.TestCase):

    def test_medida_proporcional_al_texto(self):
        measurer = TextMeasurer()
        short = measurer.measure("AB")
        long = measurer.measure("A" * 20)
        self.assertGreater(long.width, short.width)
        self.assertEqual(short.height, long.height)

    def test_multilinea(self):
        box = TextMeasurer().measure("una\ndos\ntres")
        self.assertEqual(box.lines, 3)

    def test_rotacion_intercambia_ejes(self):
        measurer = TextMeasurer()
        normal = measurer.measure("texto largo")
        rotated = measurer.measure("texto largo", rotation=90)
        self.assertAlmostEqual(rotated.width, normal.height)
        self.assertAlmostEqual(rotated.height, normal.width)

    def test_alineacion_del_ancla(self):
        measurer = TextMeasurer()
        left, _, right, _ = measurer.measure_box("hola", 100, 50)
        self.assertAlmostEqual(left, 100)
        center, _, _, _ = measurer.measure_box("hola", 100, 50, align="center")
        right_anchor, _, right_edge, _ = measurer.measure_box(
            "hola", 100, 50, align="right")
        self.assertLess(center, left)
        # Alineación a la derecha: el ancla (100) queda en el BORDE derecho.
        self.assertAlmostEqual(right_edge, 100)
        self.assertLess(right_anchor, right_edge)


class TestRotacion(unittest.TestCase):

    def test_rota_norte_a_este(self):
        """Convención QET: orientation 1 = 90° en sentido horario."""
        self.assertEqual(rotate_point(0, -10, 0), (0, -10))
        self.assertEqual(rotate_point(0, -10, 1), (10, 0))
        self.assertEqual(rotate_point(0, -10, 2), (0, 10))
        self.assertEqual(rotate_point(0, -10, 3), (-10, 0))

    def test_cuatro_cuartos_vuelven_al_origen(self):
        x, y = 7, -13
        rx, ry = x, y
        for _ in range(4):
            rx, ry = rotate_point(rx, ry, 1)
        self.assertAlmostEqual(rx, x)
        self.assertAlmostEqual(ry, y)

    def test_rotated_bbox(self):
        box = BBox(-10, -20, 10, 20)
        rotated = rotated_bbox(box, 1)
        self.assertAlmostEqual(rotated.width, 40)
        self.assertAlmostEqual(rotated.height, 20)


class TestColocacion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG)

    def test_tinta_dentro_del_slot_en_los_14_simbolos(self):
        """Evidencia: las primitivas reales caben en la caja declarada."""
        for key in self.catalog.type_keys():
            symbol = self.catalog.get(key)
            self.assertTrue(symbol.placement_bounds.contains(symbol.ink_bounds),
                            f"{key}: la tinta se sale del slot declarado")

    def test_caja_reservada_usa_el_slot(self):
        symbol = self.catalog.get("pv_cell")
        component = Component(id="P1", type="pv_cell", x=100, y=200)
        box = component_bounds(component, symbol)
        self.assertAlmostEqual(box.x1, 100 - symbol.hotspot_x)
        self.assertAlmostEqual(box.y1, 200 - symbol.hotspot_y)
        self.assertAlmostEqual(box.width, symbol.width)
        self.assertAlmostEqual(box.height, symbol.height)

    def test_caja_de_tinta_es_menor_que_la_reservada(self):
        """La tinta real de una borne es mucho menor que su espacio reservado."""
        symbol = self.catalog.get("dc_terminal")
        component = Component(id="X1", type="dc_terminal", x=0, y=0)
        self.assertLess(component_ink_bounds(component, symbol).width,
                        component_bounds(component, symbol).width)

    def test_rotacion_del_componente(self):
        symbol = self.catalog.get("pv_cell")
        component = Component(id="P1", type="pv_cell", x=0, y=0, orientation=1)
        box = component_bounds(component, symbol)
        self.assertAlmostEqual(box.width, symbol.height)
        self.assertAlmostEqual(box.height, symbol.width)

    def test_terminal_rota_con_el_simbolo(self):
        symbol = self.catalog.get("dc_terminal")
        component = Component(id="X1", type="dc_terminal", x=100, y=100)
        straight = terminal_position(component, symbol, 0)
        turned = terminal_position(
            Component(id="X1", type="dc_terminal", x=100, y=100, orientation=1),
            symbol, 0)
        self.assertAlmostEqual(straight[0], 100)
        self.assertAlmostEqual(turned[0], 110)     # el offset (0,-10) gira a (10,0)


class TestColisiones(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG)
        cls.measurer = TextMeasurer()

    def test_contencion_no_es_solape(self):
        """Un texto dentro de un bloque es intencional: no se reporta."""
        block = BBox(0, 0, 100, 100)
        inside = BBox(10, 10, 50, 20)
        self.assertEqual(overlap_area(block, inside), 0.0)

    def test_solape_parcial_si_se_reporta(self):
        a = BBox(0, 0, 100, 100)
        b = BBox(90, 10, 150, 30)
        self.assertGreater(overlap_area(a, b), 0)

    def test_solo_contacto_no_es_solape(self):
        a = BBox(0, 0, 10, 10)
        b = BBox(10, 0, 20, 10)
        self.assertEqual(overlap_area(a, b), 0.0)

    def test_simbolo_sobre_simbolo_es_error(self):
        sheet = Sheet(title="F", elements=[
            Component(id="A", type="lamp", x=100, y=100),
            Component(id="B", type="lamp", x=100, y=100),
        ])
        report = analyze_sheet(sheet, self.catalog, self.measurer)
        self.assertTrue(report.errors)
        self.assertEqual(report.errors[0].kind, "component-component")

    def test_etiqueta_propia_no_choca_consu_propio_simbolo(self):
        sheet = Sheet(title="F", elements=[
            Component(id="A", type="lamp", x=100, y=100, label="A"),
        ])
        report = analyze_sheet(sheet, self.catalog, self.measurer)
        self.assertFalse([c for c in report.collisions
                          if c.a.endswith(":label") or c.b.endswith(":label")])

    def test_texto_sobre_bloque_no_se_reporta(self):
        """Los títulos apoyados en el borde de un bloque son estilo de dibujo."""
        sheet = Sheet(title="F", shapes=[
            Shape(x1=0, y1=0, x2=200, y2=100, role="group"),
        ], texts=[Label(x=10, y=90, text="TITULO")])
        report = analyze_sheet(sheet, self.catalog, self.measurer)
        self.assertFalse([c for c in report.collisions if c.kind == "text-shape"])

    def test_bloques_decorativos_no_generan_colisiones(self):
        sheet = Sheet(title="F", shapes=[
            Shape(x1=0, y1=0, x2=200, y2=100, role="background"),
        ], texts=[Label(x=10, y=10, text="TEXTO")])
        report = analyze_sheet(sheet, self.catalog, self.measurer)
        self.assertEqual(report.collisions, [])

    def test_ocupantes_de_un_folio_real(self):
        project = load_spec(BASE / "examples" / "proyecto_fv_588.json")
        sheet = project.folios[2]
        occupants = sheet_occupants(sheet, self.catalog, self.measurer)
        # 10 símbolos + 10 etiquetas + 10 textos + 1 bloque
        self.assertEqual(len(occupants), 31)


class TestEtiquetas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG)
        cls.measurer = TextMeasurer()

    def test_coloca_una_etiqueta_libre(self):
        sheet = Sheet(title="F", elements=[
            Component(id="A", type="lamp", x=200, y=200, label="A1"),
        ])
        placed = place_labels(sheet, self.catalog, self.measurer)
        self.assertEqual(len(placed), 1)
        self.assertTrue(placed[0].free)
        self.assertIn(placed[0].side, ("e", "w", "n", "s", "ne", "nw", "se", "sw"))

    def test_evita_la_primera_posicion_ocupada(self):
        sheet = Sheet(title="F", elements=[
            Component(id="A", type="lamp", x=200, y=200, label="A1"),
        ])
        occupied = [BBox(200, 150, 400, 260)]      # tapa la posición "este"
        placed = place_labels(sheet, self.catalog, self.measurer,
                              occupied=occupied)
        self.assertNotEqual(placed[0].side, "e")


class TestRouter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG)

    def _sheet(self):
        return Sheet(
            title="F",
            elements=[
                Component(id="A", type="lamp", x=120, y=300),
                Component(id="B", type="lamp", x=600, y=300),
            ],
            connections=[Connection(from_id="A", to_id="B")])

    def test_trae_una_ruta_ortogonal(self):
        sheet = self._sheet()
        fmt = get_sheet_format("A3_17x8")
        routed, results = route_sheet(sheet, self.catalog, Grid(), fmt.drawing_area)
        self.assertTrue(results[0].ok)
        points = results[0].waypoints
        self.assertGreaterEqual(len(points), 2)
        for a, b in zip(points, points[1:]):
            horizontal = abs(a[1] - b[1]) < 1e-6
            vertical = abs(a[0] - b[0]) < 1e-6
            self.assertTrue(horizontal or vertical,
                            f"el tramo {a}->{b} no es ortogonal")

    def test_los_waypoints_se_guardan_en_la_conexion(self):
        sheet = self._sheet()
        fmt = get_sheet_format("A3_17x8")
        routed, _ = route_sheet(sheet, self.catalog, Grid(), fmt.drawing_area)
        self.assertTrue(routed.connections[0].waypoints)

    def test_la_conexion_bloqueada_conserva_su_ruta(self):
        sheet = self._sheet()
        sheet.connections[0].locked = True
        sheet.connections[0].waypoints = [(0.0, 0.0), (10.0, 0.0)]
        fmt = get_sheet_format("A3_17x8")
        routed, results = route_sheet(sheet, self.catalog, Grid(), fmt.drawing_area)
        self.assertEqual(routed.connections[0].waypoints, [(0.0, 0.0), (10.0, 0.0)])
        self.assertIn("locked", results[0].message)

    def test_no_hay_ruta_si_el_espacio_esta_bloqueado(self):
        router = ManhattanRouter(
            bounds=BBox(0, 0, 200, 200), grid=Grid(size=10),
            obstacles=[BBox(0, 0, 200, 200)])
        result = router.route((10, 10), (190, 190))
        self.assertFalse(result.ok)

    def test_evita_los_obstaculos(self):
        """La ruta rodea un obstáculo que no toca los bordes del área."""
        obstacle = BBox(80, 0, 120, 160)      # deja un paso libre abajo
        router = ManhattanRouter(
            bounds=BBox(0, 0, 200, 200), grid=Grid(size=10),
            obstacles=[obstacle])
        result = router.route((10, 100), (190, 100))
        self.assertTrue(result.ok)
        for a, b in zip(result.waypoints, result.waypoints[1:]):
            if abs(a[1] - b[1]) < 1e-6:      # tramo horizontal
                self.assertFalse(
                    obstacle.y1 <= a[1] <= obstacle.y2
                    and min(a[0], b[0]) < obstacle.x2
                    and max(a[0], b[0]) > obstacle.x1,
                    "la ruta atraviesa el obstáculo")

    def test_sin_ruta_si_el_obstaculo_bloquea_todo(self):
        """Un obstáculo que ocupa toda la altura deja el folio sin paso."""
        router = ManhattanRouter(
            bounds=BBox(0, 0, 200, 200), grid=Grid(size=10),
            obstacles=[BBox(80, 0, 120, 200)])
        result = router.route((10, 100), (190, 100))
        self.assertFalse(result.ok)
        self.assertIn("sin ruta", result.message)

    def test_evita_otro_conductor_registrado(self):
        """Un conductor ya trazado penaliza el cruce, pero no lo impide."""
        router = ManhattanRouter(bounds=BBox(0, 0, 200, 200), grid=Grid(size=10))
        # Conductor vertical que barra toda la altura: cruzarlo es inevitable.
        router.register_route([(100, 0), (100, 200)])
        result = router.route((10, 100), (190, 100))
        self.assertTrue(result.ok)
        self.assertGreater(result.crossings, 0)

    def test_los_paralelos_se_penalizan(self):
        """Dos cables paralelos demasiado juntos se separan."""
        router = ManhattanRouter(bounds=BBox(0, 0, 200, 200), grid=Grid(size=10))
        router.register_route([(0, 50), (200, 50)])
        result = router.route((10, 100), (190, 100))
        self.assertTrue(result.ok)
        ys = {round(y) for _, y in result.waypoints}
        self.assertNotIn(50, ys)      # no se pega al conductor existente


class TestAutoLayout(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG)

    def test_calcula_capas_por_el_grafo(self):
        sheet = Sheet(title="F", elements=[
            Component(id="A", type="lamp", x=0, y=0),
            Component(id="B", type="lamp", x=0, y=0),
            Component(id="C", type="lamp", x=0, y=0),
        ], connections=[Connection(from_id="A", to_id="B"),
                        Connection(from_id="B", to_id="C")])
        layers = compute_layers(sheet)
        self.assertEqual(layers["A"], 0)
        self.assertEqual(layers["B"], 1)
        self.assertEqual(layers["C"], 2)

    def test_respeta_los_bloqueados(self):
        """Modo híbrido: un elemento con locked:true no se mueve."""
        sheet = Sheet(title="F", elements=[
            Component(id="A", type="lamp", x=123, y=456, locked=True),
            Component(id="B", type="lamp", x=200, y=100),
        ])
        fmt = get_sheet_format("A3_17x8")
        updated, report = auto_layout(sheet, self.catalog, Grid(), fmt.drawing_area)
        self.assertEqual(updated.elements[0].x, 123)
        self.assertEqual(updated.elements[0].y, 456)
        self.assertIn("A", report.kept_locked)

    def test_informa_de_lo_movido(self):
        sheet = Sheet(title="F", elements=[
            Component(id="A", type="lamp", x=123, y=456),
            Component(id="B", type="lamp", x=200, y=100),
        ])
        fmt = get_sheet_format("A3_17x8")
        updated, report = auto_layout(sheet, self.catalog, Grid(), fmt.drawing_area)
        self.assertTrue(report.moved)
        old, new = report.moved[0][1], report.moved[0][2]
        self.assertNotEqual(old, new)
        self.assertTrue(updated.layout_applied)

    def test_el_resultado_no_tiene_simbolos_solapados(self):
        sheet = Sheet(title="F", elements=[
            Component(id=f"E{i}", type="lamp", x=100 + i, y=100 + i)
            for i in range(6)
        ])
        fmt = get_sheet_format("A3_17x8")
        updated, _ = auto_layout(sheet, self.catalog, Grid(), fmt.drawing_area)
        report = analyze_sheet(updated, self.catalog, TextMeasurer())
        self.assertEqual(report.errors, [])

    def test_las_coordenadas_resultantes_estan_alineadas(self):
        sheet = Sheet(title="F", elements=[
            Component(id=f"E{i}", type="lamp", x=123 + i, y=457 + i)
            for i in range(4)
        ])
        fmt = get_sheet_format("A3_17x8")
        updated, _ = auto_layout(sheet, self.catalog, Grid(size=10),
                                 fmt.drawing_area)
        for component in updated.elements:
            self.assertEqual(component.x % 10, 0)
            self.assertEqual(component.y % 10, 0)


class TestSvg(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG)
        cls.project = load_spec(BASE / "examples" / "proyecto_fv_588.json")

    def test_svg_valido(self):
        svg = sheet_to_svg(self.project.folios[2], self.catalog)
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))

    def test_dibuja_los_simbolos_reales(self):
        """El SVG dibuja las primitivas reales del .elmt, no aproximaciones."""
        svg = sheet_to_svg(self.project.folios[2], self.catalog)
        self.assertIn('<g id="PV-01"', svg)
        self.assertIn("<polygon", svg)          # primitiva real del pv_cell
        self.assertIn("<ellipse", svg)          # primitiva real de la borne
        self.assertIn(">PV-01</text>", svg)     # etiqueta del componente
        self.assertNotIn("TODO", svg)

    def test_dibuja_las_rutas_calculadas(self):
        sheet = self.project.folios[2]
        fmt = get_sheet_format(sheet.sheet_format)
        routed, _ = route_sheet(sheet, self.catalog, Grid(), fmt.drawing_area)
        svg = sheet_to_svg(routed, self.catalog, fmt, show_routes=True)
        self.assertEqual(svg.count("<polyline"), len(sheet.connections))

    def test_escapa_el_texto(self):
        """El SVG debe escapar el HTML: & < > no pueden romper el XML."""
        sheet = Sheet(title="F", texts=[Label(x=10, y=10, text="A & B < C")])
        svg = sheet_to_svg(sheet, self.catalog)
        amp = chr(38)          # "&" sin depender del escapado del editor
        escaped = f"A {amp}amp; B {amp}lt; C"
        self.assertIn(escaped, svg)
        self.assertNotIn("A & B < C", svg)
        ET.fromstring(svg)      # sigue siendo XML válido


class TestAuditoriaEstetica(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = SymbolCatalog(CATALOG)
        cls.config = QetGenConfig()

    def test_detecta_texto_que_desborda(self):
        sheet = Sheet(title="F", texts=[
            Label(x=900, y=100, text="UN TEXTO MUY LARGO QUE NO CABE EN EL FOLIO"),
        ])
        project = Project(title="P", folios=[sheet])
        report = validate_aesthetics(project, self.catalog, self.config)
        codes = [i.code for i in report.errors]
        self.assertIn("OUT_OF_SHEET", codes)

    def test_detecta_simbolos_superpuestos(self):
        sheet = Sheet(title="F", elements=[
            Component(id="A", type="lamp", x=200, y=200),
            Component(id="B", type="lamp", x=200, y=200),
        ])
        project = Project(title="P", folios=[sheet])
        report = validate_aesthetics(project, self.catalog, self.config)
        self.assertTrue([i for i in report.errors if i.code == "SYMBOL_OVERLAP"])

    def test_folio_vacio_es_informativo(self):
        project = Project(title="P", folios=[Sheet(title="Vacío")])
        report = validate_aesthetics(project, self.catalog, self.config)
        self.assertTrue([i for i in report.infos if i.code == "EMPTY_SHEET"])

    def test_informe_serializable(self):
        import json
        project = load_spec(BASE / "examples" / "proyecto_fv_588.json")
        report = validate_aesthetics(project, self.catalog, self.config)
        json.dumps(report.as_dict())

    def test_el_proyecto_real_no_tiene_simbolos_solapados(self):
        """El caso FV 588 tiene el layout manual limpio a nivel de símbolos."""
        project = load_spec(BASE / "examples" / "proyecto_fv_588.json")
        report = validate_aesthetics(project, self.catalog, self.config)
        self.assertEqual([i for i in report.errors if i.code == "SYMBOL_OVERLAP"], [])


if __name__ == "__main__":
    unittest.main()
