"""Exportador QElectroTech (.qet) — XML plano de QET 0.100.0.

Todo lo que se escribe aquí está respaldado por evidencia real (ver
``docs/QET_FORMAT_NOTES.md``). El exportador **no decide geometría**: se
limita a traducir el modelo a la representación nativa de QElectroTech.

Contrato XML (verificado por los tests y por el round-trip con QET):

.. code-block:: text

    <project title version="0.100.0">
      <properties> <newdiagrams> <diagram…>×N <collection>
    <diagram>
      <properties> <defaultconductor> <elements> <conductors> <inputs> <shapes>

Los ``id`` de terminal son **globales por folio** y reinician en cada folio
(evidencia §11). La ``<collection>`` es **una por proyecto** y contiene cada
símbolo usado **una sola vez** (evidencia §8).
"""

from __future__ import annotations

import datetime as _dt
import html
import os
import uuid as uuid_mod
import xml.etree.ElementTree as ET
from pathlib import Path

from ...core.catalog import (INSTANCE_FONT, ORIENTATION_LETTER_TO_NUM,
                              SymbolCatalog, SymbolDefinition)
from ...core.models import Component, Connection, Label, Project, Shape, Sheet
from ...core.sheet import SheetFormat, get_sheet_format

QET_VERSION = "0.100.0"

#: Plantilla HTML richtext de Qt observada en photovoltaique.qet (evidencia §6).
_HTML_TEMPLATE = (
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" '
    '"http://www.w3.org/TR/REC-html40/strict.dtd">\n'
    '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
    'p, li { white-space: pre-wrap; }\n'
    '</style></head>'
    '<body style=" font-family:\'Sans Serif\'; font-size:9pt; font-weight:0; '
    'font-style:normal;">\n'
    '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
    'margin-right:0px; -qt-block-indent:0; text-indent:0px;">{text}</p>'
    '</body></html>'
)

#: Atributos de <defaultconductor> observados (evidencia §5).
_DEFAULT_CONDUCTOR_ATTRS = {
    "dash-size": "2", "bus": "", "color2": "#000000", "text_color": "#000000",
    "bicolor": "false", "horizrotatetext": "0", "type": "multi", "num": "_",
    "displaytext": "1", "conductor_color": "", "conductor_section": "",
    "formula": "", "numsize": "7", "horizontal-alignment": "AlignBottom",
    "onetextperfolio": "0", "function": "", "vertirotatetext": "270",
    "tension_protocol": "", "condsize": "1", "cable": "",
    "vertical-alignment": "AlignRight",
}

#: Atributos de <conductor> observados (evidencia §4).
_CONDUCTOR_ATTRS = {
    "dash-size": "2", "x": "0", "bus": "", "color2": "#000000",
    "text_color": "#000000", "bicolor": "false", "horizrotatetext": "0",
    "type": "multi", "num": "", "displaytext": "1", "y": "0",
    "conductor_color": "", "conductor_section": "", "formula": "",
    "numsize": "7", "horizontal-alignment": "AlignBottom",
    "onetextperfolio": "0", "function": "", "freezeLabel": "false",
    "vertirotatetext": "270", "tension_protocol": "", "condsize": "1",
    "cable": "", "vertical-alignment": "AlignRight",
}


def _fmt(value: float) -> str:
    """Formatea un número como lo hace QET (sin ceros espurios)."""
    f = float(value)
    if f == int(f):
        return str(int(f))
    return repr(f)


def new_uuid() -> str:
    """UUID de instancia en el formato de QElectroTech: ``{xxxxxxxx-…}``."""
    return "{" + str(uuid_mod.uuid4()) + "}"


# --------------------------------------------------------------------------
# Piezas del XML
# --------------------------------------------------------------------------

