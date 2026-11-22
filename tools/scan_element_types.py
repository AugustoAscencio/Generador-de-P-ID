#!/usr/bin/env python3
"""
scan_element_types.py — Escanea todos los .qet de una carpeta y clasifica
los valores de type= de <element>: embebidos (embed://), referencias a
biblioteca (otro formato) o ausentes.

Responde: ¿cómo referencia un proyecto a elementos de la biblioteca instalada
sin embeberlos? (FASE 7)
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter

folder = sys.argv[1] if len(sys.argv) > 1 else "."
pattern = os.path.join(folder, "*.qet")

for f in sorted(glob.glob(pattern)):
    try:
        root = ET.parse(f).getroot()
    except ET.ParseError as e:
        print(f"{os.path.basename(f)}: XML MAL FORMADO ({e})")
        continue
    styles = Counter()
    non_embed = set()
    for el in root.iter("element"):
        t = el.get("type")
        if t is None:
            styles["sin type"] += 1
        elif t.startswith("embed://"):
            styles["embed://"] += 1
        else:
            styles["otro"] += 1
            non_embed.add(t)
    print(f"{os.path.basename(f)}: {dict(styles)}")
    for t in sorted(non_embed):
        print(f"    NO-embed -> {t}")
