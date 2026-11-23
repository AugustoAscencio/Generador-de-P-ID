"""Caso de aplicación: sistema fotovoltaico de 588 módulos × 8 paneles.

Filosofía: **MÓDULO TIPO × 588**. Se documenta el módulo una vez y se escala
mediante arquitectura de repetición; nunca 588 dibujos duplicados.

Trazabilidad: cada dato procede del documento técnico del proyecto (Doc1) o
del requisito explícito de 588 módulos. Lo no confirmado se marca
``PENDIENTE DE VERIFICACIÓN`` en el propio plano.
"""

from .builders import (
    build_module_folios,
    create_aux_24vdc,
    create_dc_protection,
    create_pv_string,
    folio_to_dict,
)
from .registry import ESTRUCTURA_18, PROJECT_AUTHOR, PROJECT_FILENAME, PROJECT_TITLE, SHEET_TITLES
from .sheets import (
    build_all,
    build_d001,
    build_d004,
    build_d005,
    build_d006,
    build_d007,
    build_d008,
    build_d009,
    build_d010,
    build_d011,
    build_d012,
    build_d013,
    build_d014,
    build_d015,
    build_d016,
    build_d017,
    build_d018,
)


def build_project():
    """Construye el :class:`qetgen.core.models.Project` completo del caso FV 588."""
    from ...core.models import Project

    return Project(
        title=PROJECT_TITLE,
        author=PROJECT_AUTHOR,
        filename=PROJECT_FILENAME,
        folios=build_all(),
    )


__all__ = [
    "ESTRUCTURA_18",
    "PROJECT_AUTHOR",
    "PROJECT_FILENAME",
    "PROJECT_TITLE",
    "SHEET_TITLES",
    "build_all",
    "build_d001",
    "build_d004",
    "build_d005",
    "build_d006",
    "build_d007",
    "build_d008",
    "build_d009",
    "build_d010",
    "build_d011",
    "build_d012",
    "build_d013",
    "build_d014",
    "build_d015",
    "build_d016",
    "build_d017",
    "build_d018",
    "build_module_folios",
    "build_project",
    "create_aux_24vdc",
    "create_dc_protection",
    "create_pv_string",
    "folio_to_dict",
]
