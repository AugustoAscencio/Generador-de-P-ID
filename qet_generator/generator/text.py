"""text — Fachada de compatibilidad (deprecated → ``qetgen.exporters.qet``)."""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.legacy import INSTANCE_FONT, build_text, wrap_html

__all__ = ["INSTANCE_FONT", "build_text", "wrap_html"]
