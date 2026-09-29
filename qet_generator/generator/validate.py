"""validate.py — Validaciones del modelo ANTES de generar (FASE 12).

Devuelve una lista de errores; si hay alguno, no se genera el .qet.
Reglas:
  - Los IDs de elemento son únicos en TODO el proyecto (aunque los folios
    reinicien los IDs de terminal — evidencia §11 — los IDs lógicos del JSON
    no se repiten: serán la base de referencias entre folios en el futuro).
  - Las conexiones se resuelven dentro del folio donde están definidas.
"""

from __future__ import annotations

from .model import KNOWN_INFO_KEYS, ProjectSpec


def validate_spec(spec: ProjectSpec, catalog) -> list[str]:
    errors: list[str] = []
    global_ids: set[str] = set()
    by_folio: list[dict[str, object]] = []

    # --- elementos (recolección + validación individual) ---
    for folio in spec.folios:
        by_id: dict = {}
        for i, el in enumerate(folio.elements):
            ctx = f"folio '{folio.title or folio.order}' elements[{i}] (id={el.id!r})"
            if not el.id:
                errors.append(f"{ctx}: id vacío")
                continue
            if el.id in global_ids:
                errors.append(f"ID duplicado en el proyecto: {el.id!r}")
            global_ids.add(el.id)
            by_id[el.id] = el

            if not catalog.has(el.type):
                errors.append(f"{ctx}: tipo no registrado en el catálogo: {el.type!r}")
                continue
            symbol = catalog.get(el.type)
            if el.orientation not in (0, 1, 2, 3):
                errors.append(f"{ctx}: orientation debe ser 0-3, llegó {el.orientation}")
            if el.x < 0 or el.y < 0:
                errors.append(f"{ctx}: posición negativa ({el.x}, {el.y})")
            for key in el.info:
                if key not in KNOWN_INFO_KEYS:
                    errors.append(
                        f"{ctx}: clave de info no reconocida: {key!r} "
                        f"(válidas: {', '.join(sorted(KNOWN_INFO_KEYS))})")
            if len(symbol.terminals) == 0 and any(
                    c for c in folio.connections if el.id in (c.from_id, c.to_id)):
                errors.append(f"{ctx}: el símbolo no tiene terminales conectables")
        by_folio.append(by_id)

    # --- conexiones (resueltas dentro de su folio) ---
    for folio, by_id in zip(spec.folios, by_folio):
        for i, cn in enumerate(folio.connections):
            ctx = f"folio '{folio.title or folio.order}' connections[{i}] {cn.key()}"
            if cn.from_id not in by_id:
                errors.append(f"{ctx}: 'from' hace referencia a un elemento inexistente en este folio")
                continue
            if cn.to_id not in by_id:
                errors.append(f"{ctx}: 'to' hace referencia a un elemento inexistente en este folio")
                continue
            if cn.from_id == cn.to_id:
                errors.append(f"{ctx}: un conductor no puede conectar un elemento consigo mismo")
            src, dst = by_id[cn.from_id], by_id[cn.to_id]
            for end, elem, tname in ((cn.from_terminal, src, "from_terminal"),
                                     (cn.to_terminal, dst, "to_terminal")):
                if catalog.has(elem.type):
                    n = len(catalog.get(elem.type).terminals)
                    if not (0 <= end < n):
                        errors.append(
                            f"{ctx}: {tname}={end} fuera de rango "
                            f"({elem.type!r} tiene {n} terminales: 0..{n - 1})")

    # --- textos ---
    for folio in spec.folios:
        for i, tx in enumerate(folio.texts):
            if not str(tx.text).strip():
                errors.append(f"folio '{folio.title or folio.order}' texts[{i}]: texto vacío")
            if not (5 <= tx.size <= 24):
                errors.append(f"folio '{folio.title or folio.order}' texts[{i}]: "
                              f"size debe estar entre 5 y 24 pt, llegó {tx.size}")

    # --- shapes (bloques) ---
    for folio in spec.folios:
        for i, sh in enumerate(folio.shapes):
            ctx = f"folio '{folio.title or folio.order}' shapes[{i}]"
            if sh.x2 <= sh.x1 or sh.y2 <= sh.y1:
                errors.append(f"{ctx}: coordenadas invertidas "
                              f"({sh.x1},{sh.y1})-({sh.x2},{sh.y2})")
            if sh.x1 < 0 or sh.y1 < 0 or sh.x2 > 1020 or sh.y2 > 660:
                errors.append(f"{ctx}: fuera del área del folio 1020×660")
            if not (0.5 <= sh.width <= 10):
                errors.append(f"{ctx}: width de línea irrazonable: {sh.width}")

    # --- folios ---
    orders = [f.order if f.order is not None else i + 1
              for i, f in enumerate(spec.folios)]
    if len(orders) != len(set(orders)):
        errors.append(f"orders de folio duplicados: {sorted(orders)}")
    for folio in spec.folios:
        if folio.date is not None and not (len(folio.date) == 8 and folio.date.isdigit()):
            errors.append(f"folio '{folio.title or folio.order}': date debe ser AAAAMMDD, "
                          f"llegó: {folio.date!r}")

    return errors
