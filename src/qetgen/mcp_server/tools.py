"""mcp_server/tools.py — Las herramientas atómicas del servidor MCP.

Cada herramienta es una operación **completa y tipada**:

* recibe un modelo Pydantic estricto (su JSON Schema es el ``inputSchema``
  publicado por el servidor),
* ejecuta **una** acción sobre el lienzo,
* devuelve un diccionario serializable (el mismo contenido va al texto y al
  ``structuredContent``).

Los nombres están en español porque la herramienta se usa en español; los
parámetros van en ``snake_case``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from ..core.catalog import SymbolCatalog
from ..layout.pipeline import LayoutOptions, apply_layout
from ..validation.aesthetics import validate_aesthetics
from ..validation.structural import validate_project
from .schemas import (AgregarElementoInput, ConectarElementosInput,
                       CrearDiagramaInput, EjecutarAutoLayoutInput,
                       ExportarArchivoInput, ListarSimbolosInput,
                       ObtenerResumenCanvasInput, ValidarEsteticaInput)
from .session import Session, ToolError

#: Tipo de manejador: recibe la sesión y los argumentos ya validados.
Handler = Callable[[Session, dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class Tool:
    """Herramienta MCP: nombre, esquema y manejador."""

    name: str
    title: str
    description: str
    input_model: type[BaseModel]
    handler: Handler

    @property
    def input_schema(self) -> dict:
        """JSON Schema de la entrada (generado del modelo Pydantic)."""
        schema = self.input_model.model_json_schema()
        schema.setdefault("title", self.title)
        return schema

    def as_dict(self) -> dict:
        """Descripción en el formato del protocolo MCP."""
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "inputSchema": self.input_schema,
        }

    def call(self, session: Session, arguments: dict | None) -> dict:
        """Valida la entrada y ejecuta la herramienta."""
        payload = arguments or {}
        try:
            model = self.input_model(**payload)
        except ValidationError as exc:
            details = "; ".join(
                f"{'.'.join(str(p) for p in issue['loc'])}: {issue['msg']}"
                for issue in exc.errors())
            raise ToolError(f"Entrada inválida para {self.name} → {details}") from exc
        return self.handler(session, model.model_dump())


# --------------------------------------------------------------------------
# Manejadores
# --------------------------------------------------------------------------

def _crear_diagrama(session: Session, args: dict) -> dict:
    project = session.create_project(
        titulo=args["titulo"],
        formato_hoja=args.get("formato_hoja", "A3_17x8"),
        autor=args.get("autor", ""),
        archivo=args.get("archivo"))
    return {
        "titulo": project.title,
        "folios": len(project.folios),
        "elementos": len(project.elements),
        "mensaje": (f"Proyecto «{project.title}» listo con {len(project.folios)} "
                    f"folio(s)."),
    }


def _listar_simbolos(session: Session, args: dict) -> dict:
    catalog = session.catalog
    if catalog is None:
        raise ToolError("El catálogo de símbolos no está cargado.")
    tipo = args.get("tipo")
    incluir = args.get("incluir_geometria", True)

    if tipo:
        if not catalog.has(tipo):
            raise ToolError(
                f"Tipo desconocido: {tipo!r}. "
                f"Tipos disponibles: {', '.join(catalog.type_keys())}")
        keys = [tipo]
    else:
        keys = catalog.type_keys()

    symbols = []
    for key in keys:
        symbol = catalog.get(key)
        entry: dict[str, Any] = {
            "tipo": key,
            "descripcion": symbol.description,
            "prefijo": symbol.prefix,
            "terminales": symbol.terminal_count,
        }
        if incluir:
            entry["caja_reservada"] = list(symbol.placement_bounds.as_tuple())
            entry["caja_tinta"] = list(symbol.ink_bounds.as_tuple())
            entry["ancho"] = symbol.width
            entry["alto"] = symbol.height
            entry["posicion_etiqueta"] = list(symbol.label_pos)
            entry["terminales_detalle"] = [
                {"indice": port.index, "nombre": port.name,
                 "numero": port.number, "orientacion": port.orientation,
                 "x": port.x, "y": port.y}
                for port in symbol.terminals
            ]
        symbols.append(entry)

    return {"total": len(symbols), "simbolos": symbols}


def _agregar_elemento(session: Session, args: dict) -> dict:
    return session.add_element(
        id=args["id"], tipo=args["tipo"], x=args["x"], y=args["y"],
        etiqueta=args.get("etiqueta"), orientacion=args.get("orientacion", 0),
        bloqueado=args.get("bloqueado", False), folio=args.get("folio", 1))


def _conectar_elementos(session: Session, args: dict) -> dict:
    return session.connect(
        desde=args["desde"], hasta=args["hasta"],
        terminal_desde=args.get("terminal_desde", 0),
        terminal_hasta=args.get("terminal_hasta", 0),
        tipo=args.get("tipo", "cable"), numero=args.get("numero", ""),
        bloqueado=args.get("bloqueado", False), folio=args.get("folio", 1))


def _ejecutar_auto_layout(session: Session, args: dict) -> dict:
    project = session.require_project()
    config = session.config
    catalog = session.catalog
    if catalog is None or config is None:
        raise ToolError("El motor de layout necesita el catálogo y la configuración.")

    options = LayoutOptions(
        snap=args.get("snap", False),
        auto_layout=True,
        route=config.layout.route_manhattan,
        respect_locked=not args.get("ignorar_bloqueados", False),
        folio=args.get("folio"))

    outcome = apply_layout(project, catalog, config, options)
    if args.get("aplicar", True):
        session.project = outcome.project
        session.history.append(
            f"auto-layout: {outcome.moved_count} movido(s)")
    else:
        session.history.append("auto-layout (simulación)")

    payload = outcome.as_dict()
    payload["aplicado"] = bool(args.get("aplicar", True))
    return payload


def _validar_estetica(session: Session, args: dict) -> dict:
    project = session.require_project()
    catalog = session.catalog
    config = session.config
    if catalog is None or config is None:
        raise ToolError("La validación necesita el catálogo y la configuración.")

    structural = validate_project(project, catalog)
    aesthetic = validate_aesthetics(project, catalog, config)
    return {
        "ok": structural.ok and aesthetic.ok,
        "estructura": {
            "ok": structural.ok,
            "errores": [str(issue) for issue in structural.errors],
            "avisos": [str(issue) for issue in structural.warnings],
        },
        "estetica": aesthetic.as_dict(),
    }


def _obtener_resumen_canvas(session: Session, args: dict) -> dict:
    return session.summary(folio=args.get("folio"))


def _exportar_archivo(session: Session, args: dict) -> dict:
    return session.export(ruta=args["ruta"], formato=args.get("formato", "qet"))


# --------------------------------------------------------------------------
# Registro
# --------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="crear_diagrama",
        title="Crear diagrama",
        description=(
            "Crea un proyecto de documentación eléctrica nuevo (o carga uno "
            "existente desde un JSON). Devuelve el título y el número de "
            "folios. Usa 'agregar_elemento' y 'conectar_elementos' para "
            "rellenarlo."),
        input_model=CrearDiagramaInput,
        handler=_crear_diagrama),
    Tool(
        name="listar_simbolos",
        title="Listar símbolos",
        description=(
            "Lista los símbolos reales disponibles en la biblioteca de "
            "QElectroTech (tipo lógico, descripción, terminales y geometría). "
            "Filtra con 'tipo' para obtener uno solo."),
        input_model=ListarSimbolosInput,
        handler=_listar_simbolos),
    Tool(
        name="agregar_elemento",
        title="Agregar elemento",
        description=(
            "Coloca un símbolo en un folio, con coordenadas del hotspot, "
            "orientación (0..3) y etiqueta. Marca 'bloqueado' para que el "
            "auto-layout no lo mueva."),
        input_model=AgregarElementoInput,
        handler=_agregar_elemento),
    Tool(
        name="conectar_elementos",
        title="Conectar elementos",
        description=(
            "Crea un conductor entre dos terminales de dos elementos del "
            "mismo folio. Valida que los elementos y las terminales existan."),
        input_model=ConectarElementosInput,
        handler=_conectar_elementos),
    Tool(
        name="ejecutar_auto_layout",
        title="Ejecutar auto-layout",
        description=(
            "Reorganiza el plano en columnas lógicas, respeta los elementos "
            "con 'bloqueado' true (modo híbrido) y calcula las rutas "
            "ortogonales de los conductores. Usa 'aplicar' false para "
            "simular sin modificar nada."),
        input_model=EjecutarAutoLayoutInput,
        handler=_ejecutar_auto_layout),
    Tool(
        name="validar_estetica",
        title="Validar estética",
        description=(
            "Audita el proyecto: solapes, textos desbordados, legibilidad, "
            "cableado y avisos de estructura. Devuelve los diagnósticos con "
            "código, severidad y sugerencia de corrección."),
        input_model=ValidarEsteticaInput,
        handler=_validar_estetica),
    Tool(
        name="obtener_resumen_canvas",
        title="Obtener resumen del lienzo",
        description=(
            "Resume el estado actual del lienzo: folios, elementos, "
            "conductores, textos y bloques (del proyecto entero o de un folio)."),
        input_model=ObtenerResumenCanvasInput,
        handler=_obtener_resumen_canvas),
    Tool(
        name="exportar_archivo",
        title="Exportar archivo",
        description=(
            "Guarda el proyecto como '.qet' editable para QElectroTech o como "
            "JSON canónico, en la ruta indicada."),
        input_model=ExportarArchivoInput,
        handler=_exportar_archivo),
]

TOOLS_BY_NAME: dict[str, Tool] = {tool.name: tool for tool in TOOLS}


def list_tools() -> list[dict]:
    """Descripción de todas las herramientas (formato MCP)."""
    return [tool.as_dict() for tool in TOOLS]


def call_tool(session: Session, name: str, arguments: dict | None = None) -> dict:
    """Ejecuta una herramienta por su nombre."""
    tool = TOOLS_BY_NAME.get(name)
    if tool is None:
        raise ToolError(
            f"Herramienta desconocida: {name!r}. "
            f"Disponibles: {', '.join(sorted(TOOLS_BY_NAME))}")
    return tool.call(session, arguments or {})


def _dumps(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


__all__ = ["TOOLS", "TOOLS_BY_NAME", "Tool", "call_tool", "list_tools"]