def build_element(component: Component, symbol: SymbolDefinition,
                  instance_uuid: str, terminal_ids: list[int]) -> ET.Element:
    """Construye un ``<element>`` colocado (evidencia §3)."""
    el = ET.Element("element", {
        "uuid": instance_uuid,
        "orientation": str(component.orientation),
        "type": symbol.embed_type,
        "x": _fmt(component.x),
        "y": _fmt(component.y),
        "z": "10",
        "freezeLabel": "false",
        "prefix": symbol.prefix,
    })

    terms = ET.SubElement(el, "terminals")
    for i, port in enumerate(symbol.terminals):
        ET.SubElement(terms, "terminal", {
            "id": str(terminal_ids[i]),
            "orientation": ORIENTATION_LETTER_TO_NUM.get(port.orientation, "0"),
            "x": _fmt(port.x),
            "y": _fmt(port.y),
            "uuid": port.uuid,
            "type": "Generic",
            "name": port.name,
            "number": port.number,
            "nameHidden": "0",
        })

    ET.SubElement(el, "inputs")

    infos = ET.SubElement(el, "elementInformations")
    for name in ("location", "comment", "formula"):
        node = ET.SubElement(infos, "elementInformation", {"show": "1", "name": name})
        value = component.info_value(name)
        if value:
            node.text = value
    for name in ("designation", "description", "manufacturer",
                 "manufacturer_reference", "machine_manufacturer_reference",
                 "supplier", "plant", "unity", "quantity"):
        value = component.info_value(name)
        if value:
            node = ET.SubElement(infos, "elementInformation", {"show": "1", "name": name})
            node.text = value
    label_info = ET.SubElement(infos, "elementInformation",
                               {"show": "1", "name": "label"})
    label_info.text = component.resolved_label()

    dyn_texts = ET.SubElement(el, "dynamic_texts")
    dt = ET.SubElement(dyn_texts, "dynamic_elmt_text", {
        "frame": "false",
        "uuid": new_uuid(),
        "Halignment": "AlignLeft",
        "Valignment": "AlignTop",
        "rotation": "0",
        "text_from": "ElementInfo",
        "x": _fmt(symbol.label_pos[0]),
        "font": INSTANCE_FONT,
        "text_width": "-1",
        "keep_visual_rotation": "true",
        "y": _fmt(symbol.label_pos[1]),
    })
    ET.SubElement(dt, "text")
    info = ET.SubElement(dt, "info_name")
    info.text = "label"

    ET.SubElement(el, "texts_groups")
    return el


def build_conductor(element1_uuid: str, terminal1_uuid: str,
                    element2_uuid: str, terminal2_uuid: str,
                    num: str = "") -> ET.Element:
    """Construye un ``<conductor>`` (evidencia §4).

    QET **recalcula** el trazado entre las dos terminales: aquí no se escribe
    geometría de ruta (eso vive en el modelo y lo usan SVG y el validador).
    """
    attrs = dict(_CONDUCTOR_ATTRS)
    attrs.update({
        "element1": element1_uuid,
        "terminal1": terminal1_uuid,
        "element2": element2_uuid,
        "terminal2": terminal2_uuid,
        "num": num,
    })
    cond = ET.Element("conductor", attrs)
    ET.SubElement(cond, "sequentialNumbers")
    return cond


def wrap_html(text: str) -> str:
    """Envuelve el texto plano en la plantilla richtext de Qt ( escapado )."""
    return _HTML_TEMPLATE.replace("{text}", html.escape(text, quote=False))


def build_text(label: Label) -> ET.Element:
    """Construye un ``<input>`` de texto independiente (evidencia §6)."""
    size = str(label.size)
    return ET.Element("input", {
        "rotation": str(label.rotation),
        "x": _fmt(label.x),
        "font": f"Sans Serif,{size},-1,5,0,0,0,0,0,0,normal",
        "text": wrap_html(label.text),
        "y": _fmt(label.y),
        "tagg": "label",
        "size": size,
        "rotate": "true",
    })


def build_rectangle(shape: Shape) -> ET.Element:
    """Construye un ``<shape type="Rectangle">`` (evidencia §1)."""
    el = ET.Element("shape", {
        "x1": _fmt(shape.x1),
        "y1": _fmt(shape.y1),
        "x2": _fmt(shape.x2),
        "y2": _fmt(shape.y2),
        "type": "Rectangle",
        "is_movable": "1",
        "z": "0",
        "closed": "0",
        "rx": "0",
        "ry": "0",
    })
    ET.SubElement(el, "pen", {
        "style": "DashLine" if shape.dash else "SolidLine",
        "widthF": _fmt(shape.width),
        "color": shape.color,
    })
    if shape.fill:
        ET.SubElement(el, "brush", {"style": "SolidPattern", "color": shape.fill})
    else:
        ET.SubElement(el, "brush", {"style": "NoBrush", "color": shape.color})
    return el


# --------------------------------------------------------------------------
# Folio
# --------------------------------------------------------------------------

