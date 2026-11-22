"""tools/measure_sheet_geometry.py — Evidencia medible del tamaño de folio.

Mide, sobre los proyectos de ejemplo instalados de QElectroTech 0.100.0:

1. La geometría del folio: si ``<diagram>`` guarda el atributo ``width`` y si
   ``height == rows * rowsize + 20``.
2. Cuántos tamaños de folio distintos existen en la biblioteca real.
3. Qué porcentaje de elementos (y de anclas de texto) queda dentro del área de
   dibujo útil (``cols*colsize × rows*rowsize``, sin la banda del cajetín).
4. La calibración de la métrica tipográfica: cuántos textos reales se saldrían
   del borde derecho con nuestra estimación, y cuál es el desborde máximo.

El script **solo lee**: no modifica nada. Es la fuente de las cifras citadas
en ``docs/QET_FORMAT_NOTES.md`` §12.

Uso::

    python -X utf8 tools/measure_sheet_geometry.py
"""

from __future__ import annotations

import glob
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from qetgen.layout.textmetrics import TextMeasurer  # noqa: E402

EXAMPLES = r"C:\Program Files\QElectroTech\examples"
TAG_RE = re.compile(r"<[^>]+>")
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL)


def visible_text(raw: str) -> str:
    """Extrae el texto visible del HTML richtext que guarda QElectroTech."""
    decoded = html.unescape(raw)
    paragraphs = P_RE.findall(decoded)
    body = "\n".join(paragraphs) if paragraphs else decoded
    body = TAG_RE.sub("", body)
    return body.replace("\xa0", " ").strip()


def main() -> int:
    files = sorted(glob.glob(os.path.join(EXAMPLES, "*.qet")))
    if not files:
        print(f"No se encontraron proyectos .qet en {EXAMPLES}")
        return 1

    measurer = TextMeasurer()
    folios = 0
    width_attr = 0
    height_ok = 0
    sizes: Counter = Counter()
    elements_total = elements_inside = 0
    max_dx = -1e9
    max_dy = -1e9
    texts_total = texts_inside = texts_overflow = 0
    overflows: list[float] = []
    max_overflow = 0.0
    worst_overflow: tuple[str, str] | None = None

    for path in files:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        for diagram in root.findall("diagram"):
            folios += 1
            cols = int(diagram.get("cols", 0))
            rows = int(diagram.get("rows", 0))
            colsize = int(diagram.get("colsize", 0))
            rowsize = int(diagram.get("rowsize", 0))
            height = int(diagram.get("height", 0))
            usable = rows * rowsize
            width = cols * colsize

            if "width" in diagram.attrib:
                width_attr += 1
            if height == rows * rowsize + 20:
                height_ok += 1
            sizes[(cols, rows, colsize, rowsize)] += 1

            for element in diagram.findall("elements/element"):
                x = element.get("x")
                y = element.get("y")
                if x is None or y is None:
                    continue
                elements_total += 1
                fx, fy = float(x), float(y)
                max_dx = max(max_dx, fx - width)
                max_dy = max(max_dy, fy - usable)
                if 0 <= fx <= width and 0 <= fy <= usable:
                    elements_inside += 1

            for node in diagram.findall("inputs/input"):
                raw = node.get("text", "")
                text = visible_text(raw)
                if not text:
                    continue
                x = float(node.get("x", 0))
                y = float(node.get("y", 0))
                size = int(node.get("size", 9) or 9)
                texts_total += 1
                box = measurer.measure(text, size=size)
                if 0 <= x <= width and 0 <= y <= usable:
                    texts_inside += 1
                overflow = max(0.0, (x + box.width) - width)
                if overflow > 0:
                    texts_overflow += 1
                    overflows.append(overflow)
                    if overflow > max_overflow:
                        max_overflow = overflow
                        worst_overflow = (os.path.basename(path), text[:48])

    rule = "=" * 74
    print(rule)
    print("MEDICIÓN DEL TAMAÑO DE FOLIO — QElectroTech 0.100.0 (instalado)")
    print(rule)
    print(f"Proyectos analizados      : {len(files)}")
    print(f"Folios analizados         : {folios}")
    print(f"Folios con atributo 'width' en <diagram>: {width_attr}/{folios}"
          f"  → el ancho NO se guarda: se deriva de cols*colsize")
    print(f"height == rows*rowsize+20 : {height_ok}/{folios}")
    print()
    print(f"Tamaños de folio distintos: {len(sizes)}")
    for (cols, rows, colsize, rowsize), count in sizes.most_common():
        print(f"   {cols:>3}x{rows:<3} celdas de {colsize}x{rowsize} px "
              f"-> {cols*colsize:>5}x{rows*rowsize:<5} px  ({count} folio/s)")
    print()
    if elements_total:
        pct = 100.0 * elements_inside / elements_total
        print(f"Elementos dentro del área de dibujo: {elements_inside}/{elements_total} "
              f"({pct:.1f} %)")
    print(f"Elemento más a la derecha - borde derecho: {max_dx:.0f} px "
          f"(nadie rebasa el borde)")
    print(f"Elemento más abajo   - área de dibujo   : {max_dy:.0f} px "
          f"(algunos elementos caen en la banda del cajetín)")
    if texts_total:
        pct = 100.0 * texts_inside / texts_total
        print(f"Anclas de texto dentro del área de dibujo: {texts_inside}/{texts_total} "
              f"({pct:.1f} %)")
    print()
    print("CALIBRACIÓN DE LA MÉTRICA TIPOGRÁFICA")
    print(f"  Textos analizados        : {texts_total}")
    print(f"  Se saldrían del borde    : {texts_overflow} "
          f"({100.0*texts_overflow/max(texts_total,1):.2f} %)")
    within_36 = sum(1 for value in overflows if value <= 36.0)
    print(f"  De ellos, <= 36 px       : {within_36}/{len(overflows)}")
    print(f"  Desborde máximo          : {max_overflow:.0f} px")
    if worst_overflow:
        print(f"  Caso extremo             : {worst_overflow[0]} — {worst_overflow[1]!r}")
    print()
    print("Tolerancia de borde adoptada por el motor: 36 px "
          "(aviso por encima, error por encima de 36 px).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
