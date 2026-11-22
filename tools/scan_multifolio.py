#!/usr/bin/env python3
"""scan_multifolio.py — Evidencia multi-folio: orden, IDs de terminal por folio.

Responde: ¿los IDs de terminal son globales por FOLIO o por PROYECTO?
"""

import sys
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    diagrams = root.findall("diagram")
    name = path.replace("\\", "/").split("/")[-1]
    print(f"=== {name}: {len(diagrams)} folios ===")
    all_ids = []
    for d in diagrams:
        ids = [int(t.get("id")) for t in d.iter("terminal")
               if t.get("id") is not None]
        all_ids.extend(ids)
        dup = len(ids) - len(set(ids))
        rng = f"{min(ids)}..{max(ids)}" if ids else "-"
        print(f"  folio order={d.get('order')}: con-id={len(ids):3d} "
              f"rango={rng:9s} dup-internas={dup}")
    dup_total = len(all_ids) - len(set(all_ids))
    print(f"  -> IDs repetados ENTRE folios: {dup_total} "
          f"({'GLOBALES POR PROYECTO' if dup_total == 0 else 'GLOBALES POR FOLIO'})")
    print()
