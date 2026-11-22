"""Formatos de hoja (tamaños de folio) y zona segura.

Evidencia (medida sobre los 22 proyectos de ejemplo de QElectroTech 0.100.0,
129 folios, con ``tools/measure_sheet_geometry.py``):

* ``<diagram>`` **no guarda el atributo ``width``** (0 de 129 folios lo tienen):
  el ancho del folio se **deriva** como ``cols * colsize`` [CONFIRMADO].
* ``height == rows * rowsize + 20`` — exacto en **129/129 folios (100 %)**.
* Los 20 px adicionales son la banda inferior reservada al cajetín
  (``displayAt="bottom"``).
* El área de dibujo útil es ``cols*colsize × rows*rowsize``; 3486 de 3525
  elementos reales (98,9 %) caen dentro de ella, y **ninguno** rebasa el
  borde derecho (desbordamiento máximo: 0 px).
* existen **12 tamaños de folio distintos** en la biblioteca real.

Esta hoja de evidencia es la base normativa de la zona segura que aplica el
motor de layout y el validador estético.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import BBox

#: Altura de la banda inferior reservada al cajetín (evidencia: +20 px).
TITLEBLOCK_BAND = 20.0


@dataclass(frozen=True)
class SheetFormat:
    """Tamaño de folio: rejilla de QET + márgenes + zona segura.

    Attributes
    ----------
    name:
        Identificador del preset (referenciado por ``Sheet.sheet_format``).
    cols, rows:
        Celdas de la rejilla visible de QET.
    colsize, rowsize:
        Tamaño de celda en píxeles.
    margin:
        Margen interior de seguridad (px) respecto del borde del área de dibujo.
    titleblock_height:
        Altura de la banda inferior reservada al cajetín (px).
    """

    name: str
    cols: int
    rows: int
    colsize: int = 60
    rowsize: int = 80
    margin: float = 0.0
    titleblock_height: float = TITLEBLOCK_BAND

    # -- dimensiones derivadas --------------------------------------------

    @property
    def width(self) -> float:
        """Ancho total del área de dibujo (``cols * colsize``)."""
        return float(self.cols * self.colsize)

    @property
    def usable_height(self) -> float:
        """Alto del área de dibujo (``rows * rowsize``)."""
        return float(self.rows * self.rowsize)

    @property
    def height(self) -> float:
        """Alto total del folio (``rows * rowsize + 20``) — atributo ``height``."""
        return self.usable_height + self.titleblock_height

    # -- zonas -------------------------------------------------------------

    @property
    def drawing_area(self) -> BBox:
        """Área de dibujo completa (sin la banda del cajetín)."""
        return BBox(0.0, 0.0, self.width, self.usable_height)

    @property
    def titleblock_area(self) -> BBox:
        """Banda inferior reservada al cajetín."""
        return BBox(0.0, self.usable_height, self.width, self.height)

    @property
    def safe_area(self) -> BBox:
        """**Zona segura**: área de dibujo menos los márgenes configurados."""
        area = self.drawing_area
        return area.inset(self.margin) if self.margin else area

    # -- serialización -----------------------------------------------------

    def to_dict(self) -> dict:
        """Representación serializable (config / MCP)."""
        return {
            "name": self.name,
            "cols": self.cols,
            "rows": self.rows,
            "colsize": self.colsize,
            "rowsize": self.rowsize,
            "margin": self.margin,
            "titleblock_height": self.titleblock_height,
            "width": self.width,
            "usable_height": self.usable_height,
            "height": self.height,
        }


#: Presets derivados de los tamaños reales encontrados en la biblioteca y en
#: los proyectos de ejemplo de QElectroTech.
SHEET_FORMATS: dict[str, SheetFormat] = {
    "A3_17x8": SheetFormat(name="A3_17x8", cols=17, rows=8),
    "A3_18x9": SheetFormat(name="A3_18x9", cols=18, rows=9),
    "A3_20x11": SheetFormat(name="A3_20x11", cols=20, rows=11),
    "A4_11x7": SheetFormat(name="A4_11x7", cols=11, rows=7),
    "A4_10x5": SheetFormat(name="A4_10x5", cols=10, rows=5),
    "A2_24x11": SheetFormat(name="A2_24x11", cols=24, rows=11),
    "A1_39x20": SheetFormat(name="A1_39x20", cols=39, rows=20),
    "A0_42x21": SheetFormat(name="A0_42x21", cols=42, rows=21),
    "A4_15x6": SheetFormat(name="A4_15x6", cols=15, rows=6, colsize=50),
}


def get_sheet_format(name: str | None) -> SheetFormat:
    """Resuelve un preset por nombre; si no existe, devuelve el estándar."""
    if not name:
        return SHEET_FORMATS["A3_17x8"]
    if name in SHEET_FORMATS:
        return SHEET_FORMATS[name]
    raise KeyError(
        f"Formato de hoja desconocido: {name!r}. "
        f"Disponibles: {', '.join(sorted(SHEET_FORMATS))}")


__all__ = ["SHEET_FORMATS", "SheetFormat", "TITLEBLOCK_BAND", "get_sheet_format"]
