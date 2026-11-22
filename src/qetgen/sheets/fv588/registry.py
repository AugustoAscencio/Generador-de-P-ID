"""Registro documental del caso FV 588 módulos.

Estructura objetivo de los 18 planos. Es la **única** fuente de verdad del
inventario (la v0.1 lo tenía duplicado en ``tools/build_sheets.py`` y en
``generator/sheets.py``).
"""

from __future__ import annotations

PROJECT_TITLE = "PROYECTO FV 588 MÓDULOS — SEGUEIDOR BIAXIAL 8×650 Wp"
PROJECT_AUTHOR = "Documentación eléctrica (Generador QET)"
PROJECT_FILENAME = "Proyecto_FV_588_Modulos.qet"

#: (código, título) de cada folio del paquete.
ESTRUCTURA_18: list[tuple[str, str]] = [
    ("D-001", "Arquitectura del sistema / índice"),
    ("D-002", "Diagrama general del módulo tipo"),
    ("D-003", "String fotovoltaico 8 paneles"),
    ("D-004", "Protección DC (QF-DC + SPD)"),
    ("D-005", "Alimentación 24 VDC"),
    ("D-006", "Eje de elevación"),
    ("D-007", "Eje de azimut"),
    ("D-008", "Sensores y entradas"),
    ("D-009", "Sistema de viento / STOW"),
    ("D-010", "Mapa de E/S"),
    ("D-011", "Diagrama de estados"),
    ("D-012", "Seguridad y enclavamientos"),
    ("D-013", "Comunicaciones RS485/IoT"),
    ("D-014", "Puesta a tierra TT"),
    ("D-015", "Canalizaciones"),
    ("D-016", "Borneras"),
    ("D-017", "Interfaz con planta"),
    ("D-018", "Módulo tipo × 588"),
]

#: Títulos canónicos (con el prefijo D-0XX) en orden de folio.
SHEET_TITLES: list[str] = [f"{code} — {name}" for code, name in ESTRUCTURA_18]

__all__ = [
    "ESTRUCTURA_18",
    "PROJECT_AUTHOR",
    "PROJECT_FILENAME",
    "PROJECT_TITLE",
    "SHEET_TITLES",
]
