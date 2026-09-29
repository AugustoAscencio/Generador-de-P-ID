# SKILL — Generador de planos QElectroTech

> **Skill para agentes de IA.** Versión nativa para opencode (autodescubierta por
> el agente) en: `.opencode/skill/qet-generator/SKILL.md`. Este archivo es la
> copia legible del repositorio.

## Cuándo usar esta skill

- El usuario pide **crear, modificar o regenerar** diagramas/esquemas/planos eléctricos.
- El usuario menciona **QElectroTech, .qet, folios, planos D-0XX** o el proyecto FV 588.
- El usuario entrega una especificación técnica (JSON, MD, tablas) y quiere verla como planos.
- El usuario quiere convertir especificaciones en documentación editable (y luego PDF).

## Reglas de oro (NO negociables)

1. **Nunca inventes el formato .qet.** Todo está documentado con evidencia real en
   `qet_generator/docs/QET_FORMAT_NOTES.md` (leer antes de tocar XML). Ante cualquier
   duda del formato: analiza archivos reales con `qet_generator/tools/inspect_qet.py`
   y `deep_qet.py` sobre `C:\Program Files\QElectroTech\examples\*.qet` o sobre
   cualquier .qet guardado por el usuario. Nunca supongas etiquetas/atributos.
2. **La ingeniería no la decides tú**: los valores técnicos provienen de las fuentes
   (`fuentes/01_…md`, `fuentes/02_…md`) o del requisito explícito del usuario. Lo no
   confirmado se marca **"PENDIENTE DE VERIFICACIÓN"** en los planos, nunca se inventa.
3. **Símbolos reales de biblioteca**: usa los `.elmt` de `C:\Program Files\QElectroTech\elements\`
   vía `templates/symbol_catalog.json`. Antes de usar uno NUEVO, lee su geometría
   (terminales/posiciones) — no la asumas.
4. **Valida antes de generar**: el generador lo hace solo; si hay errores, corrígelos
   en el modelo, no en el XML.
5. **No dibujes N veces lo repetitivo**: usa plantillas paramétricas
   (`generator/builders.py`, `generator/sheets.py`). Filosofía: MÓDULO TIPO × N.

## Inicio rápido (workflow estándar)

```bash
cd qet_generator

# 0) Leer estado y reglas del proyecto
#    (AGENTS.md en la raíz del repositorio)

# 1) ¿Proyecto FV 588? Regenerar desde plantillas:
python tools/build_sheets.py                       # hojas → examples/proyecto_fv_588.json
python main.py examples/proyecto_fv_588.json -o output/Proyecto_FV_588_Modulos.qet

# 2) ¿Proyecto nuevo desde JSON propio del usuario?
python main.py ruta/spec.json [-o salida.qet]      # validación + generación

# 3) Siempre: tests tras cualquier cambio
python -m unittest discover -s tests               # deben pasar 55/55

# 4) Convertir documentación MD a Word si se pide
python tools/md_to_docx.py entrada.md salida.docx "Encabezado"
```

El .qet generado se abre en QElectroTech con doble clic (o Archivo → Abrir).
La verificación visual final la hace el usuario; el agente verifica estructura con
`tools/inspect_qet.py` y los tests.

## Formato del JSON (multi-folio)

```json
{
  "project":  { "title": "...", "author": "..." },
  "diagrams": [
    { "title": "D-0XX — ...", "order": 1,
      "elements":    [ { "id": "X1", "type": "pv_cell", "x": 60, "y": 150,
                         "label": "PV-01", "info": {"designation": "..."} } ],
      "connections": [ { "from": "X1", "from_terminal": 2, "to": "X2", "to_terminal": 0 } ],
      "texts":       [ { "x": 60, "y": 60, "text": "NOTA", "size": 9 } ],
      "shapes":      [ { "x1": 60, "y1": 90, "x2": 300, "y2": 144, "fill": "#e8f0f8" } ] }
  ]
}
```

Claves: `type` = clave de `templates/symbol_catalog.json` (14 símbolos disponibles);
`from_terminal`/`to_terminal` = índice de terminal del `.elmt` (orden de documento);
`info` = metadatos BOM (designation, manufacturer, quantity…). Área útil del folio:
1020×640 px; textos/elementos con y < 560 para no tapar el cartucho.

## Añadir un símbolo nuevo

1. Localiza el `.elmt` en `C:\Program Files\QElectroTech\elements\` y LEE su XML
   (terminales: posiciones relativas al hotspot, orientación n/e/s/w, UUID).
2. Agrega la entrada a `templates/symbol_catalog.json` (ruta relativa + prefijo).
3. Usa sus índices de terminal en las conexiones.

## Mapa del repositorio

| Ruta | Contenido |
|---|---|
| `qet_generator/` | La herramienta (generador + tests + tools + docs) |
| `entregables/` | Caso FV 588: .qet de 18 planos + memoria técnica (MD/Word) |
| `fuentes/` | Documentación técnica fuente (Doc1/Doc2) |
| `evidencia/` | Round-trip con QET 0.100.0 + proyectos de referencia |
| `AGENTS.md` | Reglas, estado actual y hoja de ruta del proyecto |
| `qet_generator/docs/` | Formato .qet, arquitectura, entorno, inventario de ingeniería |

## Qué NO hacer

- ❌ No escribas XML del .qet a mano sin evidencia (usa el generador).
- ❌ No edites los `.qet` con editor de texto para "arreglarlos" — regenera.
- ❌ No resuelvas silenciosamente discrepancias de ingeniería — regístralas.
- ❌ No instales dependencias: el generador usa solo la biblioteca estándar.
- ❌ No crees símbolos personalizados sin aprobación (primero biblioteca real).
- ❌ No sobrescribas `evidencia/roundtrip/` — es la prueba del formato.
