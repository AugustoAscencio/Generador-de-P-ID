# ARQUITECTURA.md — Arquitectura del generador

## Principio rector

**Todo lo que el generador escribe sobre el formato .qet está basado en evidencia**
obtenida de archivos reales creados por QElectroTech 0.100.0 (ver
`QET_FORMAT_NOTES.md`). No hay etiquetas inventadas. Lo no confirmado está marcado.

## Capas

```
main.py (CLI)
   │
   ├── generator/model.py      LECTURA: JSON → ProjectSpec (dataclasses)
   │        No conoce nada de XML. Solo valida tipos básicos y estructura.
   │
   ├── generator/validate.py   VALIDACIÓN (FASE 12): modelo + catálogo
   │        Se ejecuta SIEMPRE antes de generar. Si falla, no se escribe nada.
   │        Detecta: IDs duplicados, conexiones a elementos inexistentes,
   │        tipos no registrados, terminales fuera de rango, textos vacíos,
   │        fechas mal formateadas.
   │
   ├── generator/elements.py   SÍMBOLOS: SymbolCatalog
   │        Clave lógica (ej. "pv_cell") → archivo .elmt REAL de la
   │        biblioteca instalada. Extrae: definición completa (para embeber),
   │        terminales (uuid, posición, orientación) y posición de etiqueta.
   │        También construye los <element> colocados (uuid de instancia,
   │        terminales con uuid de definición, elementInformation/label,
   │        dynamic_texts).
   │
   ├── generator/conductors.py CONDUCTORES: <conductor> estilo UUID moderno
   │        element1/element2 + terminal1/terminal2. QET recalcula la ruta.
   │
   ├── generator/text.py       TEXTOS: <input> independiente con HTML de Qt.
   │
   ├── generator/diagram.py    FOLIO: <diagram> (wrappers elements/conductors/
   │        inputs/shapes, ids de terminales GLOBALES por folio).
   │
   └── generator/project.py    ENSAMBLADO: <project> (properties, newdiagrams,
             diagram, collection embebida) + exportación a .qet
             (UTF-8, sin BOM, sin declaración — igual que QET).
```

## Decisiones de diseño (FASE 11)

1. **Embebido de símbolos**: cada símbolo usado se copia (una vez) del disco al
   `<collection>` del proyecto y se referencia con `embed://import/<ruta>`.
   Es el único mecanismo con evidencia total en los proyectos reales, y hace el
   proyecto portable a otros equipos.
2. **Identidad de terminales = uuid de la definición .elmt** (evidencia §3 de
   QET_FORMAT_NOTES): permite a QET restaurar conductores con precisión.
3. **Separación estricta modelo/XML**: `model.py` no genera XML; `project.py`
   no lee JSON. Extensible a: multi-folio (hecho), plantillas de módulo,
   nomenclatura.
4. **Multi-folio (evidencia §11)**: varios `<diagram order=1..N>` como hermanos;
   los IDs de terminal son **globales por folio** (reinician en 0, como los
   archivos reales); una sola `<collection>` compartida; los IDs lógicos del
   JSON son únicos en todo el proyecto (base futura de xrefs).
5. **Plantillas paramétricas** (`builders.py`): `create_pv_string(count=N)`,
   `create_dc_protection()`, `create_aux_24vdc()`, `build_module_folios()` →
   emiten `ElementSpec`/`ConnectionSpec`/`FolioSpec` sin tocar los módulos XML.
   Es la implementación de la filosofía **MÓDULO TIPO × 588**.
6. **Metadatos BOM**: `ElementSpec.info` → `elementInformation` con las claves
   confirmadas del formato (designation, manufacturer, quantity…) para la
   nomenclatura futura.
7. **Compatibilidad (FASE 16)**: el formato plano antiguo sigue cargando
   (`load_spec` lo envuelve en un único folio).

## Límites actuales (conscientes)

- Conexiones solo dentro de cada folio (sin conductores entre folios — QET
  usa report/xref para eso; pendiente de análisis).
- `version` de diagrama escrita como `0.100.0` (confirmada por round-trip).
- Sin xrefs/reports entre folios todavía (siguiente paso para 588 módulos).
- Los valores técnicos de `builders.py` son SUPUESTOS hasta que exista el
  documento técnico maestro (regla nº3 de AGENTS.md).

## Herramientas de evidencia (`tools/`)

- `inspect_qet.py <f.qet>` — censo de etiquetas/atributos/tipos usados
- `deep_qet.py <f.qet>` — dumps completos y correlaciones de uuids
- `dump_parts.py <f.qet>` — partes concretas (properties, inputs, shapes)
- `scan_element_types.py <carpeta>` — cómo referencian elementos los .qet
- `scan_multifolio.py <f.qet…>` — multi-folio: orders e ids de terminal por folio
- `build_module_demo.py [MODULO] [PANELES]` — genera el JSON del módulo tipo

Estas herramientas son parte del sistema: ante cualquier duda del formato,
se vuelve a la fuente real, nunca se supone.
