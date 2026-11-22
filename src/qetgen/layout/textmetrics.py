"""layout/textmetrics.py — Métrica tipográfica aproximada pero reproducible.

QElectroTech mide el texto con Qt (``QFontMetrics``), que no está disponible
fuera de la aplicación. Para poder detectar colisiones y solapes **sin abrir
QET**, este módulo estima la caja ocupada por un texto con una métrica
parametrizable y documentada.

Calibración (verificable a ojo en los planos reales del proyecto FV 588):

* El tamaño de fuente de QET se expresa en **puntos**; el folio se mide en
  **píxeles**. A 96 dpi, ``1 pt = 4/3 px`` (``px_per_pt``).
* Una línea de texto ocupa ``size_pt · px_per_pt · line_height_ratio`` de alto.
* El ancho medio de un carácter es ``size_pt · px_per_pt · char_width_ratio``.

Los valores por defecto (``0.58`` y ``1.25``) son una estimación calibrada
para *Sans Serif*; se pueden ajustar en ``config/default.yaml`` sin tocar
código. La estimación **nunca** se escribe en el ``.qet``: solo se usa para
diagnóstico y previsualización.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextBox:
    """Caja ocupada por un texto, en píxeles de folio."""

    width: float
    height: float
    lines: int

    @property
    def area(self) -> float:
        return self.width * self.height

    def as_tuple(self) -> tuple[float, float]:
        return (self.width, self.height)


class TextMeasurer:
    """Medidor de texto con métricas configurables."""

    def __init__(self, font_family: str = "Sans Serif", default_size: int = 9,
                 char_width_ratio: float = 0.58, line_height_ratio: float = 1.25,
                 px_per_pt: float = 4.0 / 3.0):
        self.font_family = font_family
        self.default_size = default_size
        self.char_width_ratio = char_width_ratio
        self.line_height_ratio = line_height_ratio
        self.px_per_pt = px_per_pt

    # -- núcleo -------------------------------------------------------------

    def measure(self, text: str, size: int | None = None,
                rotation: int = 0) -> TextBox:
        """Mide un texto (posiblemente multilínea) y devuelve su caja.

        ``rotation`` en grados (0/90/180/270) intercambia ancho y alto, como
        hace el lienzo de QElectroTech.
        """
        size_pt = float(size if size is not None else self.default_size)
        raw_lines = str(text).split("\n")
        lines = [line for line in raw_lines] or [""]
        size_px = size_pt * self.px_per_pt
        longest = max((len(line) for line in lines), default=0)
        width = longest * size_px * self.char_width_ratio
        height = len(lines) * size_px * self.line_height_ratio
        rot = int(rotation) % 180
        if rot == 90:
            width, height = height, width
        return TextBox(width=width, height=height, lines=len(lines))

    def measure_box(self, text: str, x: float, y: float, size: int | None = None,
                    rotation: int = 0, align: str = "left"):
        """Caja delimitadora de un texto anclado en ``(x, y)``.

        El ancla de QET es la **esquina superior izquierda** del texto
        (evidencia §6 del formato: ``<input x= y= size= font= …>``).
        """
        box = self.measure(text, size=size, rotation=rotation)
        if align == "center":
            left = x - box.width / 2.0
        elif align == "right":
            left = x - box.width
        else:
            left = x
        top = y
        return (left, top, left + box.width, top + box.height)

    def is_readable(self, size: int, min_size: int = 5) -> bool:
        """``True`` si el tamaño es legible según la configuración."""
        return int(size) >= int(min_size)


__all__ = ["TextBox", "TextMeasurer"]
