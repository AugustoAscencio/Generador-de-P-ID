"""tools/check_doc_links.py — Comprueba que los enlaces de la documentación existen.

Recorre los Markdown del repositorio (raíz y ``docs/``) y verifica que cada
enlace relativo apunte a un archivo que exista. Un enlace roto en el README
es un fallo de documentación, no un detalle menor: el CI lo detecta.

Script en Python (y no un bloque heredoc en el YAML) para que funcione igual
en ``bash`` (Linux) y en ``pwsh`` (Windows).

Salida: 0 si no hay enlaces rotos, 1 si los hay.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Solo enlaces a archivos locales: los remotos no se pueden comprobar.
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)\)")
REMOTE_PREFIXES = ("http://", "https://", "mailto:")


def markdown_files() -> list[pathlib.Path]:
    """Markdown de la raíz y de ``docs/``."""
    return sorted(REPO.glob("*.md")) + sorted((REPO / "docs").glob("*.md"))


def main() -> int:
    docs = markdown_files()
    missing: list[str] = []
    checked = 0
    for doc in docs:
        for target in LINK_RE.findall(doc.read_text(encoding="utf-8")):
            if target.startswith(REMOTE_PREFIXES):
                continue
            checked += 1
            resolved = (doc.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{doc.relative_to(REPO)}: {target}")

    if missing:
        print("ERROR: enlaces rotos en la documentacion:")
        for item in missing:
            print("  -", item)
        return 1
    print(f"OK: {len(docs)} documentos, {checked} enlaces locales, "
          f"ninguno roto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
