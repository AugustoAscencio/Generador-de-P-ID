"""builders — Fachada de compatibilidad (deprecated → ``qetgen.sheets.fv588``).

> **Deprecated:** el contenido de ingeniería del caso FV 588 vive ahora en
> ``src/qetgen/sheets/fv588/builders.py``. Esta fachada re-exporta la API.
"""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.sheets.fv588.builders import (build_d002, build_d003,
                                           build_module_folios,
                                           create_aux_24vdc, create_dc_protection,
                                           create_pv_string, folio_to_dict)

__all__ = [
    "build_d002",
    "build_d003",
    "build_module_folios",
    "create_aux_24vdc",
    "create_dc_protection",
    "create_pv_string",
    "folio_to_dict",
]
