"""shapes — Fachada de compatibilidad (deprecated → ``qetgen.exporters.qet``)."""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.legacy import build_rectangle

__all__ = ["build_rectangle"]
