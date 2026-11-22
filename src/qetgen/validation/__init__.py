"""Validación del modelo: reglas estructurales y auditoría estética."""

from .structural import (MAX_FONT_SIZE, MIN_FONT_SIZE, ValidationReport,
                         validate_project, validate_spec)

__all__ = [
    "MAX_FONT_SIZE",
    "MIN_FONT_SIZE",
    "ValidationReport",
    "validate_project",
    "validate_spec",
]
