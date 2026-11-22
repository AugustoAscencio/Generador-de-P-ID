"""Configuración central del motor.

Un único archivo (``config/default.yaml``) gobierna **todo** lo que un
usuario pueda querer ajustar sin tocar código:

* formato de hoja y márgenes (zona segura y cajetín),
* paso de la cuadrícula y comportamiento del *snap-to-grid*,
* tipografía (familia, tamaños, colores),
* separación mínima entre cables, penalización de giros y cruces,
* estilos de bloques y colores,
* rutas de las fuentes (catálogo de símbolos y biblioteca de QET).

El formato es YAML (si ``PyYAML`` está disponible) o JSON; ambos se pueden
usar indistintamente. Los valores se validan con Pydantic: una configuración
errónea se rechaza al cargar, no a mitad de un cálculo.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .core.errors import SpecError
from .core.sheet import SHEET_FORMATS


class _Section(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SheetConfig(_Section):
    """Hoja: tamaño, márgenes y zona segura."""

    format: str = Field(default="A3_17x8", description="Preset de hoja")
    margin: float = Field(default=8.0, ge=0, description="Margen interior de seguridad (px)")
    titleblock_height: float = Field(default=20.0, ge=0,
                                     description="Banda inferior reservada al cajetín (px)")
    show_grid: bool = Field(default=True, description="Mostrar la rejilla de QET")

    @field_validator("format")
    @classmethod
    def _known_format(cls, value: str) -> str:
        if value not in SHEET_FORMATS:
            raise ValueError(
                f"formato de hoja desconocido: {value!r} "
                f"(disponibles: {', '.join(sorted(SHEET_FORMATS))})")
        return value


class LayoutConfig(_Section):
    """Motor de layout: cuadrícula, colisiones, etiquetas y routing."""

    grid_size: float = Field(default=10.0, gt=0, description="Paso de la cuadrícula (px)")
    snap_to_grid: bool = Field(default=True, description="Alinear a la cuadrícula")
    min_separation: float = Field(
        default=12.0, gt=0, description="Separación mínima entre cables paralelos (px)")
    label_margin: float = Field(
        default=4.0, ge=0, description="Respiro mínimo alrededor de una etiqueta (px)")
    label_max_candidates: int = Field(
        default=8, ge=1, le=32, description="Posiciones de etiqueta a probar por componente")
    respect_locked: bool = Field(
        default=True, description="Respetar los elementos con locked=true")
    route_manhattan: bool = Field(
        default=True, description="Calcular rutas ortogonales (A* con penalización)")
    turn_penalty: float = Field(
        default=20.0, ge=0, description="Penalización por giro (px equivalentes)")
    crossing_penalty: float = Field(
        default=40.0, ge=0, description="Penalización por cruzar otro conductor")
    max_search_nodes: int = Field(
        default=60000, ge=100, description="Límite de nodos explorados por el router")


class TypographyConfig(_Section):
    """Tipografía de textos y etiquetas."""

    font_family: str = Field(default="Sans Serif", description="Familia tipográfica")
    default_size: int = Field(default=9, ge=1, description="Tamaño por defecto (pt)")
    min_size: int = Field(default=5, ge=1, description="Tamaño mínimo admitido (pt)")
    max_size: int = Field(default=24, ge=1, description="Tamaño máximo admitido (pt)")
    char_width_ratio: float = Field(
        default=0.58, gt=0,
        description="Ancho medio de carácter como fracción del tamaño de fuente")
    line_height_ratio: float = Field(
        default=1.25, gt=0, description="Alto de línea como fracción del tamaño de fuente")


class StyleConfig(_Section):
    """Colores y estilos visuales de los bloques."""

    block_color: str = Field(default="#1f4e79", description="Color de línea de los bloques")
    block_fill: str = Field(default="#e8f0f8", description="Color de relleno de los bloques")
    block_width: float = Field(default=1.5, gt=0, description="Grosor de línea de los bloques")
    table_color: str = Field(default="#7f7f7f", description="Color de las tablas")
    warning_color: str = Field(default="#b26a00", description="Color de los avisos")
    error_color: str = Field(default="#c0392b", description="Color de los errores")
    wire_color: str = Field(default="#000000", description="Color de los conductores")
    background: str = Field(default="#ffffff", description="Fondo del lienzo (SVG)")


class SourcesConfig(_Section):
    """Rutas de las fuentes externas."""

    library_path: str = Field(
        default=r"C:\Program Files\QElectroTech\elements",
        description="Biblioteca de elementos de QElectroTech")
    catalog_path: str = Field(
        default="resources/symbol_catalog.json",
        description="Catálogo de símbolos lógicos → .elmt")


class QetGenConfig(_Section):
    """Configuración completa."""

    sheet: SheetConfig = Field(default_factory=SheetConfig)
    layout: LayoutConfig = Field(default_factory=LayoutConfig)
    typography: TypographyConfig = Field(default_factory=TypographyConfig)
    styles: StyleConfig = Field(default_factory=StyleConfig)
    sources: SourcesConfig = Field(default_factory=SourcesConfig)

    def to_dict(self) -> dict[str, Any]:
        """Representación serializable."""
        return self.model_dump()


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError as exc:      # pragma: no cover
        raise SpecError(
            "PyYAML no está instalado. Instálalo (pip install PyYAML) o usa "
            "un archivo de configuración en formato JSON.") from exc
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_config(path: str | Path | None = None) -> QetGenConfig:
    """Carga la configuración desde YAML o JSON.

    Sin ``path`` devuelve la configuración por defecto.
    """
    if path is None:
        return QetGenConfig()
    path = Path(path)
    if not path.is_file():
        raise SpecError(f"No existe el archivo de configuración: {path}")
    data = _load_yaml(path) if path.suffix.lower() in {".yaml", ".yml"} else _load_json(path)
    if not isinstance(data, dict):
        raise SpecError(f"{path}: la configuración debe ser un objeto")
    try:
        return QetGenConfig(**data)
    except Exception as exc:       # pydantic.ValidationError
        raise SpecError(f"{path}: configuración inválida → {exc}") from exc


def default_config_path() -> Path:
    """Ruta por defecto de la configuración dentro del repositorio."""
    here = Path(__file__).resolve()
    for base in (here.parents[2], here.parents[1]):
        candidate = base / "config" / "default.yaml"
        if candidate.is_file():
            return candidate
    return Path.cwd() / "config" / "default.yaml"


__all__ = [
    "LayoutConfig",
    "QetGenConfig",
    "SheetConfig",
    "SourcesConfig",
    "StyleConfig",
    "TypographyConfig",
    "default_config_path",
    "load_config",
]
