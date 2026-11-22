#!/usr/bin/env python3
"""md_to_docx.py — Convierte Markdown a Word (.docx) con formato profesional.

Pipeline: pandoc (estructura) → python-docx (estilo) → .docx listo para Word.

Formato aplicado:
  - Portada centrada (primeros 3 encabezados + tabla de metadatos sin bordes)
  - Capítulos numerados con salto de página
  - Encabezados en azul ingeniería, cuerpo Calibri 11
  - Tablas con rejilla, cabecera azul/blanca y filas alternadas
  - Encabezado y pie de página (con número de página) en cada hoja

Uso:
    python tools/md_to_docx.py entrada.md salida.docx
"""

import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AZUL = RGBColor(0x1F, 0x4E, 0x79)
AZUL_MED = RGBColor(0x2E, 0x74, 0xB5)
GRIS = RGBColor(0x59, 0x59, 0x59)
ZEBRA = "EDF2F9"
ENCABEZADO_TABLA = "1F4E79"


def _shd(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def _bordes(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "8EAADB")
        borders.append(el)
    tblPr.append(borders)


def _run_props(p, size, color, bold=None, italic=None, font="Calibri"):
    p.alignment = None
    for r in p.runs:
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.name = font
        if bold is not None:
            r.font.bold = bold
        if italic is not None:
            r.font.italic = italic


def estilo_portada_y_capitulos(doc):
    headings = [p for p in doc.paragraphs
                if p.style.name.startswith("Heading")]
    # --- portada: primeros 3 encabezados centrados ---
    for p in headings[:3]:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if len(headings) >= 1:
        _run_props(headings[0], 28, AZUL, bold=True)
        headings[0].paragraph_format.space_before = Pt(60)
    if len(headings) >= 2:
        _run_props(headings[1], 16, AZUL_MED, bold=True)
    if len(headings) >= 3:
        _run_props(headings[2], 12, GRIS, bold=False, italic=True)

    # --- capítulos: H2 numerados con salto de página; resto estilizado ---
    for p in headings[3:]:
        name = p.style.name
        txt = p.text.strip()
        if name == "Heading 2":
            _run_props(p, 14, AZUL, bold=True)
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
            if txt and txt[0].isdigit():
                p.paragraph_format.page_break_before = True
        elif name == "Heading 3":
            _run_props(p, 12, AZUL_MED, bold=True)
            p.paragraph_format.space_before = Pt(12)
        elif name == "Heading 4":
            _run_props(p, 10.5, GRIS, bold=True, italic=True)
        else:
            _run_props(p, 12, AZUL, bold=True)


def estilo_tablas(doc):
    for i, table in enumerate(doc.tables):
        if i == 0:
            # tabla de metadatos de portada: sin bordes, centrada
            table.alignment = 1  # WD_TABLE_ALIGNMENT.CENTER
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for r in p.runs:
                            r.font.size = Pt(10.5)
                            r.font.name = "Calibri"
            continue
        _bordes(table)
        for ri, row in enumerate(table.rows):
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.space_after = Pt(2)
                    for r in p.runs:
                        r.font.size = Pt(9.5)
                        r.font.name = "Calibri"
                        if ri == 0:
                            r.font.bold = True
                            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                if ri == 0:
                    _shd(cell, ENCABEZADO_TABLA)
                elif ri % 2 == 0:
                    _shd(cell, ZEBRA)


def encabezado_y_pie(doc, titulo_header):
    for sec in doc.sections:
        sec.top_margin = Cm(2.3)
        sec.bottom_margin = Cm(2.0)
        sec.left_margin = Cm(2.2)
        sec.right_margin = Cm(2.2)

        # encabezado
        hp = sec.header.paragraphs[0]
        hp.text = ""
        run = hp.add_run(titulo_header)
        run.font.size = Pt(8)
        run.font.color.rgb = GRIS
        run.font.name = "Calibri"
        run.font.italic = True
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # pie: "Página N de M"
        fp = sec.footer.paragraphs[0]
        fp.text = ""
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

        def _campo(instr, placeholder="1"):
            fld = OxmlElement("w:fldSimple")
            fld.set(qn("w:instr"), instr)
            r = OxmlElement("w:r")
            rPr = OxmlElement("w:rPr")
            sz = OxmlElement("w:sz")
            sz.set(qn("w:val"), "18")            # 9 pt (half-points)
            col = OxmlElement("w:color")
            col.set(qn("w:val"), "595959")
            rPr.append(sz)
            rPr.append(col)
            r.append(rPr)
            t = OxmlElement("w:t")
            t.text = placeholder
            r.append(t)
            fld.append(r)
            return fld

        r1 = fp.add_run("Página ")
        r1.font.size = Pt(9)
        r1.font.color.rgb = GRIS
        fp._p.append(_campo(" PAGE "))
        r2 = fp.add_run(" de ")
        r2.font.size = Pt(9)
        r2.font.color.rgb = GRIS
        fp._p.append(_campo(" NUMPAGES ", placeholder="1"))


def convertir(md_path: str, docx_path: str, titulo_header: str) -> Path:
    md = Path(md_path)
    out = Path(docx_path)

    # 1) estructura con pandoc
    subprocess.run(["pandoc", str(md), "-o", str(out)], check=True)

    # 2) estilo profesional con python-docx
    doc = Document(str(out))
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15

    estilo_portada_y_capitulos(doc)
    estilo_tablas(doc)
    encabezado_y_pie(doc, titulo_header)

    doc.core_properties.title = titulo_header
    doc.core_properties.subject = "Memoria técnica — ingeniería eléctrica"
    doc.save(str(out))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/md_to_docx.py entrada.md salida.docx")
        raise SystemExit(1)
    header = sys.argv[3] if len(sys.argv) > 3 else "Documento técnico"
    result = convertir(sys.argv[1], sys.argv[2], header)
    print(f"OK  {result}  ({result.stat().st_size:,} bytes)")
