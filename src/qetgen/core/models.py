"""Modelos de dominio estrictos.

Nuclear del proyecto: aquí vive **la verdad del modelo**, sin XML, sin
geometría computada y sin dependencias de QElectroTech. Todo lo demás
(exportadores, motor de layout, CLI, servidor MCP) opera sobre estos tipos.

Tecnología: **Pydantic v2**.

Motivos (decisión de arquitectura documentada en ``ARCHITECTURE.md``):

1. Validación estricta en el borde: un JSON de una IA o de un usuario se
   rechaza con un mensaje accionable, no con un ``AttributeError`` tres
   capas más abajo.
2. ``model_json_schema()`` genera el JSON Schema que el servidor MCP publica
   como ``inputSchema`` de cada herramienta: un solo origen de verdad.
3. ``extra="forbid"`` + ``validate_assignment=True`` convierten el modelo en
   un contrato, no en un ``dict`` disfrazado.

Los nombres heredados de la v0.1 (``ElementSpec``, ``FolioSpec``…) se
conservan como alias en :mod:`qetgen.legacy` para no romper código existente.
"""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from .errors import SpecError

# --------------------------------------------------------------------------
# Constantes de dominio
# --------------------------------------------------------------------------

#: Claves de metadatos de elemento confirmadas en proyectos reales 0.100.0
#: (QET_FORMAT_NOTES.md §3). Una clave fuera de esta lista se rechaza.
KNOWN_INFO_KEYS: frozenset[str] = frozenset({
    "location", "comment", "formula", "designation", "description",
    "manufacturer", "manufacturer_reference", "machine_manufacturer_reference",
    "supplier", "plant", "unity", "quantity",
})

#: Orden canónico de las claves de metadatos al serializar.
INFO_KEY_ORDER: tuple[str, ...] = (
    "location", "comment", "formula", "designation", "description",
    "manufacturer", "manufacturer_reference", "machine_manufacturer_reference",
    "supplier", "plant", "unity", "quantity",
)

_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

#: Tipos de conexión admitidos (cableado / tubería / señal / barra).
ConnectionKind = Literal["cable", "pipe", "signal", "bus"]

#: Alineación horizontal de una etiqueta de texto.
TextAlign = Literal["left", "center", "right"]

#: Orientación de un símbolo en el folio (0-3,Evidence §3).
Orientation = Literal[0, 1, 2, 3]


def _check_color(value: str, field: str) -> str:
    if not _HEX_COLOR_RE.match(value or ""):
        raise ValueError(f"{field} debe tener formato '#rrggbb' (recibido: {value!r})")
    return value


class _Base(BaseModel):
    """Base común: estricta, con alias population y validación al asignar."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        str_strip_whitespace=False,
    )


# --------------------------------------------------------------------------
# Puertos / pines
# --------------------------------------------------------------------------

class Port(_Base):
    """Pin (terminal) de un componente.

    Las coordenadas son **relativas al hotspot** del símbolo, tal como las
    guarda el ``.elmt`` real (QET_FORMAT_NOTES.md §3 y §7).
    """

    index: int = Field(ge=0, description="Índice base 0 dentro del símbolo (orden del .elmt)")
    uuid: str = Field(min_length=1, description="UUID de la terminal en la definición .elmt")
    x: float = Field(description="Desplazamiento X respecto del hotspot, en px")
    y: float = Field(description="Desplazamiento Y respecto del hotspot, en px")
    orientation: Literal["n", "e", "s", "w"] = Field(
        default="n", description="Orientación de la terminal en el .elmt")
    name: str = Field(default="", description="Nombre de la terminal en el .elmt")
    number: str = Field(default="", description="Numeración documentada (vacía si no consta)")

    def absolute(self, host_x: float, host_y: float) -> tuple[float, float]:
        """Posición absoluta de la terminal dado el hotspot del componente."""
        return (host_x + self.x, host_y + self.y)


# --------------------------------------------------------------------------
# Componentes
# --------------------------------------------------------------------------

class Component(_Base):
    """Equipo, símbolo o componente colocado en un folio.

    ``x``/``y`` son la posición del **hotspot**, no del centro (evidencia §7).
    """

    id: str = Field(min_length=1, description="Identificador único en todo el proyecto")
    type: str = Field(min_length=1, description="Clave lógica del catálogo de símbolos")
    x: float = Field(description="X del hotspot en el folio (px)")
    y: float = Field(description="Y del hotspot en el folio (px)")
    label: str | None = Field(default=None, description="Etiqueta visible; si es None, se usa el id")
    orientation: int = Field(
        default=0, ge=0, le=3, description="Rotación del símbolo (0-3)")
    info: dict[str, str] = Field(
        default_factory=dict, description="Metadatos BOM (claves confirmadas en KNOWN_INFO_KEYS)")
    locked: bool = Field(
        default=False,
        description="Si es True, el auto-layout NO mueve este componente (modo híbrido)")

    @field_validator("info", mode="before")
    @classmethod
    def _coerce_info(cls, value: Any) -> Any:
        """Normaliza metadatos: claves a str, valores a str, sin vacíos."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("info debe ser un objeto (mapa clave → valor)")
        out: dict[str, str] = {}
        for raw_key, raw_value in value.items():
            if raw_value is None or raw_value == "":
                continue
            out[str(raw_key)] = str(raw_value)
        return out

    @field_validator("orientation", mode="before")
    @classmethod
    def _coerce_orientation(cls, value: Any) -> Any:
        if isinstance(value, bool):
            raise ValueError("orientation no puede ser booleano")
        if isinstance(value, str):
            value = value.strip()
            if not value.lstrip("-").isdigit():
                raise ValueError(f"orientation debe ser un entero 0-3 (recibido: {value!r})")
            return int(value)
        return value

    def resolved_label(self) -> str:
        """Etiqueta efectiva: la explícita o, en su defecto, el identificador."""
        return self.label if self.label is not None else self.id

    def info_value(self, key: str) -> str:
        """Valor de un metadato BOM (cadena vacía si no existe)."""
        return str(self.info.get(key, "") or "")


