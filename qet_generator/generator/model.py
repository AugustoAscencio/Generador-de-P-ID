"""model.py — Modelo de datos del JSON de entrada.

Formato nuevo (multi-folio):

    {
      "project":  { "title": "...", "author": "..." },
      "diagrams": [
        { "title": "Folio 1", "order": 1,
          "elements":    [ { "id": "...", "type": "...", "x": 0, "y": 0,
                             "label": "...", "info": {"designation": "..."} } ],
          "connections": [ { "from": "...", "from_terminal": 0, "to": "...", "to_terminal": 0 } ],
          "texts":       [ { "x": 0, "y": 0, "text": "..." } ] },
        { "title": "Folio 2", "order": 2, ... }
      ]
    }

Formato antiguo (mono-folio plano) sigue soportado por compatibilidad:
"diagram" + "elements"/"connections"/"texts" a nivel raíz.

El JSON es una representación estructurada de la especificación técnica;
el generador SOLO transforma esto en .qet. Nunca al revés.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# Claves de <elementInformation> confirmadas en proyectos reales (§3 del
# QET_FORMAT_NOTES.md). "label" se gestiona aparte (campo propio del elemento).
KNOWN_INFO_KEYS = {
    "location", "comment", "formula", "designation", "description",
    "manufacturer", "manufacturer_reference", "machine_manufacturer_reference",
    "supplier", "plant", "unity", "quantity",
}


class SpecError(Exception):
    """Error de lectura/estructura del JSON."""


@dataclass
class ElementSpec:
    id: str
    type: str
    x: float
    y: float
    label: str | None = None
    orientation: int = 0
    info: dict[str, str] = field(default_factory=dict)

    def resolved_label(self) -> str:
        return self.label if self.label is not None else self.id

    def info_value(self, key: str) -> str:
        return str(self.info.get(key, "") or "")


@dataclass
class ConnectionSpec:
    from_id: str
    to_id: str
    from_terminal: int = 0
    to_terminal: int = 0

    def key(self) -> str:
        return f"{self.from_id}[{self.from_terminal}] -> {self.to_id}[{self.to_terminal}]"


@dataclass
class TextSpec:
    x: float
    y: float
    text: str
    rotation: int = 0
    size: int = 9          # tamaño de fuente (pt), evidencia: atributo size="9"


@dataclass
class ShapeSpec:
    """Rectángulo funcional (bloque de diagrama). Formato <shape> confirmado
    en photovoltaique.qet: attrs x1/y1/x2/y2 + <pen/> + <brush/>."""
    x1: float
    y1: float
    x2: float
    y2: float
    color: str = "#004080"       # color de línea (pen)
    width: float = 1.0           # widthF del pen
    fill: str | None = None      # None=NoBrush; "#rrggbb"=SolidPattern
    dash: bool = False           # pen DashLine


@dataclass
class FolioSpec:
    """Un folio (<diagram>) del proyecto."""
    title: str = ""
    author: str = ""
    indexrev: str = "A"
    date: str | None = None          # AAAAMMDD; None = hoy al generar
    order: int | None = None         # None = posición en la lista (1-based)
    elements: list[ElementSpec] = field(default_factory=list)
    connections: list[ConnectionSpec] = field(default_factory=list)
    texts: list[TextSpec] = field(default_factory=list)
    shapes: list[ShapeSpec] = field(default_factory=list)


@dataclass
class ProjectSpec:
    title: str
    author: str = ""
    filename: str = ""
    library_path: str | None = None
    folios: list[FolioSpec] = field(default_factory=list)

    @property
    def elements(self) -> list[ElementSpec]:
        """Todos los elementos del proyecto (todos los folios)."""
        return [el for folio in self.folios for el in folio.elements]


def _require(d: dict, key: str, ctx: str):
    if key not in d:
        raise SpecError(f"Falta el campo '{key}' en {ctx}")
    return d[key]


def _num(value, ctx: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SpecError(f"Se esperaba un número en {ctx}, llegó: {value!r}")
    return float(value)


def _parse_elements(raw, ctx: str) -> list[ElementSpec]:
    if not isinstance(raw, list):
        raise SpecError(f"{ctx} debe ser una lista")
    out: list[ElementSpec] = []
    for i, el in enumerate(raw):
        ectx = f"{ctx}[{i}]"
        if not isinstance(el, dict):
            raise SpecError(f"{ectx} debe ser un objeto")
        info_raw = el.get("info") or {}
        if not isinstance(info_raw, dict):
            raise SpecError(f"{ectx}.info debe ser un objeto")
        info = {str(k): str(v) for k, v in info_raw.items() if v not in (None, "")}
        out.append(ElementSpec(
            id=str(_require(el, "id", ectx)),
            type=str(_require(el, "type", ectx)),
            x=_num(_require(el, "x", ectx), f"{ectx}.x"),
            y=_num(_require(el, "y", ectx), f"{ectx}.y"),
            label=str(el["label"]) if el.get("label") is not None else None,
            orientation=int(el.get("orientation", 0)),
            info=info,
        ))
    return out


def _parse_connections(raw, ctx: str) -> list[ConnectionSpec]:
    if not isinstance(raw, list):
        raise SpecError(f"{ctx} debe ser una lista")
    out: list[ConnectionSpec] = []
    for i, cn in enumerate(raw):
        cctx = f"{ctx}[{i}]"
        if not isinstance(cn, dict):
            raise SpecError(f"{cctx} debe ser un objeto")
        out.append(ConnectionSpec(
            from_id=str(_require(cn, "from", cctx)),
            to_id=str(_require(cn, "to", cctx)),
            from_terminal=int(cn.get("from_terminal", 0)),
            to_terminal=int(cn.get("to_terminal", 0)),
        ))
    return out


def _parse_texts(raw, ctx: str) -> list[TextSpec]:
    if not isinstance(raw, list):
        raise SpecError(f"{ctx} debe ser una lista")
    out: list[TextSpec] = []
    for i, tx in enumerate(raw):
        tctx = f"{ctx}[{i}]"
        if not isinstance(tx, dict):
            raise SpecError(f"{tctx} debe ser un objeto")
        out.append(TextSpec(
            x=_num(_require(tx, "x", tctx), f"{tctx}.x"),
            y=_num(_require(tx, "y", tctx), f"{tctx}.y"),
            text=str(_require(tx, "text", tctx)),
            rotation=int(tx.get("rotation", 0)),
            size=int(tx.get("size", 9)),
        ))
    return out


_COLOR_RE = None  # compilado perezosamente en validate


def _valid_color(value: str) -> bool:
    import re
    global _COLOR_RE
    if _COLOR_RE is None:
        _COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
    return bool(_COLOR_RE.match(value or ""))


def _parse_shapes(raw, ctx: str) -> list[ShapeSpec]:
    if not isinstance(raw, list):
        raise SpecError(f"{ctx} debe ser una lista")
    out: list[ShapeSpec] = []
    for i, sh in enumerate(raw):
        sctx = f"{ctx}[{i}]"
        if not isinstance(sh, dict):
            raise SpecError(f"{sctx} debe ser un objeto")
        fill = sh.get("fill")
        if fill is not None and not _valid_color(str(fill)):
            raise SpecError(f"{sctx}.fill debe ser '#rrggbb' o null")
        color = str(sh.get("color", "#004080"))
        if not _valid_color(color):
            raise SpecError(f"{sctx}.color debe ser '#rrggbb'")
        out.append(ShapeSpec(
            x1=_num(_require(sh, "x1", sctx), f"{sctx}.x1"),
            y1=_num(_require(sh, "y1", sctx), f"{sctx}.y1"),
            x2=_num(_require(sh, "x2", sctx), f"{sctx}.x2"),
            y2=_num(_require(sh, "y2", sctx), f"{sctx}.y2"),
            color=color,
            width=_num(sh.get("width", 1.0), f"{sctx}.width"),
            fill=str(fill) if fill else None,
            dash=bool(sh.get("dash", False)),
        ))
    return out


def _parse_folio(raw: dict, order: int, default_author: str) -> FolioSpec:
    return FolioSpec(
        title=str(raw.get("title", "") or ""),
        author=str(raw.get("author", "") or default_author),
        indexrev=str(raw.get("indexrev", "A") or "A"),
        date=str(raw["date"]) if raw.get("date") else None,
        order=int(raw["order"]) if raw.get("order") is not None else order,
        elements=_parse_elements(raw.get("elements") or [], "elements"),
        connections=_parse_connections(raw.get("connections") or [], "connections"),
        texts=_parse_texts(raw.get("texts") or [], "texts"),
        shapes=_parse_shapes(raw.get("shapes") or [], "shapes"),
    )


def load_spec(path: str | Path) -> ProjectSpec:
    """Lee y traduce el JSON de entrada a ProjectSpec (multi o mono-folio)."""
    path = Path(path)
    if not path.is_file():
        raise SpecError(f"No existe el archivo: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SpecError(f"JSON mal formado en {path}: {e}") from e

    project = _require(data, "project", "raíz del documento") or {}
    if not isinstance(project, dict):
        raise SpecError("'project' debe ser un objeto")
    pj_title = str(_require(project, "title", "project") or "").strip()
    if not pj_title:
        raise SpecError("project.title no puede estar vacío")

    spec = ProjectSpec(
        title=pj_title,
        author=str(project.get("author", "") or ""),
        filename=str(project.get("filename", "") or ""),
        library_path=project.get("library_path"),
    )

    if "diagrams" in data:
        # --- formato nuevo: multi-folio ---
        diagrams = data["diagrams"]
        if not isinstance(diagrams, list):
            raise SpecError("'diagrams' debe ser una lista")
        for i, dg in enumerate(diagrams, start=1):
            if not isinstance(dg, dict):
                raise SpecError(f"diagrams[{i}] debe ser un objeto")
            spec.folios.append(_parse_folio(dg, i, spec.author))
    else:
        # --- formato antiguo: mono-folio plano (compatibilidad) ---
        spec.folios.append(_parse_folio({
            "title": (data.get("diagram") or {}).get("title", ""),
            "author": (data.get("diagram") or {}).get("author", spec.author),
            "indexrev": (data.get("diagram") or {}).get("indexrev", "A"),
            "date": (data.get("diagram") or {}).get("date"),
            "elements": data.get("elements"),
            "connections": data.get("connections"),
            "texts": data.get("texts"),
        }, 1, spec.author))

    if not spec.folios:
        raise SpecError("El proyecto debe tener al menos un folio")
    return spec
