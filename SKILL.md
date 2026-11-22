# SKILL — qetgen: generador de planos QElectroTech

> **Skill para agentes de IA.** La versión nativa para opencode (autodescubierta
> por el agente) está en `.opencode/skill/qet-generator/SKILL.md`. Este archivo
> es la copia legible del repositorio.

## Cuándo usar esta skill

- El usuario pide **crear, modificar o regenerar** diagramas/esquemas/planos eléctricos.
- El usuario menciona **QElectroTech, .qet, folios, planos D-0XX** o el proyecto FV 588.
- El usuario entrega una especificación técnica (JSON, MD, tablas) y quiere verla como planos.
- El usuario quiere convertir especificaciones en documentación editable (y luego PDF).
- El usuario quiere **revisar la estética** de un plano (solapes, textos desbordados, cableado).

## Reglas de oro (NO negociables)

1. **Nunca inventes el formato .qet.** Todo está documentado con evidencia real en
   `docs/QET_FORMAT_NOTES.md` (leer antes de tocar XML; marca CONFIRMADO vs INFERIDO).
   Ante cualquier duda, analiza archivos reales con `tools/inspect_qet.py` y
   `tools/deep_qet.py` sobre `C:\Program Files\QElectroTech\examples\*.qet` o sobre
   cualquier .qet guardado por el usuario. Nunca supongas etiquetas/atributos.
   *Dato clave:* `<diagram>` **no** guarda `width` (0/129 folios reales): el ancho se
   deriva de `cols × colsize`. `height == rows × rowsize + 20` en 129/129.
2. **La ingeniería no la decides tú** (jerarquía: documentación del cliente →
   especificación técnica maestra → JSON → generador → QET). Los valores técnicos
   vienen de `fuentes/01_…md`, `fuentes/02_…md` o del requisito explícito del
   usuario. Lo no confirmado se marca **"PENDIENTE DE VERIFICACIÓN"**, nunca se inventa.
3. **Símbolos reales de biblioteca:** usa los `.elmt` de
   `C:\Program Files\QElectroTech\elements\` vía `resources/symbol_catalog.json`
   (14 tipos). Antes de usar uno NUEVO, lee su geometría (terminales/posiciones) —
   no la asumas.
4. **Valida antes de generar:** el generador lo hace solo; si hay errores, corrígelos
   en el modelo, no en el XML.
5. **No dibujes N veces lo repetitivo:** usa las hojas paramétricas de
   `src/qetgen/sheets/fv588/`. Filosofía: MÓDULO TIPO × N.
6. **Respeta `locked: true`:** es la decisión del ingeniero sobre la posición de un
   elemento; el motor no lo mueve.

## Inicio rápido (workflow estándar)

```bash
# 0) Leer estado y reglas del workspace
#    (AGENTS.md en la raíz del repositorio)

# 1) ¿Entorno correcto? (Python, Pydantic, PyYAML, QET, catálogo, config)
python -m qetgen.cli doctor

# 2) ¿Proyecto FV 588? Regenerar desde las hojas paramétricas:
python -m qetgen.cli fv588

# 3) ¿Proyecto nuevo desde JSON propio del usuario?
python -m qetgen.cli build ruta/spec.json -o salida.qet

# 4) ¿Revisar la estética? (código de salida 1 si hay defectos)
python -m qetgen.cli layout ruta/spec.json --check

# 5) ¿Reorganizar un plano? (simulación: no escribe nada)
python -m qetgen.cli layout ruta/spec.json --folio 3 --auto-layout
python -m qetgen.cli layout ruta/spec.json --folio 3 --auto-layout --apply -o corregido.json

# 6) Previsualizar en SVG (primitivas reales de cada .elmt)
python -m qetgen.cli layout ruta/spec.json --preview preview/

# 7) Siempre: tests tras cualquier cambio
python -m unittest discover -s tests               # deben pasar 221/221