# --------------------------------------------------------------------------
# Conexiones
# --------------------------------------------------------------------------

class Connection(_Base):
    """Cable, tubería o enlace lógico entre dos puertos.

    ``waypoints`` almacena la **ruta ortogonal calculada** por el motor de
    layout. No se escribe en el ``.qet`` (QET recalcula su propio trazado,
    evidencia §4): alimenta el exportador SVG, el validador estético y el
    auto-layout. Es la representación del *routing* en el modelo.
    """

    from_id: str = Field(
        min_length=1, validation_alias=AliasChoices("from_id", "from"),
        serialization_alias="from", description="Id del componente origen")
    to_id: str = Field(
        min_length=1, validation_alias=AliasChoices("to_id", "to"),
        serialization_alias="to", description="Id del componente destino")
    from_terminal: int = Field(default=0, ge=0, description="Índice de terminal origen")
    to_terminal: int = Field(default=0, ge=0, description="Índice de terminal destino")
    kind: ConnectionKind = Field(default="cable", description="Naturaleza del enlace")
    number: str = Field(default="", description="Número de conductor (autonumeración QET)")
    waypoints: list[tuple[float, float]] = Field(
        default_factory=list,
        description="Ruta ortogonal calculada [(x,y)…]; la usa layout/SVG, no el .qet")
    locked: bool = Field(
        default=False, description="Si es True, el router no recalcula esta ruta")

    def key(self) -> str:
        """Identificador legible del enlace."""
        return f"{self.from_id}[{self.from_terminal}] -> {self.to_id}[{self.to_terminal}]"


# --------------------------------------------------------------------------
# Etiquetas de texto
# --------------------------------------------------------------------------

class Label(_Base):
    """Texto independiente del folio (nota, TAG, leyenda, título de bloque)."""

    x: float = Field(description="X del ancla del texto (px)")
    y: float = Field(description="Y del ancla del texto (px)")
    text: str = Field(description="Contenido del texto")
    rotation: int = Field(default=0, description="Rotación en grados")
    size: int = Field(default=9, description="Tamaño de fuente en pt")
    align: TextAlign = Field(default="left", description="Alineación horizontal")
    locked: bool = Field(
        default=False, description="Si es True, el auto-layout no mueve esta etiqueta")

    # Nota: el texto vacío NO se rechaza en el modelo (regla de dominio,
    # reportada por validation/structural.py como diagnóstico accionable,
    # no como excepción). El modelo valida *estructura*; el validador
    # valida *contenido*.


# --------------------------------------------------------------------------
# Formas / bloques
# --------------------------------------------------------------------------

class Shape(_Base):
    """Rectángulo funcional (bloque de diagrama).

    Formato ``<shape>`` confirmado en los .qet reales (evidencia §1):
    atributos ``x1/y1/x2/y2`` + ``<pen/>`` + ``<brush/>``.
    """

    x1: float = Field(description="X del borde izquierdo")
    y1: float = Field(description="Y del borde superior")
    x2: float = Field(description="X del borde derecho")
    y2: float = Field(description="Y del borde inferior")
    color: str = Field(default="#004080", description="Color de línea (#rrggbb)")
    width: float = Field(default=1.0, gt=0, le=10, description="Grosor de línea")
    fill: str | None = Field(default=None, description="Color de relleno (#rrggbb) o None")
    dash: bool = Field(default=False, description="Línea discontinua")
    title: str = Field(default="", description="Título del bloque (uso del motor de layout)")
    role: Literal["background", "group", "table", "frame", "decoration"] = Field(
        default="group",
        description="Papel del bloque: fondo, agrupación, tabla, marco o decoración")
    locked: bool = Field(
        default=False, description="Si es True, el auto-layout no redimensiona este bloque")

    @field_validator("color")
    @classmethod
    def _valid_color(cls, value: str) -> str:
        return _check_color(value, "color")

    @field_validator("fill")
    @classmethod
    def _valid_fill(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _check_color(value, "fill")

    @field_validator("dash", mode="before")
    @classmethod
    def _coerce_dash(cls, value: Any) -> Any:
        """``"false"`` en JSON debe significa False, no True (bug v0.1)."""
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"false", "no", "0", ""}:
                return False
            if lowered in {"true", "yes", "1"}:
                return True
            raise ValueError(f"dash debe ser booleano (recibido: {value!r})")
        return value


