"""diagram — Fachada de compatibilidad (deprecated → ``qetgen.exporters.qet``)."""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.legacy import DiagramBuildResult, build_diagram

__all__ = ["DiagramBuildResult", "build_diagram"]
