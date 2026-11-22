"""validate — Fachada de compatibilidad (deprecated → ``qetgen.validation``)."""

from ._bootstrap import *  # noqa: F401,F403
from qetgen.legacy import validate_project, validate_spec

__all__ = ["validate_project", "validate_spec"]
