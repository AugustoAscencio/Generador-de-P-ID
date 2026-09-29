"""shapes.py — Bloques gráficos <shape> (rectángulos de diagrama funcional).

Formato CONFIRMADO en photovoltaique.qet / schema_unifilaire_voltaique2.qet
(docs/QET_FORMAT_NOTES.md §1):
    <shape x1=".." y1=".." x2=".." y2=".." type="Rectangle"
           is_movable="1" z="0" closed="0" rx="0" ry="0">
        <pen style="SolidLine|DashLine" widthF="1" color="#rrggbb"/>
        <brush style="NoBrush|SolidPattern" color="#rrggbb"/>
    </shape>
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from .model import ShapeSpec


def _fmt(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return repr(float(value))


def build_rectangle(shape: ShapeSpec) -> ET.Element:
    """Construye un <shape type="Rectangle"> según el formato observado."""
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
        # la evidencia muestra color presente también con NoBrush
        ET.SubElement(el, "brush", {"style": "NoBrush", "color": shape.color})
    return el
