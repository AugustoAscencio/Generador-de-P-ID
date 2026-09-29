"""elements.py — Catálogo de símbolos y construcción de <element>.

El catálogo resuelve cada tipo lógico del JSON a un archivo .elmt REAL de la
biblioteca instalada, del que extrae (sin inventar nada):
  - la definición completa (para embeber en <collection>),
  - las terminales (uuid, posición relativa al hotspot, orientación),
  - la posición por defecto de la etiqueta (dynamic_text del .elmt).
"""

from __future__ import annotations

import json
import uuid as uuid_mod
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

# Orientación de terminal: letras en el .elmt -> números en el elemento colocado.
# CONFIRMADO: n->0, s->2 (evidencia en photovoltaique.qet).
# INFERIDO: e->1, w->3 (convención QET; pendiente de confirmar con evidencia e/w).
ORIENTATION_LETTER_TO_NUM = {"n": "0", "e": "1", "s": "2", "w": "3"}

# Valores observados en instancias reales 0.100.0 (docs/QET_FORMAT_NOTES.md §3)
INSTANCE_FONT = "Sans Serif,9,-1,5,0,0,0,0,0,0,normal"
DEFAULT_LABEL_POS = (10.0, -17.5)


@dataclass
class TerminalInfo:
    index: int
    uuid: str          # con llaves, tal como está en el .elmt
    x: str             # string original del archivo (evita floats espurios)
    y: str
    orientation: str   # letra n/e/s/w
    name: str


@dataclass
class SymbolDefinition:
    """Datos extraídos de un .elmt real."""
    type_key: str
    elmt_path: str        # ruta relativa dentro de la colección, ej: a/b/x.elmt
    file_path: Path      # ruta absoluta del .elmt en disco
    definition: ET.Element  # nodo <definition> raíz del .elmt
    terminals: list[TerminalInfo]
    label_pos: tuple[float, float]
    prefix: str

    @property
    def embed_type(self) -> str:
        return f"embed://import/{self.elmt_path}"


def _fmt(value: str) -> str:
    """Normaliza números para atributos (quita ceros espurios de float)."""
    try:
        f = float(value)
        if f == int(f):
            return str(int(f))
        return repr(f)
    except (TypeError, ValueError):
        return str(value)


class SymbolCatalog:
    """Catálogo: tipo lógico -> .elmt real de la biblioteca instalada."""

    DEFAULT_LIBRARY = Path(r"C:\Program Files\QElectroTech\elements")

    def __init__(self, catalog_path: str | Path, library_path: str | Path | None = None):
        self.catalog_path = Path(catalog_path)
        self.library = Path(library_path) if library_path else self.DEFAULT_LIBRARY
        if not self.library.is_dir():
            raise FileNotFoundError(
                f"No se encuentra la biblioteca de QElectroTech: {self.library}")
        self._entries: dict[str, dict] = {}
        self._cache: dict[str, SymbolDefinition] = {}
        self._load()

    def _load(self) -> None:
        if not self.catalog_path.is_file():
            raise FileNotFoundError(f"No existe el catálogo: {self.catalog_path}")
        data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("El catálogo debe ser un objeto JSON")
        self._entries = data

    def has(self, type_key: str) -> bool:
        return type_key in self._entries

    def type_keys(self) -> list[str]:
        return sorted(self._entries.keys())

    def get(self, type_key: str) -> SymbolDefinition:
        """Resuelve un tipo lógico; cachea el parseo del .elmt."""
        if type_key in self._cache:
            return self._cache[type_key]
        if type_key not in self._entries:
            raise KeyError(f"Tipo no registrado en el catálogo: {type_key!r}")
        entry = self._entries[type_key]
        elmt_path = entry["elmt_path"].replace("\\", "/").strip("/")
        file_path = self.library / elmt_path
        if not file_path.is_file():
            raise FileNotFoundError(
                f"El .elmt del tipo {type_key!r} no existe: {file_path}")

        definition = ET.parse(file_path).getroot()
        if definition.tag != "definition":
            raise ValueError(f"{file_path}: raíz inesperada <{definition.tag}>")

        # Terminales en orden de documento = índice usado por las conexiones
        terminals: list[TerminalInfo] = []
        for i, t in enumerate(definition.iter("terminal")):
            terminals.append(TerminalInfo(
                index=i,
                uuid=t.get("uuid", ""),
                x=_fmt(t.get("x", "0")),
                y=_fmt(t.get("y", "0")),
                orientation=t.get("orientation", "n"),
                name=t.get("name", "") or "",
            ))

        # Posición por defecto de la etiqueta: dynamic_text con info_name=label
        label_pos = DEFAULT_LABEL_POS
        for dt in definition.iter("dynamic_text"):
            info = dt.find("info_name")
            if info is not None and (info.text or "") == "label":
                label_pos = (float(dt.get("x", 10)), float(dt.get("y", -17.5)))
                break

        sym = SymbolDefinition(
            type_key=type_key,
            elmt_path=elmt_path,
            file_path=file_path,
            definition=definition,
            terminals=terminals,
            label_pos=label_pos,
            prefix=str(entry.get("prefix", "")),
        )
        self._cache[type_key] = sym
        return sym

    def used_symbols(self, type_keys) -> list[SymbolDefinition]:
        """Definiciones únicas (una por tipo) para embeber en <collection>."""
        seen: dict[str, SymbolDefinition] = {}
        for key in type_keys:
            if key not in seen:
                seen[key] = self.get(key)
        return list(seen.values())


