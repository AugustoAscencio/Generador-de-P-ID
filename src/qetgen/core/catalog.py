"""Catálogo de símbolos: clave lógica → ``.elmt`` real de la biblioteca.

Este módulo resuelve el único punto de contacto con la instalación de
QElectroTech. Todo lo que expone son **datos puros** (rutas, terminales,
caja envolvente, posición de etiqueta); el XML del ``.elmt`` se relee en el
exportador cuando hace falta embeberlo, de modo que el núcleo no depende
de ElementTree.

Evidencia:
  * Los ``.elmt`` de la biblioteca instalada (8.597 archivos) usan las
    primitivas ``line``, ``polygon``, ``rect``, ``ellipse``, ``arc``,
    ``circle``, ``text`` y ``terminal`` (censado 2026-11-22).
  * Las coordenadas de las primitivas son **relativas al hotspot**; el
    ``<definition>`` declara además ``width``, ``height``, ``hotspot_x`` y
    ``hotspot_y`` (QET_FORMAT_NOTES.md §3, §7).
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from .errors import CatalogError
from .geometry import BBox
from .models import Port

#: Orientación de terminal: letras del .elmt → números del elemento colocado.
#: CONFIRMADO: n→0, s→2 (evidencia §3). INFERIDO: e→1, w→3 (convención QET).
ORIENTATION_LETTER_TO_NUM: dict[str, str] = {"n": "0", "e": "1", "s": "2", "w": "3"}

#: Fuente por defecto de las instancias (evidencia §3).
INSTANCE_FONT = "Sans Serif,9,-1,5,0,0,0,0,0,0,normal"

#: Posición por defecto de la etiqueta si el .elmt no la declara.
DEFAULT_LABEL_POS: tuple[float, float] = (10.0, -17.5)

#: Claves reservadas del JSON del catálogo (no son símbolos).
_RESERVED_KEYS = {"_comment", "_meta", "$schema"}


@dataclass(frozen=True)
class SymbolDefinition:
    """Datos extraídos de un ``.elmt`` real (sin XML dentro)."""

    type_key: str
    elmt_path: str
    file_path: Path
    prefix: str = ""
    description: str = ""
    width: float = 0.0
    height: float = 0.0
    hotspot_x: float = 0.0
    hotspot_y: float = 0.0
    terminals: tuple[Port, ...] = ()
    label_pos: tuple[float, float] = DEFAULT_LABEL_POS
    bounds: BBox = field(default_factory=lambda: BBox(0, 0, 0, 0))

    @property
    def embed_type(self) -> str:
        """Referencia ``embed://`` usada por los elementos colocados."""
        return f"embed://import/{self.elmt_path}"

    @property
    def terminal_count(self) -> int:
        return len(self.terminals)

    @property
    def ink_bounds(self) -> BBox:
        """Caja de la **tinta real** del símbolo (primitivas de ``<description>``).

        Es la caja que se usa para detectar colisiones: lo que se pisa
        visualmente es la tinta, no el espacio en blanco que el diseñador del
        símbolo reservó alrededor. Si el símbolo no tiene primitivas, se cae
        a :attr:`placement_bounds`.
        """
        if self.bounds.is_empty():
            return self.placement_bounds
        return self.bounds

    @property
    def placement_bounds(self) -> BBox:
        """Caja de colocación del símbolo, **relativa al hotspot**.

        Es la caja declarada por el ``.elmt`` (``width`` × ``height`` con el
        hotspot en ``hotspot_x``/``hotspot_y``). Evidencia medida sobre los 14
        símbolos del catálogo: las primitivas reales de ``<description>``
        quedan **siempre dentro** de esta caja, por lo que es una envolvente
        conservadora y verificable (test ``test_primitivas_dentro_del_slot``).
        """
        return BBox(
            -self.hotspot_x,
            -self.hotspot_y,
            self.width - self.hotspot_x,
            self.height - self.hotspot_y,
        )

    def port(self, index: int) -> Port:
        """Terminal por índice; lanza ``IndexError`` si no existe."""
        return self.terminals[index]

    def absolute_terminal(self, index: int, host_x: float, host_y: float) -> tuple[float, float]:
        """Posición absoluta de una terminal dado el hotspot del componente."""
        return self.terminals[index].absolute(host_x, host_y)