class DiagramBuildResult:
    """Resultado de construir un folio: XML + métricas + identidad."""

    def __init__(self) -> None:
        self.xml: ET.Element | None = None
        self.order: int = 1
        self.title: str = ""
        self.element_uuids: dict[str, str] = {}
        self.element_count: int = 0
        self.conductor_count: int = 0
        self.text_count: int = 0


def _diagram_attrs(sheet: Sheet, author: str, fmt: SheetFormat) -> dict:
    date = sheet.date or _dt.date.today().strftime("%Y%m%d")
    order = sheet.order if sheet.order is not None else 1
    return {
        "title": sheet.title,
        "version": QET_VERSION,
        "author": author,
        "date": date,
        "order": str(order),
        "cols": str(fmt.cols),
        "rows": str(fmt.rows),
        "colsize": str(fmt.colsize),
        "rowsize": str(fmt.rowsize),
        "height": str(int(fmt.height)),
        "displaycols": "true",
        "displayrows": "true",
        "displayAt": "bottom",
        "folio": "%id/%total",
        "auto_page_num": "",
        "indexrev": sheet.indexrev,
        "locmach": "",
        "plant": "",
        "filename": "",
        "freezeNewConductor": "false",
        "freezeNewElement": "false",
    }


def build_diagram(sheet: Sheet, catalog: SymbolCatalog,
                  project_author: str = "") -> DiagramBuildResult:
    """Construye un folio completo a partir de un :class:`Sheet`."""
    result = DiagramBuildResult()
    result.order = sheet.order if sheet.order is not None else 1
    result.title = sheet.title
    author = sheet.author or project_author
    fmt = get_sheet_format(sheet.sheet_format)

    diagram = ET.Element("diagram", _diagram_attrs(sheet, author, fmt))

    props = ET.SubElement(diagram, "properties")
    for name in ("date", "title", "filename", "folio", "author"):
        ET.SubElement(props, "property", {"show": "1", "name": name})

    ET.SubElement(diagram, "defaultconductor", dict(_DEFAULT_CONDUCTOR_ATTRS))

    # --- elementos (los id de terminal son globales POR FOLIO: evidencia §11)
    elements_wrap = ET.SubElement(diagram, "elements")
    terminal_id_counter = 0
    for component in sheet.elements:
        symbol = catalog.get(component.type)
        instance_uuid = new_uuid()
        n_terms = len(symbol.terminals)
        terminal_ids = list(range(terminal_id_counter, terminal_id_counter + n_terms))
        terminal_id_counter += n_terms
        elements_wrap.append(
            build_element(component, symbol, instance_uuid, terminal_ids))
        result.element_uuids[component.id] = instance_uuid
        result.element_count += 1

    # --- conductores
    conductors_wrap = ET.SubElement(diagram, "conductors")
    by_id = {el.id: el for el in sheet.elements}
    for connection in sheet.connections:
        src_spec, dst_spec = by_id[connection.from_id], by_id[connection.to_id]
        src_sym = catalog.get(src_spec.type)
        dst_sym = catalog.get(dst_spec.type)
        conductors_wrap.append(build_conductor(
            result.element_uuids[connection.from_id],
            src_sym.terminals[connection.from_terminal].uuid,
            result.element_uuids[connection.to_id],
            dst_sym.terminals[connection.to_terminal].uuid,
            connection.number,
        ))
        result.conductor_count += 1

    # --- textos independientes
    inputs_wrap = ET.SubElement(diagram, "inputs")
    for text_spec in sheet.texts:
        inputs_wrap.append(build_text(text_spec))
        result.text_count += 1

    # --- bloques gráficos
    shapes_wrap = ET.SubElement(diagram, "shapes")
    for shape_spec in sheet.shapes:
        shapes_wrap.append(build_rectangle(shape_spec))

    result.xml = diagram
    return result


# --------------------------------------------------------------------------
# Proyecto
# --------------------------------------------------------------------------

def _project_properties(project: Project) -> ET.Element:
    today = _dt.date.today()
    now = _dt.datetime.now()
    props = ET.Element("properties")
    values = {
        "saveddate": today.strftime("%d/%m/%Y"),
        "savedtime": now.strftime("%H:%M"),
        "saveddate-eu": today.strftime("%d-%m-%Y"),
        "saveddate-us": today.strftime("%Y-%m-%d"),
        "savedfilename": Path(project.filename or "proyecto").stem,
        "savedfilepath": project.filename or "",
    }
    for name, value in values.items():
        node = ET.SubElement(props, "property", {"show": "1", "name": name})
        node.text = value
    return props