# 8) Convertir documentación MD a Word si se pide
python tools/md_to_docx.py entrada.md salida.docx "Encabezado"
```

> Si el paquete está instalado (`pip install -e .`), `qetgen` sustituye a
> `python -m qetgen.cli`. En Windows, usa `python -X utf8` si la consola (cp1252)
> protesta con `→` o `—`.

El `.qet` generado se abre en QElectroTech con doble clic (o Archivo → Abrir).
La verificación visual final la hace el usuario; tú verificas estructura con
`tools/inspect_qet.py`, `qetgen layout --check` y los tests.

## Formato del JSON (multi-folio, canónico)

```json
{
  "project":  { "title": "...", "author": "..." },
  "diagrams": [
    { "title": "D-0XX — ...", "order": 1,
      "elements":    [ { "id": "X1", "type": "pv_cell", "x": 60, "y": 150,
                         "label": "PV-01", "locked": false,
                         "info": {"designation": "..."} } ],
      "connections": [ { "from": "X1", "from_terminal": 2, "to": "X2", "to_terminal": 0 } ],
      "texts":       [ { "x": 60, "y": 60, "text": "NOTA", "size": 9 } ],
      "shapes":      [ { "x1": 60, "y1": 90, "x2": 300, "y2": 144, "fill": "#e8f0f8" } ] }
  ]
}
```

Claves: `type` = clave de `resources/symbol_catalog.json` (14 símbolos);
`from_terminal`/`to_terminal` = índice de terminal del `.elmt` (orden de
documento); `locked: true` = el auto-layout no lo mueve; `info` = metadatos BOM
(designation, manufacturer, quantity…). Folio estándar: 1020×640 px útiles, con
la banda del cajetín de 20 px abajo (`height` total 660 px).

## Diagnóstico: qué significa cada código

`qetgen layout --check` y `qetgen doctor` devuelven diagnósticos accionables.

| Severidad | Código | Significa |
|---|---|---|
| error | `SYMBOL_OVERLAP` | dos símbolos se pisan (cajas de tinta que se cruzan) |
| error | `OUT_OF_SHEET` | el contenido se sale del folio (más de `edge_tolerance`, 36 px) |
| warning | `TEXT_OVERLAP` | dos textos se pisan |
| warning | `LABEL_OVERLAP` | una etiqueta choca con otro objeto |
| warning | `ROUTE_CROSSING` / `ROUTE_TOO_CLOSE` | cables que se cruzan o van demasiado juntos |
| info | `BLOCK_CROSSING` / `EMPTY_SHEET` | avisos de composición |

Cada diagnóstico lleva **qué pasa**, **por qué importa** y **qué cambiar**.

## Configuración

Un solo archivo gobierna hoja, rejilla, tipografía, cableado y estilos:
`config/default.yaml` (YAML o JSON). Se carga con `--config`.

```yaml
sheet:
  format: A3_17x8      # presets: A3_17x8, A3_18x9, A3_20x11, A4_11x7,
  margin: 8            #          A4_10x5, A4_15x6, A2_24x11, A1_39x20, A0_42x21
  edge_tolerance: 36   # calibrada con 416 textos reales de QET 0.100.0
layout:
  grid_size: 10
  respect_locked: true # modo híbrido
  clearance: 18        # holgura al reubicar
  route_clearance: 6   # holgura al cablear (distinta, a propósito)
```

Referencia completa de cada clave: `docs/CONFIGURACION.md`.

## Servidor MCP (para integraciones y agentes)

```bash
python -m qetgen.cli serve            # servidor MCP por stdio
python -m qetgen.cli serve --fallback # fuerza el transporte propio (sin SDK)
```

8 herramientas atómicas: `crear_diagrama`, `listar_simbolos`,
`agregar_elemento`, `conectar_elementos`, `ejecutar_auto_layout`,
`validar_estetica`, `obtener_resumen_canvas`, `exportar_archivo`.
Detalle en `docs/MCP.md`; configuración de cliente en `mcp_config_example.json`.

## Añadir un símbolo nuevo

1. Localiza el `.elmt` en `C:\Program Files\QElectroTech\elements\` y LEE su XML
   (terminales: posiciones relativas al hotspot, orientación n/e/s/w, UUID).
2. Agrega la entrada a `resources/symbol_catalog.json` (ruta relativa + prefijo).
3. Usa sus índices de terminal en las conexiones.
4. Verifica con `python -m qetgen.cli symbols` y `qetgen doctor`.

## Mapa del repositorio

| Ruta | Contenido |
|---|---|
| `src/qetgen/` | **La herramienta**: `core/`, `layout/`, `exporters/`, `validation/`, `cli/`, `mcp_server/`, `sheets/` |
| `qet_generator/` | Fachada de compatibilidad de la v0.1 (se elimina en la v2.0) |
| `config/default.yaml` | Configuración central (hoja, rejilla, tipografía, cableado) |
| `resources/symbol_catalog.json` | Símbolos disponibles (14) |
| `examples/` | JSON de los proyectos (`proyecto_fv_588.json`) |
| `entregables/` | Caso FV 588: `.qet` de 18 planos + memoria técnica (MD/Word) |
| `fuentes/` | Documentación técnica fuente (Doc1/Doc2) — fuentes ÚNICAS |
| `evidencia/` | Round-trip con QET 0.100.0 + proyectos de referencia |
| `docs/` | Formato `.qet`, arquitectura, configuración, MCP, inventario de ingeniería |
| `tools/` | Análisis de evidencia, medición de geometría, `md_to_docx.py` |
| `AGENTS.md` | Reglas, estado actual y hoja de ruta del workspace |

## Qué NO hacer

- ❌ No escribas XML del .qet a mano sin evidencia (usa el generador).
- ❌ No edites los `.qet` con editor de texto para "arreglarlos" — regenera.
- ❌ No resuelvas silenciosamente discrepancias de ingeniería — regístralas.
- ❌ No inventes etiquetas XML, atributos ni símbolos que no estén en la biblioteca.
- ❌ No muevas elementos con `locked: true` sin que el usuario lo pida.
- ❌ No sobrescribas `evidencia/roundtrip/` — es la prueba del formato.
