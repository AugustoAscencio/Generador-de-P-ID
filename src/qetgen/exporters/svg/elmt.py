"""exporters/svg/elmt.py — Renderizado de las primitivas reales de un ``.elmt``.

El preview SVG **no** inventa gráficos: dibuja exactamente las primitivas
declaradas en ``<description>`` del símbolo real (líneas, rectángulos,
polígonos, elipses, arcos, círculos y textos), con los mismos atributos de
estilo observados en la biblioteca instalada:

.. code-block:: text

    style="line-style:normal;line-weight:normal;filling:none;color:black"

Es la capa de exportador (no el núcleo) la que relee el ``.elmt`` en XML: el
núcleo solo guarda datos puros.
"""

from __future__ import annotations

import html
import math
import re
import xml.etree.ElementTree as ET

from ...core.catalog import SymbolDefinition

#: Traducción de ``line-weight`` a grosor de trazo (px).
_WEIGHTS = {"normal": 1.0, "hight": 2.0, "high": 2.0, "bold": 3.0, "light": 0.6}

#: Traducción de ``filling`` a color de relleno SVG.
_FILLINGS = {
    "none": "none",
    "black": "#000000",
    "white": "#ffffff",
    "darkgray": "#404040",
    "gray": "#808080",
    "lightgray": "#c0c0c0",
}

_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")


def _parse_style(raw: str | None) -> dict[str, str]:
    """Descompone el atributo ``style`` de las primitivas de QET."""
    style: dict[str, str] = {}
    if not raw:
        return style
    for chunk in raw.split(";"):
        if ":" not in chunk:
            continue
        key, _, value = chunk.partition(":")
        style[key.strip()] = value.strip()
    return style


def _color(value: str | None, default: str = "#000000") -> str:
    """Normaliza un color de QET a un color SVG."""
    if not value:
        return default
    value = value.strip().lower()
    if value in _FILLINGS:
        return _FILLINGS[value]
    if _COLOR_RE.match(value):
        return value
    if re.match(r"^[a-z]+$", value):
        return value
    return default


def _stroke_and_fill(style: dict[str, str]) -> tuple[str, str, float]:
    """Devuelve ``(color_trazo, color_relleno, grosor)`` de una primitiva."""
    stroke = _color(style.get("color"))
    filling = style.get("filling", "none")
    fill = _FILLINGS.get(filling.lower(), filling if filling.startswith("#") else "none")
    width = _WEIGHTS.get(style.get("line-weight", "normal").lower(), 1.0)
    if style.get("line-style") == "dash":
        width = max(width, 1.0)
    return stroke, fill, width


def _num(node, key: str, default: float = 0.0) -> float:
    """Lee un atributo numérico del ``.elmt``."""
    raw = node.get(key)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _points(node, count: int = 8) -> str:
    """Extrae los vértices ``x1,y1 … xN,yN`` de un polígono."""
    values = []
    for index in range(1, count + 1):
        xa, ya = node.get(f"x{index}"), node.get(f"y{index}")
        if xa is None or ya is None:
            break
        values.append(f"{float(xa)},{float(ya)}")
    return " ".join(values)


def render_primitive(node: ET.Element, px_per_pt: float = 4.0 / 3.0) -> str:
    """Convierte una primitiva de ``<description>`` en un elemento SVG."""
    tag = node.tag
    style = _parse_style(node.get("style"))
    stroke, fill, width = _stroke_and_fill(style)
    dash = ' stroke-dasharray="4 3"' if style.get("line-style") == "dash" else ""

    if tag == "line":
        return (f'<line x1="{_num(node, "x1")}" y1="{_num(node, "y1")}" '
                f'x2="{_num(node, "x2")}" y2="{_num(node, "y2")}" '
                f'stroke="{stroke}" stroke-width="{width}"{dash} />')
    if tag == "rect":
        return (f'<rect x="{_num(node, "x")}" y="{_num(node, "y")}" '
                f'width="{_num(node, "width")}" height="{_num(node, "height")}" '
                f'rx="{_num(node, "rx")}" ry="{_num(node, "ry")}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"{dash} />')
    if tag == "polygon":
        points = _points(node)
        if not points:
            return ""
        return (f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" '
                f'stroke-width="{width}"{dash} />')
    if tag == "ellipse":
        x, y = _num(node, "x"), _num(node, "y")
        w, h = _num(node, "width"), _num(node, "height")
        return (f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2}" '
                f'ry="{h / 2}" fill="{fill}" stroke="{stroke}" '
                f'stroke-width="{width}"{dash} />')
    if tag == "circle":
        x, y = _num(node, "x"), _num(node, "y")
        diameter = _num(node, "diameter")
        return (f'<circle cx="{x + diameter / 2}" cy="{y + diameter / 2}" '
                f'r="{diameter / 2}" fill="{fill}" stroke="{stroke}" '
                f'stroke-width="{width}"{dash} />')
    if tag == "arc":
        x, y = _num(node, "x"), _num(node, "y")
        w, h = _num(node, "width"), _num(node, "height")
        start = _num(node, "start", 0.0)
        angle = _num(node, "angle", 90.0)
        cx, cy = x + w / 2.0, y + h / 2.0
        rx, ry = w / 2.0, h / 2.0
        a0 = math.radians(start)
        a1 = math.radians(start + angle)
        p0 = (cx + rx * math.cos(a0), cy + ry * math.sin(a0))
        p1 = (cx + rx * math.cos(a1), cy + ry * math.sin(a1))
        large = 1 if abs(angle) > 180 else 0
        sweep = 1 if angle >= 0 else 0
        return (f'<path d="M {p0[0]:.3f},{p0[1]:.3f} '
                f'A {rx:.3f},{ry:.3f} 0 {large} {sweep} {p1[0]:.3f},{p1[1]:.3f}" '
                f'fill="none" stroke="{stroke}" stroke-width="{width}"{dash} />')
    if tag == "text":
        content = node.get("text", "")
        if not content:
            return ""
        size = _num(node, "size", 9.0) * px_per_pt
        color = _color(node.get("color"))
        return (f'<text x="{_num(node, "x")}" y="{_num(node, "y")}" '
                f'font-size="{size:.1f}" fill="{color}" '
                f'dominant-baseline="text-before-edge">'
                f'{html.escape(content)}</text>')
    return ""


def render_symbol(symbol: SymbolDefinition, px_per_pt: float = 4.0 / 3.0) -> str:
    """Renderiza el contenido gráfico de un símbolo (grupo SVG).

    Las coordenadas resultantes son **relativas al hotspot**, igual que en el
    ``.elmt``: quien las coloca aplica la transformación del componente.
    """
    try:
        root = ET.parse(symbol.file_path).getroot()
    except (ET.ParseError, OSError):
        return ""
    description = root.find("description")
    if description is None:
        return ""
    parts: list[str] = []
    for node in description:
        rendered = render_primitive(node, px_per_pt=px_per_pt)
        if rendered:
            parts.append(rendered)
    return "\n      ".join(parts)


def symbol_label_anchor(symbol: SymbolDefinition) -> tuple[float, float]:
    """Posición del ancla de la etiqueta dinámica del símbolo."""
    return symbol.label_pos


__all__ = ["render_primitive", "render_symbol", "symbol_label_anchor"]