def _newdiagrams(fmt: SheetFormat) -> ET.Element:
    nd = ET.Element("newdiagrams")
    ET.SubElement(nd, "border", {
        "rows": str(fmt.rows), "cols": str(fmt.cols),
        "displaycols": "true", "displayrows": "true",
        "rowsize": str(fmt.rowsize), "colsize": str(fmt.colsize),
    })
    ET.SubElement(nd, "inset", {
        "plant": "", "date": "", "title": "", "auto_page_num": "",
        "locmach": "", "filename": "", "displayAt": "bottom",
        "folio": "%id/%total", "indexrev": "", "version": "", "author": "",
    })
    ET.SubElement(nd, "conductors", {
        key: value for key, value in _DEFAULT_CONDUCTOR_ATTRS.items()
    })
    ET.SubElement(nd, "report", {"label": "%f-%l%c"})
    xrefs = ET.SubElement(nd, "xrefs")
    ET.SubElement(xrefs, "xref", {
        "snapto": "label", "switchprefix": "", "displayhas": "cross",
        "master_label": "%f-%l%c", "offset": "40", "delayprefix": "",
        "type": "coil", "showpowerctc": "true", "xrefpos": "AlignTop",
        "slave_label": "(%f-%l%c)", "powerprefix": "",
    })
    ET.SubElement(nd, "conductors_autonums",
                  {"freeze_new_conductors": "false", "current_autonum": ""})
    ET.SubElement(nd, "folio_autonums")
    ET.SubElement(nd, "element_autonums",
                  {"freeze_new_elements": "false", "current_autonum": ""})
    return nd


def _collection(used_symbols: list[SymbolDefinition]) -> ET.Element:
    """``<collection>``: biblioteca embebida (evidencia §8).

    Mapeo: ``embed://import/a/b/x.elmt`` → ``category "import" > "a" > "b" >
    element name="x.elmt"`` con la **copia literal** del ``.elmt``.
    """
    collection = ET.Element("collection")
    root_cat = ET.SubElement(collection, "category", {"name": "import"})
    for symbol in used_symbols:
        parts = symbol.elmt_path.split("/")
        dirs, filename = parts[:-1], parts[-1]
        node = root_cat
        for directory in dirs:
            existing = next((c for c in node
                             if c.tag == "category" and c.get("name") == directory),
                            None)
            if existing is None:
                existing = ET.SubElement(node, "category", {"name": directory})
            node = existing
        wrapper = ET.SubElement(node, "element", {"name": filename})
        wrapper.append(ET.parse(symbol.file_path).getroot())
    return collection


def build_project(project: Project, catalog: SymbolCatalog):
    """Construye el árbol XML completo.

    Returns
    -------
    (root, results)
        ``root`` es el ``<project>``; ``results`` es la lista de
        :class:`DiagramBuildResult` (uno por folio).
    """
    root = ET.Element("project", {"title": project.title, "version": QET_VERSION})
    root.append(_project_properties(project))
    default_fmt = get_sheet_format(
        project.folios[0].sheet_format if project.folios else None)
    root.append(_newdiagrams(default_fmt))

    results = []
    for sheet in project.folios:
        result = build_diagram(sheet, catalog, project.author)
        results.append(result)
        root.append(result.xml)

    used = catalog.used_symbols([el.type for el in project.elements])
    root.append(_collection(used))
    return root, results


def export_project(root: ET.Element, output_path: str | Path) -> Path:
    """Serializa a ``.qet``: XML plano UTF-8, sin BOM ni declaración.

    La escritura es **atómica** (archivo temporal + ``replace``) para no
    dejar un proyecto corrupto si el proceso se interrumpe.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    try:
        ET.indent(tree, space="    ")
    except AttributeError:      # pragma: no cover - Python < 3.9
        pass
    xml_text = ET.tostring(root, encoding="unicode")
    tmp_path = output_path.with_name(output_path.name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(xml_text)
    os.replace(tmp_path, output_path)
    return output_path


__all__ = [
    "DiagramBuildResult",
    "QET_VERSION",
    "build_conductor",
    "build_diagram",
    "build_element",
    "build_project",
    "build_rectangle",
    "build_text",
    "export_project",
    "new_uuid",
    "wrap_html",
]
