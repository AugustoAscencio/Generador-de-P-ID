# Generador de proyectos QElectroTech (.qet)

Convierte una especificación eléctrica estructurada (JSON) en un **proyecto real de
QElectroTech**, editable, con elementos de la biblioteca instalada, conductores,
textos, multi-folio y metadatos BOM.

```
JSON  →  python main.py  →  .qet  →  QElectroTech (editable)
```

Construido **por ingeniería inversa del formato real** producido por QElectroTech
0.100.0 (ver `docs/QET_FORMAT_NOTES.md`). Nada del formato fue inventado.

## Requisitos

- Python 3.10+ (probado con 3.13.7, solo biblioteca estándar)
- QElectroTech 0.100.0 instalado en `C:\Program Files\QElectroTech`
  (la biblioteca de símbolos se lee de ahí)

## Uso rápido

```bash
cd qet_generator
python main.py examples/basic_circuit.json      # mono-folio
python main.py examples/pv_8_panels.json        # string FV 8 paneles + BOM
python main.py examples/module_demo.json        # MÓDULO TIPO: 2 folios
```

Salida: `output/<nombre>.qet` (o usa `-o ruta/mi.qet`).
Ábrelo en QElectroTech: doble clic, o **Archivo → Abrir**.

## Formato del JSON — multi-folio (actual)

```json
{
  "project":  { "title": "...", "author": "..." },
  "diagrams": [
    {
      "title": "Folio 1 - String FV",
      "order": 1,
      "elements": [
        { "id": "M001-PV1", "type": "pv_cell", "x": 60, "y": 150,
          "label": "PV1",
          "info": { "designation": "Panel FV 650Wp (SUPUESTO)", "quantity": "1" } }
      ],
      "connections": [
        { "from": "M001-PV1", "from_terminal": 2,
          "to": "M001-PV2",   "to_terminal": 0 }
      ],
      "texts": [ { "x": 60, "y": 60, "text": "Nota del folio" } ]
    },
    { "title": "Folio 2 - Auxiliar 24VDC", "order": 2, "...": "..." }
  ]
}
```

- `id` = identificador interno, **único en todo el proyecto** (recomendado
  prefijarlo por módulo: `M001-PV3`).
- `label` = etiqueta visible en el esquema (por defecto, el id).
- `type` = clave del catálogo `templates/symbol_catalog.json` → `.elmt` real.
- `from_terminal`/`to_terminal` = índice de terminal del símbolo (0, 1, 2…)
  según el orden en que aparece en su `.elmt`.
- `info` = metadatos BOM (claves confirmadas del formato: `designation`,
  `description`, `manufacturer`, `manufacturer_reference`, `quantity`, `unity`,
  `supplier`, `location`, `comment`, `formula`, `plant`,
  `machine_manufacturer_reference`).
- Coordenadas: área útil del folio ≈ 1020 × 640 px.

**Formato plano antiguo** (`diagram` + `elements`/`connections`/`texts` a nivel
raíz) sigue soportado por compatibilidad.

## Plantillas paramétricas (MÓDULO TIPO × N)

```bash
python tools/build_module_demo.py M001 8    # → examples/module_demo.json
python main.py examples/module_demo.json     # → 2 folios
```

API en `generator/builders.py`:

```python
from generator.builders import create_pv_string, build_module_folios
elements, connections = create_pv_string(count=8, module="M001")
folios = build_module_folios(module="M001", panel_count=8)
```

⚠ Los valores técnicos de las plantillas son **SUPUESTOS estructurales**,
pendientes de la especificación técnica maestra del cliente (ver `AGENTS.md`).

## Símbolos disponibles (catálogo)

| Clave | Símbolo real de la biblioteca QET |
|---|---|
| `ac_source` | Fuente de tensión (nuevo) |
| `circuit_breaker_1p` | Disyuntor térmico magnético en polo P |
| `motor_1p` | Motor monofásico |
| `pv_cell` | Celda fotovoltaica (panel FV) |
| `lamp` | Lámpara |
| `dc_terminal` | Punto de unión / borne final |

Para añadir símbolos: localiza el `.elmt` en `C:\Program Files\QElectroTech\elements\`
y agrégalo a `templates/symbol_catalog.json` (ruta relativa + prefijo).

## Tests

```bash
python -m unittest discover -s tests    # 42 tests
```

## Estructura

- `generator/model.py` — lectura del JSON (mono y multi-folio)
- `generator/validate.py` — validaciones previas
- `generator/project.py` — ensambla `<project>` (folios + colección) y exporta
- `generator/diagram.py` — folios (`<diagram>`)
- `generator/elements.py` — catálogo + elementos (terminales/etiquetas/BOM)
- `generator/conductors.py` — conductores
- `generator/text.py` — textos independientes
- `generator/builders.py` — plantillas paramétricas (módulo tipo)
- `tools/` — utilidades de análisis del formato real

## Reglas del proyecto (FASE 15)

La fuente de verdad es la **especificación técnica del proyecto**, no el código:
Documentación del cliente → Especificación técnica maestra → JSON → Generador → QET.
El generador nunca decide ingeniería; solo representa.