def new_uuid() -> str:
    """UUID de instancia en el formato de QET: {xxxxxxxx-...}."""
    return "{" + str(uuid_mod.uuid4()) + "}"


def build_element(spec, symbol: SymbolDefinition, instance_uuid: str,
                  terminal_ids: list[int]) -> ET.Element:
    """Construye un <element> colocado según el formato observado 0.100.0.

    `terminal_ids` son los id GLOBALES de folio (asignados por diagram.py).
    """
    el = ET.Element("element", {
        "uuid": instance_uuid,
        "orientation": str(spec.orientation),
        "type": symbol.embed_type,
        "x": _fmt(spec.x),
        "y": _fmt(spec.y),
        "z": "10",
        "freezeLabel": "false",
        "prefix": symbol.prefix,
    })

    # <terminals> — copia uuid/posición de la definición, orientación numérica
    terms = ET.SubElement(el, "terminals")
    for i, t in enumerate(symbol.terminals):
        ET.SubElement(terms, "terminal", {
            "id": str(terminal_ids[i]),
            "orientation": ORIENTATION_LETTER_TO_NUM.get(t.orientation, "0"),
            "x": t.x,
            "y": t.y,
            "uuid": t.uuid,
            "type": "Generic",
            "name": t.name,
            "number": "",
            "nameHidden": "0",
        })

    ET.SubElement(el, "inputs")

    # <elementInformations> — núcleo observado en archivos reales
    # (location, comment, formula, label) + metadatos BOM opcionales (spec.info)
    infos = ET.SubElement(el, "elementInformations")
    for name in ("location", "comment", "formula"):
        node = ET.SubElement(infos, "elementInformation", {"show": "1", "name": name})
        value = spec.info_value(name)
        if value:
            node.text = value
    # extras BOM (claves confirmadas en proyectos reales, §3 QET_FORMAT_NOTES)
    for name in ("designation", "description", "manufacturer",
                 "manufacturer_reference", "machine_manufacturer_reference",
                 "supplier", "plant", "unity", "quantity"):
        value = spec.info_value(name)
        if value:
            node = ET.SubElement(infos, "elementInformation", {"show": "1", "name": name})
            node.text = value
    label_info = ET.SubElement(infos, "elementInformation",
                               {"show": "1", "name": "label"})
    label_info.text = spec.resolved_label()

    # <dynamic_texts> — texto dinámico que muestra la etiqueta (uuid NUEVO)
    dyn_texts = ET.SubElement(el, "dynamic_texts")
    dt = ET.SubElement(dyn_texts, "dynamic_elmt_text", {
        "frame": "false",
        "uuid": new_uuid(),
        "Halignment": "AlignLeft",
        "Valignment": "AlignTop",
        "rotation": "0",
        "text_from": "ElementInfo",
        "x": _fmt(symbol.label_pos[0]),
        "font": INSTANCE_FONT,
        "text_width": "-1",
        "keep_visual_rotation": "true",
        "y": _fmt(symbol.label_pos[1]),
    })
    ET.SubElement(dt, "text")
    info = ET.SubElement(dt, "info_name")
    info.text = "label"

    ET.SubElement(el, "texts_groups")
    return el
