"""conductors.py — Construcción de <conductor> (estilo UUID moderno).

Atributo set copiado de conductores reales de la versión 0.100.0
(docs/QET_FORMAT_NOTES.md §4). QET recalcula la ruta entre terminales.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

# Atributos observados en conductores "multi" sin personalizar
_BASE_ATTRS = {
    "dash-size": "2",
    "x": "0",
    "bus": "",
    "color2": "#000000",
    "text_color": "#000000",
    "bicolor": "false",
    "horizrotatetext": "0",
    "type": "multi",
    "num": "",
    "displaytext": "1",
    "y": "0",
    "conductor_color": "",
    "conductor_section": "",
    "formula": "",
    "numsize": "7",
    "horizontal-alignment": "AlignBottom",
    "onetextperfolio": "0",
    "function": "",
    "freezeLabel": "false",
    "vertirotatetext": "270",
    "tension_protocol": "",
    "condsize": "1",
    "cable": "",
    "vertical-alignment": "AlignRight",
}


def build_conductor(element1_uuid: str, terminal1_uuid: str,
                    element2_uuid: str, terminal2_uuid: str,
                    num: str = "") -> ET.Element:
    """Conductor entre la terminal1 del elemento1 y la terminal2 del elemento2."""
    attrs = dict(_BASE_ATTRS)
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
