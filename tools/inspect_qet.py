#!/usr/bin/env python3
"""
inspect_qet.py — Inspector estructural de proyectos QElectroTech (.qet).

Herramienta de EVIDENCIA: imprime la estructura real del XML tal como la
escribe QElectroTech, para que el generador nunca invente el formato.

Uso:
    python inspect_qet.py <archivo.qet>            -> resumen (raiz, censo, atributos, tipos)
    python inspect_qet.py <archivo.qet> --all      -> ademas, volcado completo de la primera
                                                     ocurrencia de cada etiqueta
    python inspect_qet.py <archivo.qet> --full TAG  -> volcado completo de la primera
                                                     ocurrencia de TAG (repetible)
"""
import argparse
import sys
import xml.etree.ElementTree as ET
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MAX_DUMP_LINES = 100


def indent(elem, level=0):
    """Pretty-printer oficial de ElementTree (docs de Python)."""
    i = "\n" + level * "  "
    if len(elem):
        if not (elem.text or "").strip():
            elem.text = i + "  "
        if not (elem.tail or "").strip():
            elem.tail = i
        for child in elem:
            indent(child, level + 1)
        if not (child.tail or "").strip():
            child.tail = i
    else:
        if level and (not (elem.tail or "").strip()):
            elem.tail = i
    return elem


def dump(el):
    """Serializa un subtree con sangria, truncado a MAX_DUMP_LINES."""
    clone = indent(el)
    text = ET.tostring(clone, encoding="unicode")
    lines = text.splitlines()
    if len(lines) > MAX_DUMP_LINES:
        lines = lines[:MAX_DUMP_LINES] + ["    ... (TRUNCADO)"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Inspector de .qet basado en evidencia")
    ap.add_argument("file", help="Archivo .qet a inspeccionar")
    ap.add_argument("--full", action="append", default=[],
                    help="Volcar la primera ocurrencia completa de TAG (repetible)")
    ap.add_argument("--all", action="store_true",
                    help="Volcar la primera ocurrencia de TODAS las etiquetas (excepto la raiz)")
    args = ap.parse_args()

    try:
        tree = ET.parse(args.file)
    except ET.ParseError as e:
        print(f"XML MAL FORMADO: {e}", file=sys.stderr)
        sys.exit(2)
    root = tree.getroot()

    print(f"=== ARCHIVO: {args.file}")
    print(f"=== RAIZ: <{root.tag}> {root.attrib}")
    print()

    # 1) Censo de etiquetas
    counts = Counter(e.tag for e in root.iter())
    print("=== CENSO DE ETIQUETAS (total %d nodos) ===" % sum(counts.values()))
    for tag, n in counts.most_common():
        print(f"  {tag}: {n}")
    print()

    # 2) Union de atributos por etiqueta (primer valor visto como ejemplo)
    first = {}
    attr_union = {}
    for e in root.iter():
        if e.tag not in first:
            first[e.tag] = e
            attr_union[e.tag] = {}
        for k, v in e.attrib.items():
            attr_union[e.tag].setdefault(k, v)
    print("=== ATRIBUTOS POR ETIQUETA (valor de la 1a ocurrencia como ejemplo) ===")
    for tag in counts:
        print(f"  <{tag}> {attr_union[tag]}")
    print()

    # 3) Hijos directos de la raiz
    print("=== HIJOS DIRECTOS DE <project> (orden real) ===")
    for ch in root:
        print(f"  <{ch.tag}> attrs={dict(ch.attrib)}")
    print()

    # 4) Diagramas
    diagrams = root.findall(".//diagram")
    print(f"=== DIAGRAMAS: {len(diagrams)} ===")
    for d in diagrams[:5]:
        print(f"  <diagram> {d.attrib}")
    print()

    # 5) Referencias a elementos (type=...) -> rutas de .elmt usadas realmente
    types = Counter()
    for el in root.iter("element"):
        types[el.get("type", "?")] += 1
    print(f"=== ELEMENTOS <element type=...> : {len(list(root.iter('element')))} total, {len(types)} tipos distintos ===")
    for t, n in types.most_common(60):
        print(f"  {t}  x{n}")
    print()

    # 6) Conductores
    conductors = list(root.iter("conductor"))
    print(f"=== CONDUCTORES: {len(conductors)} ===")
    for c in conductors[:3]:
        print(f"  {dict(c.attrib)}")
    print()

    # 7) Volcados completos
    targets = list(args.full)
    if args.all:
        targets.extend(counts.keys())
    seen_targets = set()
    for tag in targets:
        if tag in seen_targets:
            continue
        seen_targets.add(tag)
        if tag not in first:
            print(f"=== <{tag}> NO EXISTE EN ESTE ARCHIVO ===")
            continue
        if first[tag] is root:
            print(f"=== <{tag}> es la RAIZ; se omite el volcado completo ===")
            continue
        print(f"=== PRIMERA OCURRENCIA COMPLETA DE <{tag}> ===")
        print(dump(first[tag]))


if __name__ == "__main__":
    main()
