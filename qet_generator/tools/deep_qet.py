#!/usr/bin/env python3
"""
deep_qet.py — Análisis profundo de un proyecto .qet para extraer el formato EXACTO.

Responde preguntas concretas que el generador necesita saber:
  1. Orden de hijos de <diagram>
  2. Dump completo de un <element> con type
  3. Dump completo de un <element> sin type
  4. Dump de conductores estilo UUID y estilo numérico
  5. Estructura de la <collection> embebida
  6. Correlación de uuids elemento/definición/terminal
  7. Dónde se guarda el texto de la etiqueta
  8. Estadística de atributos (obligatorios vs opcionales)
"""
import argparse
import sys
import xml.etree.ElementTree as ET
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def indent(elem, level=0):
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


def dump(el, max_lines=120):
    text = ET.tostring(indent(el), encoding="unicode")
    lines = text.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["    ... (TRUNCADO)"]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    args = ap.parse_args()
    root = ET.parse(args.file).getroot()

    print("### 1. HIJOS DIRECTOS DE <diagram> (primer diagrama, en orden)")
    d = root.find("diagram")
    if d is not None:
        seq = [c.tag for c in d]
        print("  secuencia:", seq[:40])
        print("  conteo:", dict(Counter(seq)))

    print("\n### 2. PRIMER <element> CON type (dump completo)")
    for el in root.iter("element"):
        if el.get("type"):
            print(dump(el))
            break

    print("\n### 3. PRIMER <element> SIN type (dump completo)")
    for el in root.iter("element"):
        if not el.get("type"):
            print(dump(el))
            break

    print("\n### 4a. PRIMER <conductor> terminal1=UUID (dump completo)")
    for c in root.iter("conductor"):
        if (c.get("terminal1") or "").startswith("{"):
            print(dump(c))
            break

    print("\n### 4b. PRIMER <conductor> terminal1=NUMÉRICO (dump completo)")
    for c in root.iter("conductor"):
        if c.get("terminal1") and not c.get("terminal1", "").startswith("{"):
            print(dump(c))
            break

    print("\n### 5. <collection> embebida")
    coll = root.find("collection")
    if coll is not None:
        for cat in coll.findall("category"):
            defs = cat.findall("definition")
            print(f"  <category name={cat.get('name')!r}> con {len(defs)} <definition>")
            for df in defs[:4]:
                print("    definition attrs:", dict(df.attrib))
        df0 = coll.find(".//definition")
        if df0 is not None:
            print("\n  Primera <definition> de la colección (dump, truncado):")
            print(dump(df0, 60))
    else:
        print("  (no hay colección embebida)")

    print("\n### 6. CORRELACIÓN DE UUIDs")
    def_uuids = set()
    for u in root.iter("uuid"):
        def_uuids.add(u.get("uuid"))
    elem_uuids = [e.get("uuid") for e in root.iter("element")]
    intersect = set(elem_uuids) & def_uuids
    print(f"  uuids de <element>: {len(elem_uuids)} | uuids en <definition>/<uuid>: {len(def_uuids)}")
    print(f"  intersección (elemento apunta a definición?): {len(intersect)}")
    if intersect:
        print("  ejemplos:", list(intersect)[:3])

    print("\n### 7. TEXTO DE ETIQUETAS (elementInformation con contenido)")
    n_text = 0
    for el in root.iter("elementInformation"):
        if (el.text or "").strip():
            n_text += 1
            if n_text <= 5:
                print(f"  {el.attrib} -> texto={el.text!r}")
    print(f"  total elementInformation con texto: {n_text}")

    print("\n### 8. ESTADÍSTICA DE ATRIBUTOS (presencia en % de casos)")
    def attr_stats(tag):
        elems = list(root.iter(tag))
        if not elems:
            print(f"  <{tag}>: no hay")
            return
        keys = Counter()
        for e in elems:
            for k in e.attrib:
                keys[k] += 1
        total = len(elems)
        print(f"  <{tag}> n={total}:")
        for k, v in keys.most_common():
            print(f"    {k}: presente en {v}/{total}")

    attr_stats("element")
    attr_stats("conductor")
    attr_stats("terminal")

    print("\n### 9. <inputs> a nivel de diagrama (textos independientes)")
    if d is not None:
        direct = d.findall("input")
        print(f"  <input> hijos directos de <diagram>: {len(direct)}")
        for inp in direct[:2]:
            print("   ", inp.attrib, "-> texto:", repr((inp.text or "")[:60]))

    print("\n### 10. <properties> del proyecto (dump completo)")
    props = root.find("properties")
    if props is not None:
        print(dump(props, 40))

    print("\n### 11. ÁRBOL de la <collection> embebida")
    coll = root.find("collection")
    if coll is not None:
        def tree(node, depth=0):
            for child in node:
                if child.tag == "category":
                    print("  " * (depth + 1) + f"<category name={child.get('name')!r}>")
                    tree(child, depth + 1)
                elif child.tag == "element":
                    print("  " * (depth + 1) + f"<element name={child.get('name')!r}>"
                          + (" (con <definition>)" if child.find("definition") is not None else ""))
        tree(coll)

    print("\n### 12. TERMINALES: ¿IDs locales o globales?")
    ids = [t.get("id") for t in root.iter("terminal") if t.get("id") is not None]
    ints = [int(i) for i in ids]
    print(f"  terminales con id: {len(ints)} | únicos: {len(set(ints))} | max: {max(ints) if ints else '-'}")
    if ints:
        print(f"  duplicados (locales): {len(ints) - len(set(ints))}")

    print("\n### 13. CAZA DE ETIQUETAS: ¿dónde está el texto del label?")
    # a) elementInformation name=label con texto
    for el in root.iter("elementInformation"):
        if el.get("name") == "label" and (el.text or "").strip():
            print(f"  elementInformation name=label CON TEXTO: {el.text!r}")
            break
    else:
        print("  elementInformation name=label: ninguno con texto")
    # b) <input tagg="label"> DENTRO de un <element> (estilo antiguo)
    found_legacy = False
    for el in root.iter("element"):
        if el.find("terminals") is None and el.find("definition") is None:
            continue  # saltar wrappers de la colección embebida
        for inp in el.iter("input"):
            if inp.get("tagg") == "label" and (inp.text or "").strip():
                print(f"  <input tagg=label> DENTRO de element: {inp.attrib} texto={inp.text!r}")
                found_legacy = True
                break
        if found_legacy:
            break
    if not found_legacy:
        print("  <input tagg=label> dentro de element: ninguno con texto")
    # c) enumerar qué elementInformation name= existen
    names = Counter(e.get("name") for e in root.iter("elementInformation"))
    print("  nombres de elementInformation:", dict(names))


if __name__ == "__main__":
    main()