# --------------------------------------------------------------------------
# Folios
# --------------------------------------------------------------------------

class Sheet(_Base):
    """Un folio (hoja) del proyecto — equivalencia de ``<diagram>``."""

    title: str = Field(default="", description="Título del folio")
    author: str = Field(default="", description="Autor del folio")
    indexrev: str = Field(default="A", description="Índice de revisión")
    date: str | None = Field(
        default=None, description="Fecha AAAAMMDD; None = fecha de generación")
    order: int | None = Field(default=None, ge=1, description="Número de folio (1..N)")
    elements: list[Component] = Field(default_factory=list, description="Componentes colocados")
    connections: list[Connection] = Field(default_factory=list, description="Enlaces")
    texts: list[Label] = Field(default_factory=list, description="Textos independientes")
    shapes: list[Shape] = Field(default_factory=list, description="Bloques funcionales")
    sheet_format: str = Field(
        default="A3_17x8",
        description="Nombre del preset de hoja (config/default.yaml → sheets)")
    layout_applied: bool = Field(
        default=False, description="True si el motor de layout ya procesó este folio")

    @field_validator("date")
    @classmethod
    def _valid_date(cls, value: str | None) -> str | None:
        if value is None:
            return None
        # El formato AAAAMMDD se verifica en validation/structural.py: es una
        # regla de dominio y debe poder reportarse como diagnóstico.
        return value

    @field_validator("order", mode="before")
    @classmethod
    def _coerce_order(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError("order no puede ser booleano")
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        return value


# --------------------------------------------------------------------------
# Proyecto
# --------------------------------------------------------------------------

class Project(_Base):
    """Proyecto completo: metadatos + folios."""

    title: str = Field(min_length=1, description="Título del proyecto")
    author: str = Field(default="", description="Autor del proyecto")
    filename: str = Field(default="", description="Nombre de archivo de referencia (metadatos)")
    library_path: str | None = Field(
        default=None, description="Ruta de la biblioteca de elementos de QElectroTech")
    folios: list[Sheet] = Field(default_factory=list, description="Folios del proyecto")

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("project.title no puede estar vacío")
        return value

    @model_validator(mode="after")
    def _at_least_one_folio(self) -> "Project":
        if not self.folios:
            raise ValueError("el proyecto debe tener al menos un folio")
        return self

    # -- acceso de conveniencia -------------------------------------------

    @property
    def sheets(self) -> list[Sheet]:
        """Alias semántico de ``folios`` (hojas del proyecto)."""
        return self.folios

    @property
    def elements(self) -> list[Component]:
        """Todos los componentes del proyecto (todos los folios)."""
        return [el for folio in self.folios for el in folio.elements]


# --------------------------------------------------------------------------
# Constructores ergonomicos
# --------------------------------------------------------------------------

def component(
    id: str, type: str, x: float, y: float, *, label: str | None = None,
    orientation: int = 0, info: dict[str, str] | None = None,
    locked: bool = False,
) -> Component:
    """Crea un :class:`Component` con validación estricta."""
    return Component(id=id, type=type, x=x, y=y, label=label,
                     orientation=orientation, info=info or {}, locked=locked)


def connection(
    from_id: str, to_id: str, from_terminal: int = 0, to_terminal: int = 0,
    *, kind: str = "cable", number: str = "", locked: bool = False,
) -> Connection:
    """Crea una :class:`Connection` con validación estricta."""
    return Connection(from_id=from_id, to_id=to_id, from_terminal=from_terminal,
                      to_terminal=to_terminal, kind=kind, number=number, locked=locked)


def label(x: float, y: float, text: str, *, size: int = 9, rotation: int = 0,
          align: str = "left", locked: bool = False) -> Label:
    """Crea una :class:`Label` con validación estricta."""
    return Label(x=x, y=y, text=text, size=size, rotation=rotation,
                 align=align, locked=locked)


def shape(x1: float, y1: float, x2: float, y2: float, *, color: str = "#004080",
          width: float = 1.0, fill: str | None = None, dash: bool = False,
          title: str = "", role: str = "group", locked: bool = False) -> Shape:
    """Crea un :class:`Shape` con validación estricta."""
    return Shape(x1=x1, y1=y1, x2=x2, y2=y2, color=color, width=width,
                 fill=fill, dash=dash, title=title, role=role, locked=locked)


__all__ = [
    "KNOWN_INFO_KEYS",
    "INFO_KEY_ORDER",
    "Connection",
    "ConnectionKind",
    "Component",
    "Label",
    "Orientation",
    "Port",
    "Project",
    "Shape",
    "Sheet",
    "SpecError",
    "TextAlign",
    "component",
    "connection",
    "label",
    "shape",
]
