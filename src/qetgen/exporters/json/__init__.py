"""Exportador JSON canónico (ida y vuelta sin pérdida)."""

from __future__ import annotations

import json
from pathlib import Path

from ...core.io import project_to_dict


def project_to_json(project, indent: int | None = 2) -> str:
    """Serializa el proyecto a JSON (UTF-8, sin BOM)."""
    return json.dumps(project_to_dict(project), ensure_ascii=False, indent=indent)


def export_json(project, output_path: str | Path, indent: int | None = 2) -> Path:
    """Escribe el proyecto como JSON canónico."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(project_to_json(project, indent=indent))
        handle.write("\n")
    return output_path


__all__ = ["export_json", "project_to_json"]
