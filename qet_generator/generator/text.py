"""text.py — Textos independientes del folio (<input> dentro de <inputs>).

Formato confirmado: el texto se envuelve en HTML richtext de Qt
(QTextDocument), tal como lo escribe QET 0.100.0.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from .elements import INSTANCE_FONT

# Plantilla HTML observada en photovoltaique.qet (docs/QET_FORMAT_NOTES.md §6)
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

def wrap_html(text: str) -> str:
    """Envuelve el texto plano en la plantilla richtext de Qt."""
    return _HTML_TEMPLATE.replace("{text}", text)


def build_text(spec) -> ET.Element:
    """Construye un <input> (texto independiente) según el formato observado.

    El atributo size y el tamaño en la fuente QFont provienen de la evidencia
    (size="9", font="Sans Serif,9,-1,5,0,0,0,0,0,0,normal").
    """
    size = str(spec.size)
    return ET.Element("input", {
        "rotation": str(spec.rotation),
        "x": _fmt_num(spec.x),
        "font": f"Sans Serif,{size},-1,5,0,0,0,0,0,0,normal",
        "text": wrap_html(spec.text),
        "y": _fmt_num(spec.y),
        "tagg": "label",
        "size": size,
        "rotate": "true",
    })


def _fmt_num(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return repr(float(value))