def _fmt(value: float) -> str:
    """Formatea un número como lo hace QET (sin ceros espurios)."""
    f = float(value)
    if f == int(f):
        return str(int(f))
    return repr(f)


def _as_float(value: str | None, default: float = 0.0) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def _extract_bounds(definition: ET.Element) -> BBox:
    """Caja envolvente real del símbolo, relativa al hotspot.

    Recorre las primitivas confirmadas en la biblioteca instalada y añade
    las terminales (para que el bbox incluya los puntos de conexión).
    """
    points: list[tuple[float, float]] = []

    description = definition.find("description")
    if description is not None:
        for node in description.iter():
            tag = node.tag
            if tag == "line":
                points.append((_as_float(node.get("x1")), _as_float(node.get("y1"))))
                points.append((_as_float(node.get("x2")), _as_float(node.get("y2"))))
            elif tag == "polygon":
                for i in range(1, 7):
                    xa, ya = node.get(f"x{i}"), node.get(f"y{i}")
                    if xa is not None and ya is not None:
                        points.append((_as_float(xa), _as_float(ya)))
            elif tag in {"rect", "ellipse"}:
                x = _as_float(node.get("x"))
                y = _as_float(node.get("y"))
                w = _as_float(node.get("width"))
                h = _as_float(node.get("height"))
                points.extend([(x, y), (x + w, y + h)])
            elif tag == "arc":
                x = _as_float(node.get("x"))
                y = _as_float(node.get("y"))
                w = _as_float(node.get("width"))
                h = _as_float(node.get("height"))
                points.extend([(x, y), (x + w, y + h)])
            elif tag == "circle":
                x = _as_float(node.get("x"))
                y = _as_float(node.get("y"))
                d = _as_float(node.get("diameter"))
                points.extend([(x, y), (x + d, y + d)])
            elif tag == "text":
                # Texto estático del propio símbolo: se incluye su ancla.
                points.append((_as_float(node.get("x")), _as_float(node.get("y"))))

    for terminal in definition.iter("terminal"):
        points.append((_as_float(terminal.get("x")), _as_float(terminal.get("y"))))

    bounds = BBox.from_points(points)
    return bounds if bounds is not None else BBox(0, 0, 0, 0)


def _extract_terminals(definition: ET.Element) -> tuple[Port, ...]:
    """Terminales en orden de documento = índice usado por las conexiones."""
    ports: list[Port] = []
    for i, node in enumerate(definition.iter("terminal")):
        ports.append(Port(
            index=i,
            uuid=node.get("uuid", "") or "",
            x=_as_float(node.get("x")),
            y=_as_float(node.get("y")),
            orientation=node.get("orientation", "n") or "n",
            name=node.get("name", "") or "",
            number=node.get("number", "") or "",
        ))
    return tuple(ports)


def _extract_label_pos(definition: ET.Element) -> tuple[float, float]:
    """Posición del texto dinámico que muestra la etiqueta."""
    for dyn in definition.iter("dynamic_text"):
        info = dyn.find("info_name")
        if info is not None and (info.text or "") == "label":
            return (_as_float(dyn.get("x"), 10.0), _as_float(dyn.get("y"), -17.5))
    return DEFAULT_LABEL_POS


