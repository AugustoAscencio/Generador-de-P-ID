"""Ejecución como módulo: ``python -m qetgen.cli``."""

from __future__ import annotations

import sys

from .main import main

if __name__ == "__main__":
    sys.exit(main())
