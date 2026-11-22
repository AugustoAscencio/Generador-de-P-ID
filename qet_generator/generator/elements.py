"""elements — Fachada de compatibilidad (deprecated → ``qetgen.core.catalog``)."""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.legacy import (INSTANCE_FONT, ORIENTATION_LETTER_TO_NUM,
                           Port as TerminalInfo, SymbolCatalog,
                           SymbolDefinition, build_element, new_uuid)

__all__ = [
    "INSTANCE_FONT",
    "ORIENTATION_LETTER_TO_NUM",
    "SymbolCatalog",
    "SymbolDefinition",
    "TerminalInfo",
    "build_element",
    "new_uuid",
]
