"""mcp_server/session.py — Estado del servidor MCP.

El servidor MCP trabaja sobre un **lienzo** (un proyecto en memoria) con un
catálogo de símbolos y una configuración. La sesión encapsula ese estado y
expone las operaciones de alto nivel; las herramientas son funciones puras
sobre la sesión.

Reglas:

* las operaciones son **atómicas**: o se aplican enteras, o no se aplica nada
  (si un elemento no existe, no se crea una conexión a medias);
* los errores son **accionables**: nunca un ``KeyError`` desnudo;
* el núcleo no se toca: aquí solo se orquestan ``core``, ``layout``,
  ``validation`` y ``exporters``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..config import QetGenConfig, default_config_path, load_config
from ..core.catalog import SymbolCatalog, default_catalog_path
from ..core.errors import QetGenError, SpecError
from ..core.io import load_spec, save_spec
from ..core.models import Project, Sheet
from ..core.sheet import SHEET_FORMATS


class ToolError(QetGenError):
    """Error de negocio de una herramienta MCP (mensaje accionable)."""


@dataclass
class Session:
    """Estado compartido del servidor MCP."""

    catalog: SymbolCatalog | None = None
    config: QetGenConfig | None = None
    project: Project | None = None
    #: Ruta del archivo desde el que se cargó el proyecto (opcional).
    source_path: str | None = None
    #: Historial breve de las operaciones (para contexto y auditoría).
    history: list[str] = field(default_factory=list)

    # -- construcción -------------------------------------------------------

    @classmethod
    def create(cls, config_path: str | Path | None = None,
               catalog_path: str | Path | None = None,
               library_path: str | Path | None = None) -> Session:
        """Crea la sesión con el catálogo y la configuración del entorno."""
        config = load_config(config_path or default_config_path())
        catalog = SymbolCatalog(
            catalog_path or default_catalog_path(),
            library_path or config.sources.library_path)
        return cls(catalog=catalog, config=config)

    def _require_catalog(self) -> SymbolCatalog:
        if self.catalog is None:
            raise ToolError(
                "El catálogo de símbolos no está cargado. "
                "Arranca el servidor con una instalación de QElectroTech "
                "o indica --library.")
        return self.catalog

    def _require_config(self) -> QetGenConfig:
        if self.config is None:
            raise ToolError("La configuración no está cargada.")
        return self.config

    def require_project(self) -> Project:
        """Proyecto actual; error accionable si todavía no hay ninguno."""
        if self.project is None:
            raise ToolError(
                "No hay ningún proyecto en el lienzo. "
                "Llama primero a 'crear_diagrama'.")
        return self.project

    def require_sheet(self, folio: int = 1) -> Sheet:
        """Folio solicitado (1..N)."""
        project = self.require_project()
        if folio < 1 or folio > len(project.folios):
            raise ToolError(
                f"El folio {folio} no existe: el proyecto tiene "
                f"{len(project.folios)} folio(s).")
        return project.folios[folio - 1]

    # -- operaciones --------------------------------------------------------

    def create_project(self, titulo: str, formato_hoja: str = "A3_17x8",
                       autor: str = "", archivo: str | None = None) -> Project:
        """Crea un proyecto nuevo o carga uno desde un JSON existente."""
        if formato_hoja not in SHEET_FORMATS:
            raise ToolError(
                f"formato de hoja desconocido: {formato_hoja!r} "
                f"(disponibles: {', '.join(sorted(SHEET_FORMATS))})")
        if archivo:
            path = Path(archivo)
            if not path.is_file():
                raise ToolError(f"No existe el archivo: {path}")
            try:
                self.project = load_spec(path)
            except SpecError as exc:
                raise ToolError(f"No se pudo cargar {path}: {exc}") from exc
            self.source_path = str(path)
            self.history.append(f"proyecto cargado desde {path}")
            return self.project

        sheet = Sheet(title="D-001", order=1, sheet_format=formato_hoja)
        self.project = Project(title=titulo, author=autor, folios=[sheet])
        self.source_path = None
        self.history.append(f"proyecto creado: {titulo}")
        return self.project

    def add_element(self, id: str, tipo: str, x: float, y: float,
                    etiqueta: str | None = None, orientacion: int = 0,
                    bloqueado: bool = False, folio: int = 1) -> dict:
        """Coloca un símbolo en un folio (operación atómica)."""
        catalog = self._require_catalog()
        project = self.require_project()
        sheet = self.require_sheet(folio)

        if not catalog.has(tipo):
            raise ToolError(
                f"Tipo desconocido: {tipo!r}. "
                f"Usa 'listar_simbolos' para ver los {len(catalog.entries())} "
                f"tipos disponibles.")
        if any(el.id == id for el in project.elements):
            raise ToolError(
                f"Ya existe un elemento con id {id!r}: los ids deben ser "
                f"únicos en todo el proyecto.")

        symbol = catalog.get(tipo)
        if etiqueta is None and not symbol.terminal_count:
            pass    # la etiqueta por defecto es el id

        from ..core.models import Component
        component = Component(
            id=id, type=tipo, x=float(x), y=float(y), label=etiqueta,
            orientation=orientacion, locked=bloqueado)
        sheet.elements.append(component)
        self.history.append(f"elemento {id} ({tipo}) en folio {folio}")
        return {
            "id": id,
            "tipo": tipo,
            "folio": folio,
            "x": component.x,
            "y": component.y,
            "orientacion": component.orientation,
            "bloqueado": component.locked,
            "terminales": symbol.terminal_count,
        }

    def connect(self, desde: str, hasta: str, terminal_desde: int = 0,
                terminal_hasta: int = 0, tipo: str = "cable",
                numero: str = "", bloqueado: bool = False,
                folio: int = 1) -> dict:
        """Conecta dos elementos (operación atómica)."""
        sheet = self.require_sheet(folio)
        catalog = self._require_catalog()

        by_id = {el.id: el for el in sheet.elements}
        for cid in (desde, hasta):
            if cid not in by_id:
                raise ToolError(
                    f"El elemento {cid!r} no existe en el folio {folio}. "
                    f"Elementos del folio: {', '.join(sorted(by_id)) or '(ninguno)'}")
        for component, terminal, label in ((by_id[desde], terminal_desde, "origen"),
                                           (by_id[hasta], terminal_hasta, "destino")):
            symbol = catalog.get(component.type)
            if terminal >= symbol.terminal_count:
                raise ToolError(
                    f"El elemento {component.id!r} ({component.type}) tiene "
                    f"{symbol.terminal_count} terminal(es); la terminal {label} "
                    f"{terminal} no existe.")

        from ..core.models import Connection
        connection = Connection(
            from_id=desde, to_id=hasta, from_terminal=terminal_desde,
            to_terminal=terminal_hasta, kind=tipo, number=numero,
            locked=bloqueado)
        sheet.connections.append(connection)
        self.history.append(f"conductor {connection.key()}")
        return {"clave": connection.key(), "folio": folio, "tipo": tipo}

    def export(self, ruta: str, formato: str = "qet") -> dict:
        """Exporta el proyecto a ``.qet`` o a JSON canónico."""
        project = self.require_project()
        catalog = self._require_catalog()
        path = Path(ruta)
        try:
            if formato == "json":
                save_spec(project, path)
            else:
                from ..exporters.qet import export_qet
                export_qet(project, catalog, path)
        except OSError as exc:
            raise ToolError(f"No se pudo escribir {path}: {exc}") from exc
        size = path.stat().st_size if path.is_file() else 0
        self.history.append(f"exportado {path}")
        return {"ruta": str(path), "formato": formato, "bytes": size}

    def summary(self, folio: int | None = None) -> dict:
        """Resumen del proyecto (o de un folio)."""
        project = self.require_project()
        if folio is not None:
            sheet = self.require_sheet(folio)
            return {
                "proyecto": project.title,
                "folio": folio,
                "titulo": sheet.title,
                "elementos": len(sheet.elements),
                "conexiones": len(sheet.connections),
                "textos": len(sheet.texts),
                "bloques": len(sheet.shapes),
                "formato_hoja": sheet.sheet_format,
            }
        return {
            "proyecto": project.title,
            "autor": project.author,
            "folios": len(project.folios),
            "elementos": len(project.elements),
            "conexiones": sum(len(f.connections) for f in project.folios),
            "textos": sum(len(f.texts) for f in project.folios),
            "bloques": sum(len(f.shapes) for f in project.folios),
            "detalle": [
                {
                    "folio": index,
                    "titulo": sheet.title,
                    "elementos": len(sheet.elements),
                    "conexiones": len(sheet.connections),
                }
                for index, sheet in enumerate(project.folios, start=1)
            ],
        }


__all__ = ["Session", "ToolError"]
