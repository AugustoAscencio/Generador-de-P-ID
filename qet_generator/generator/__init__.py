"""generator — Fachada de compatibilidad de la v0.1 (deprecated).

> **Deprecated:** el motor canónico vive en ``src/qetgen`` (v1.0).
> Este paquete se conserva **solo** para no romper código y scripts que
> usan ``import generator.*``. Se eliminará en la v2.0.

No hay lógica aquí: todo se re-exporta desde :mod:`qetgen.legacy`.
"""

from ._bootstrap import *  # noqa: F401,F403  (añade src/ al sys.path)
from qetgen.legacy import *  # noqa: F401,F403
from qetgen.legacy import __all__ as _legacy_all

__version__ = "0.1.0"

__all__ = list(_legacy_all) + ["__version__"]
