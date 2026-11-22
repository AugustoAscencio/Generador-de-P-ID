"""project — Fachada de compatibilidad (deprecated → ``qetgen.exporters.qet``)."""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.legacy import build_project, export_project

__all__ = ["build_project", "export_project"]