class SymbolCatalog:
    """Resuelve tipos lógicos del modelo a símbolos reales de la biblioteca.

    Parameters
    ----------
    catalog_path:
        JSON con ``{tipo_logico: {elmt_path, prefix, description}}``.
    library_path:
        Raíz de la colección de elementos de QElectroTech.
    """

    DEFAULT_LIBRARY = Path(r"C:\Program Files\QElectroTech\elements")

    def __init__(self, catalog_path: str | Path,
                 library_path: str | Path | None = None):
        self.catalog_path = Path(catalog_path)
        self.library = Path(library_path) if library_path else self.DEFAULT_LIBRARY
        if not self.library.is_dir():
            raise CatalogError(
                f"No se encuentra la biblioteca de QElectroTech: {self.library}\n"
                f"Instala QElectroTech o indica --library / config.sources.library_path.")
        self._entries: dict[str, dict] = {}
        self._cache: dict[str, SymbolDefinition] = {}
        self._load()

    # -- carga -------------------------------------------------------------

    def _load(self) -> None:
        if not self.catalog_path.is_file():
            raise CatalogError(f"No existe el catálogo de símbolos: {self.catalog_path}")
        try:
            data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CatalogError(f"Catálogo JSON mal formado: {exc}") from exc
        if not isinstance(data, dict):
            raise CatalogError("El catálogo debe ser un objeto JSON")
        self._entries = {k: v for k, v in data.items() if k not in _RESERVED_KEYS}

    # -- consultas ---------------------------------------------------------

    def has(self, type_key: str) -> bool:
        """``True`` si el tipo está registrado (las claves reservadas no cuentan)."""
        return type_key in self._entries

    def type_keys(self) -> list[str]:
        """Tipos lógicos disponibles, ordenados alfabéticamente."""
        return sorted(self._entries.keys())

    def entries(self) -> list[dict]:
        """Entradas del catálogo con su descripción (para listados y MCP)."""
        out = []
        for key in self.type_keys():
            entry = self._entries[key]
            out.append({
                "type": key,
                "elmt_path": entry.get("elmt_path", ""),
                "prefix": entry.get("prefix", ""),
                "description": entry.get("description", ""),
            })
        return out

    def get(self, type_key: str) -> SymbolDefinition:
        """Resuelve un tipo lógico; cachea el parseo del ``.elmt``."""
        if type_key in self._cache:
            return self._cache[type_key]
        if type_key not in self._entries:
            raise CatalogError(f"Tipo no registrado en el catálogo: {type_key!r}")
        entry = self._entries[type_key]
        elmt_path = str(entry.get("elmt_path", "")).replace("\\", "/").strip("/")
        if not elmt_path:
            raise CatalogError(f"El catálogo no define 'elmt_path' para {type_key!r}")
        file_path = self.library / elmt_path
        if not file_path.is_file():
            raise CatalogError(
                f"El .elmt del tipo {type_key!r} no existe: {file_path}")

        try:
            definition = ET.parse(file_path).getroot()
        except ET.ParseError as exc:
            raise CatalogError(f"{file_path}: XML inválido ({exc})") from exc
        if definition.tag != "definition":
            raise CatalogError(f"{file_path}: raíz inesperada <{definition.tag}>")

        symbol = SymbolDefinition(
            type_key=type_key,
            elmt_path=elmt_path,
            file_path=file_path,
            prefix=str(entry.get("prefix", "") or ""),
            description=str(entry.get("description", "") or ""),
            width=_as_float(definition.get("width")),
            height=_as_float(definition.get("height")),
            hotspot_x=_as_float(definition.get("hotspot_x")),
            hotspot_y=_as_float(definition.get("hotspot_y")),
            terminals=_extract_terminals(definition),
            label_pos=_extract_label_pos(definition),
            bounds=_extract_bounds(definition),
        )
        self._cache[type_key] = symbol
        return symbol

    def used_symbols(self, type_keys) -> list[SymbolDefinition]:
        """Definiciones únicas (una por tipo) para embeber en ``<collection>``."""
        seen: dict[str, SymbolDefinition] = {}
        for key in type_keys:
            if key not in seen:
                seen[key] = self.get(key)
        return list(seen.values())


def default_catalog_path() -> Path:
    """Ruta por defecto del catálogo dentro del repositorio."""
    here = Path(__file__).resolve()
    for base in (here.parents[3], here.parents[2]):
        candidate = base / "resources" / "symbol_catalog.json"
        if candidate.is_file():
            return candidate
    return Path.cwd() / "resources" / "symbol_catalog.json"


__all__ = [
    "DEFAULT_LABEL_POS",
    "INSTANCE_FONT",
    "ORIENTATION_LETTER_TO_NUM",
    "SymbolCatalog",
    "SymbolDefinition",
    "default_catalog_path",
]
