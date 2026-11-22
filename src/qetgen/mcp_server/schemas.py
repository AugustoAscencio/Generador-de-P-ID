"""mcp_server/schemas.py — Esquemas de entrada de las herramientas MCP.

Cada herramienta tiene un modelo Pydantic **estricto** (``extra="forbid"``).
El JSON Schema que el servidor publica como ``inputSchema`` se genera con
``model_json_schema()``: hay **una sola fuente de verdad** para los tipos, y
el mismo modelo valida la entrada en el servidor.

Nombres de campo en español (la herramienta se usa en español) pero en
``snake_case`` para mantener la convención del resto del proyecto.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _Input(BaseModel):
    """Base común de las entradas: estricta y con validación al asignar."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=False,
    )


class CrearDiagramaInput(_Input):
    """Crea un proyecto nuevo (o carga uno existente desde un JSON)."""

    titulo: str = Field(min_length=1, description="Título del proyecto")
    formato_hoja: str = Field(
        default="A3_17x8",
        description="Preset de hoja (A3_17x8, A3_18x9, A4_11x7, …)")
    autor: str = Field(default="", description="Autor del proyecto")
    archivo: str | None = Field(
        default=None,
        description="Ruta de un JSON de especificación existente a cargar "
                    "(tiene prioridad sobre el resto de parámetros)")

    @field_validator("titulo")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("el título no puede estar vacío")
        return value


class ListarSimbolosInput(_Input):
    """Filtra el catálogo de símbolos reales de QElectroTech."""

    tipo: str | None = Field(
        default=None, description="Tipo lógico exacto (ej. 'pv_cell')")
    incluir_geometria: bool = Field(
        default=True, description="Incluir caja, terminales y etiqueta")


class AgregarElementoInput(_Input):
    """Coloca un símbolo en un folio."""

    id: str = Field(min_length=1, description="Identificador único del elemento")
    tipo: str = Field(min_length=1, description="Tipo lógico del catálogo")
    x: float = Field(description="X del hotspot (px)")
    y: float = Field(description="Y del hotspot (px)")
    etiqueta: str | None = Field(default=None, description="Etiqueta visible")
    orientacion: int = Field(
        default=0, ge=0, le=3, description="Rotación del símbolo (0..3)")
    bloqueado: bool = Field(
        default=False, description="Si es True, el auto-layout no lo mueve")
    folio: int = Field(default=1, ge=1, description="Folio (1..N)")

    @field_validator("id")
    @classmethod
    def _id_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("el id no puede estar vacío")
        return value


class ConectarElementosInput(_Input):
    """Crea un conductor entre dos terminales."""

    desde: str = Field(min_length=1, description="Id del elemento origen")
    hasta: str = Field(min_length=1, description="Id del elemento destino")
    terminal_desde: int = Field(default=0, ge=0, description="Terminal origen")
    terminal_hasta: int = Field(default=0, ge=0, description="Terminal destino")
    tipo: str = Field(
        default="cable", description="Naturaleza del enlace: cable, pipe, signal o bus")
    numero: str = Field(default="", description="Número de conductor (autonumeración)")
    bloqueado: bool = Field(
        default=False, description="Si es True, el router no recalcula la ruta")
    folio: int = Field(default=1, ge=1, description="Folio (1..N)")


class EjecutarAutoLayoutInput(_Input):
    """Ejecuta el motor de layout (snap, auto-layout y routing)."""

    folio: int | None = Field(
        default=None, description="Folio a procesar (1..N); None = todos")
    snap: bool = Field(default=False, description="Alinear antes a la rejilla")
    aplicar: bool = Field(
        default=True, description="False = simulación, no modifica el proyecto")
    ignorar_bloqueados: bool = Field(
        default=False, description="Ignorar locked:true (desactiva el modo híbrido)")


class ValidarEsteticaInput(_Input):
    """Audita el proyecto actual (sin parámetros: se audita el estado)."""


class ObtenerResumenCanvasInput(_Input):
    """Resumen del proyecto (o de un folio concreto)."""

    folio: int | None = Field(
        default=None, description="Resumen de un folio (1..N); None = proyecto")


class ExportarArchivoInput(_Input):
    """Exporta el proyecto a ``.qet`` o a JSON canónico."""

    ruta: str = Field(min_length=1, description="Ruta del archivo de salida")
    formato: str = Field(default="qet", description="'qet' o 'json'")

    @field_validator("formato")
    @classmethod
    def _known_format(cls, value: str) -> str:
        lowered = value.strip().lower()
        if lowered not in {"qet", "json"}:
            raise ValueError(f"formato desconocido: {value!r} (usa 'qet' o 'json')")
        return lowered


__all__ = [
    "AgregarElementoInput",
    "ConectarElementosInput",
    "CrearDiagramaInput",
    "EjecutarAutoLayoutInput",
    "ExportarArchivoInput",
    "ListarSimbolosInput",
    "ObtenerResumenCanvasInput",
    "ValidarEsteticaInput",
]
