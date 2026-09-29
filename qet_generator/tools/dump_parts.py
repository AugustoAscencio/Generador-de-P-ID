#!/usr/bin/env python3
"""dump_parts.py — Vuelca partes concretas de un .qet (gaps de evidencia)."""
import sys
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

root = ET.parse(sys.argv[1]).getroot()
d = root.find("diagram")

print("=== diagram/properties ===")
p = d.find("properties")
print(ET.tostring(p, encoding="unicode") if p is not None else "(no existe)")

print("=== diagram/inputs: primeros 3 <input> ===")
inputs = d.find("inputs")
if inputs is not None:
    n = 0
    for inp in inputs:
        if n >= 3:
            break
        print(ET.tostring(inp, encoding="unicode")[:600])
        n += 1
    if n == 0:
        print("(vacío)")

print("=== diagram/shapes (primeros 300 chars) ===")
shapes = d.find("shapes")
print(ET.tostring(shapes, encoding="unicode")[:300] if shapes is not None else "(no existe)")

print("=== diagram/elements: es wrapper, primer hijo ===")
els = d.find("elements")
if els is not None:
    first = els.find("element")
    print("attrs del primer element:", dict(first.attrib) if first is not None else "(vacío)")

print("=== diagram/conductors: es wrapper, primer hijo ===")
cs = d.find("conductors")
if cs is not None:
    first = cs.find("conductor")
    print("attrs del primer conductor:", dict(first.attrib) if first is not None else "(vacío)")
