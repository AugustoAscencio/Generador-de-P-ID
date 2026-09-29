"""diagram.py — Construcción de un <diagram> (folio).

Estructura y atributos copiados de folios reales 0.100.0
(docs/QET_FORMAT_NOTES.md §5): properties, defaultconductor, elements,
conductors, inputs, shapes — en ese orden observado.

Los IDs de terminal son GLOBALES POR FOLIO (evidencia §11): cada folio
reinicia su contador en 0, igual que hacen los archivos reales.
"""

from __future__ import annotations

import datetime as _dt
import xml.etree.ElementTree as ET

from . import conductors as conductors_mod
from . import elements as elements_mod
from . import shapes as shapes_mod
from . import text as text_mod


def _diagram_attrs(folio, author: str) -> dict:
    date = folio.date or _dt.date.today().strftime("%Y%m%d")
    order = folio.order if folio.order is not None else 1
    return {
        "title": folio.title,
        "version": "0.100.0",
        "author": author,
        "date": date,
        "order": str(order),
        "cols": "17",
        "rows": "8",
        "colsize": "60",
        "rowsize": "80",
        "height": "660",
        "displaycols": "true",
        "displayrows": "true",
        "displayAt": "bottom",
        "folio": "%id/%total",
        "auto_page_num": "",
        "indexrev": folio.indexrev,
        "locmach": "",
        "plant": "",
        "filename": "",
        "freezeNewConductor": "false",
        "freezeNewElement": "false",
    }


# <defaultconductor>: set de atributos observado en photovoltaique.qet
_DEFAULT_CONDUCTOR_ATTRS = {
    "dash-size": "2",
    "bus": "",
    "color2": "#000000",
    "text_color": "#000000",
    "bicolor": "false",
    "horizrotatetext": "0",
    "type": "multi",
    "num": "_",
    "displaytext": "1",
    "conductor_color": "",
    "conductor_section": "",
    "formula": "",
    "numsize": "7",
    "horizontal-alignment": "AlignBottom",
    "onetextperfolio": "0",
    "function": "",
    "vertirotatetext": "270",
    "tension_protocol": "",
    "condsize": "1",
    "cable": "",
    "vertical-alignment": "AlignRight",
}


class DiagramBuildResult:
    def __init__(self):
        self.xml: ET.Element | None = None
        self.order: int = 1
        self.title: str = ""
        self.element_uuids: dict[str, str] = {}      # id del modelo -> uuid instancia
        self.element_count = 0
        self.conductor_count = 0
        self.text_count = 0


def build_diagram(folio, catalog, project_author: str = "") -> DiagramBuildResult:
    """Construye un folio completo a partir de un FolioSpec y el catálogo."""
    result = DiagramBuildResult()
    result.order = folio.order if folio.order is not None else 1
    result.title = folio.title
    author = folio.author or project_author

    diagram = ET.Element("diagram", _diagram_attrs(folio, author))

    # <properties> — visibilidad de campos del cartucho (observado)
    props = ET.SubElement(diagram, "properties")
    for name in ("date", "title", "filename", "folio", "author"):
        ET.SubElement(props, "property", {"show": "1", "name": name})

    ET.SubElement(diagram, "defaultconductor", dict(_DEFAULT_CONDUCTOR_ATTRS))

    # --- elementos ---
    elements_wrap = ET.SubElement(diagram, "elements")
    terminal_id_counter = 0                      # GLOBAL POR FOLIO (evidencia §11)
    for el_spec in folio.elements:
        symbol = catalog.get(el_spec.type)
        instance_uuid = elements_mod.new_uuid()
        n_terms = len(symbol.terminals)
        terminal_ids = list(range(terminal_id_counter, terminal_id_counter + n_terms))
        terminal_id_counter += n_terms
        elements_wrap.append(
            elements_mod.build_element(el_spec, symbol, instance_uuid, terminal_ids))
        result.element_uuids[el_spec.id] = instance_uuid
        result.element_count += 1

    # --- conductores (estilo UUID moderno) ---
    conductors_wrap = ET.SubElement(diagram, "conductors")
    by_id = {el.id: el for el in folio.elements}
    for cn in folio.connections:
        src_spec, dst_spec = by_id[cn.from_id], by_id[cn.to_id]
        src_sym = catalog.get(src_spec.type)
        dst_sym = catalog.get(dst_spec.type)
        conductors_wrap.append(conductors_mod.build_conductor(
            result.element_uuids[cn.from_id], src_sym.terminals[cn.from_terminal].uuid,
            result.element_uuids[cn.to_id], dst_sym.terminals[cn.to_terminal].uuid,
        ))
        result.conductor_count += 1

    # --- textos independientes ---
    inputs_wrap = ET.SubElement(diagram, "inputs")
    for tx_spec in folio.texts:
        inputs_wrap.append(text_mod.build_text(tx_spec))
        result.text_count += 1

    # --- bloques gráficos (shapes) ---
    shapes_wrap = ET.SubElement(diagram, "shapes")
    for sh_spec in folio.shapes:
        shapes_wrap.append(shapes_mod.build_rectangle(sh_spec))

    result.xml = diagram
    return result
