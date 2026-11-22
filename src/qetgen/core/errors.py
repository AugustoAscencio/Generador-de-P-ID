"""Errores del dominio.

Jerarquía única para que el CLI y el servidor MCP puedan mapear cada fallo a
un código de salida y a un mensaje accionable, sin块 except genéricos.
"""

from __future__ import annotations


class QetGenError(Exception):
    """Raíz de todos los errores del paquete."""

    code = "qetgen_error"


class SpecError(QetGenError):
    """El JSON de entrada no cumple el esquema esperado."""

    code = "spec_error"


class CatalogError(QetGenError):
    """El catálogo de símbolos o la biblioteca de QElectroTech no son válidos."""

    code = "catalog_error"


class GeometryError(QetGenError):
    """Una operación geométrica no puede resolverse (p. ej. no hay ruta)."""

    code = "geometry_error"


class ValidationError(QetGenError):
    """El modelo no pasa la validación estructural o estética."""

    code = "validation_error"

    def __init__(self, issues: list[str]):
        self.issues = list(issues)
        super().__init__(f"{len(self.issues)} problema(s) de validación")


__all__ = [
    "QetGenError",
    "SpecError",
    "CatalogError",
    "GeometryError",
    "ValidationError",
]
