"""project.py — Construcción del <project> completo y exportación.

Copia la estructura real observada: properties, newdiagrams (defaults),
diagram(s) y la <collection> embebida con los .elmt usados por TODOS los
folios (una sola colección por proyecto — evidencia §11).
"""

from __future__ import annotations

import datetime as _dt
import xml.etree.ElementTree as ET
from pathlib import Path

from . import diagram as diagram_mod


def _project_properties(spec) -> ET.Element:
    """<properties> de proyecto (QET los reescribe al guardar)."""
    today = _dt.date.today()
    now = _dt.datetime.now()
    props = ET.Element("properties")
    values = {
        "saveddate": today.strftime("%d/%m/%Y"),
        "savedtime": now.strftime("%H:%M"),
        "saveddate-eu": today.strftime("%d-%m-%Y"),
        "saveddate-us": today.strftime("%Y-%m-%d"),
        "savedfilename": Path(spec.filename or "proyecto").stem,
        "savedfilepath": spec.filename or "",
    }
    for name, value in values.items():
        p = ET.SubElement(props, "property", {"show": "1", "name": name})
        p.text = value
    return props


def _newdiagrams(spec) -> ET.Element:
    """<newdiagrams>: defaults para folios nuevos (valores observados)."""
    nd = ET.Element("newdiagrams")
    ET.SubElement(nd, "border", {
        "rows": "8", "cols": "17",
        "displaycols": "true", "displayrows": "true",
        "rowsize": "80", "colsize": "60",
    })
    ET.SubElement(nd, "inset", {
        "plant": "", "date": "", "title": "", "auto_page_num": "",
        "locmach": "", "filename": "", "displayAt": "bottom",
        "folio": "%id/%total", "indexrev": "", "version": "", "author": "",
    })
    ET.SubElement(nd, "conductors", {
        "dash-size": "2", "bus": "", "color2": "#000000",
        "text_color": "#000000", "bicolor": "false", "type": "multi",
        "num": "_", "horizrotatetext": "0", "displaytext": "1",
        "conductor_color": "", "conductor_section": "", "formula": "",
        "numsize": "7", "horizontal-alignment": "AlignBottom",
        "onetextperfolio": "0", "function": "", "vertirotatetext": "270",
        "tension_protocol": "", "condsize": "1", "cable": "",
        "vertical-alignment": "AlignRight",
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


def _collection(used_symbols: list) -> ET.Element:
    """<collection>: biblioteca embebida con los .elmt usados.

    Mapeo confirmado: embed://import/a/b/x.elmt ->
    category "import" > category "a" > category "b" > element name="x.elmt".
    Una sola colección compartida por todos los folios (evidencia §11).
    """
    collection = ET.Element("collection")
    root_cat = ET.SubElement(collection, "category", {"name": "import"})

    for symbol in used_symbols:
        parts = symbol.elmt_path.split("/")
        dirs, filename = parts[:-1], parts[-1]
        node = root_cat
        for d in dirs:
            existing = next((c for c in node if c.tag == "category"
                             and c.get("name") == d), None)
            if existing is None:
                existing = ET.SubElement(node, "category", {"name": d})
            node = existing
        wrapper = ET.SubElement(node, "element", {"name": filename})
        wrapper.append(symbol.definition)            # copia literal del .elmt
    return collection


def build_project(spec, catalog):
    """Construye el árbol XML completo (todos los folios).

    Devuelve (root, [DiagramBuildResult por folio]).
    """
    root = ET.Element("project", {"title": spec.title, "version": "0.100.0"})
    root.append(_project_properties(spec))
    root.append(_newdiagrams(spec))

    results = []
    for folio in spec.folios:
        result = diagram_mod.build_diagram(folio, catalog, spec.author)
        results.append(result)
        root.append(result.xml)

    # símbolos usados en TODOS los folios, embebidos UNA vez
    used = catalog.used_symbols([el.type for el in spec.elements])
    root.append(_collection(used))
    return root, results


def export_project(root: ET.Element, output_path: str | Path) -> Path:
    """Serializa a .qet: XML plano UTF-8, sin declaración ni BOM (evidencia §1)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(root)
    try:
        ET.indent(tree, space="    ")   # legibilidad; QET re-formatea al guardar
    except AttributeError:
        pass
    xml_text = ET.tostring(root, encoding="unicode")
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml_text)
    return output_path
