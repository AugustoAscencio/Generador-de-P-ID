# ARCHITECTURE.md — Arquitectura de qetgen v1.0

> Documento normativo. Describe **qué** hace cada capa, **por qué** está
> separada así y qué garantías ofrece. Si el código y este documento
> discrepan, el código tiene un bug.

---

## 1. Principios rectores

| # | Principio | Consecuencia práctica |
|---|---|---|
| 1 | **Evidencia, no suposición** | Nada del formato `.qet` está inventado: todo procede de archivos reales de QElectroTech 0.100.0, documentados en [`QET_FORMAT_NOTES.md`](QET_FORMAT_NOTES.md) con etiquetas CONFIRMADO / INFERIDO. |
| 2 | **La ingeniería no la decide la herramienta** | El motor *representa* especificaciones; no inventa componentes, valores ni conexiones. Lo no confirmado se marca `PENDIENTE DE VERIFICACIÓN`. |
| 3 | **Capas con dependencias en una sola dirección** | `core ← layout ← exporters ← cli/mcp`. Ninguna capa interna importa hacia fuera. |
| 4 | **Contratos antes que convenciones** | Los modelos son Pydantic estrictos (`extra="forbid"`): un error se detecta en el borde, con la ruta exacta del campo. |
| 5 | **Cero sorpresas en el formato** | El exportador `.qet` solo escribe etiquetas confirmadas. El motor geométrico **no** escribe geometría en el `.qet` (QET recalcula las rutas). |
| 6 | **Regenerable** | Ningún entregable se edita a mano: se regenera desde el modelo. |
| 7 | **Documentación viva** | `docs/`, `SKILL.md` y `AGENTS.md` se actualizan en el mismo commit que el código que cambian. |

---

## 2. Vista de capas

```
┌──────────────────────────────────────────────────────────────────────┐
│  APLICACIONES        cli/  ·  mcp_server/  ·  scripts de tools/     │
└───────────────┬──────────────────────────────────────────────────────┘
                │  usan servicios (una sola lógica para CLI y MCP)
┌───────────────▼──────────────────────────────────────────────────────┐
│  APLICACIÓN/CASO      sheets/fv588/  (contenido de ingeniería)       │
└───────────────┬──────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────┐   ┌──────────────────────────────────┐
│  EXPORTADORES               │   │  VALIDACIÓN                       │
│  exporters/qet  (XML .qet)  │   │  validation/structural.py          │
│  exporters/svg  (preview)   │   │  validation/aesthetics.py          │
│  exporters/json (canónico)  │   │  (reglas de dominio → diagnósticos)│
└───────────────┬──────────────┘   └──────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────┐
│  MOTOR GEOMÉTRICO          layout/                                  │
│  geometry · grid (snap) · collision · textmetrics · labels ·       │
│  router (Manhattan A*) · autolayout (respeta locked)               │
└───────────────┬──────────────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────────────┐
│  NÚCLEO                     core/                                   │
│  models (Pydantic) · catalog (.elmt real) · sheet (formatos/zona    │
│  segura) · geometry (BBox/Vec2) · io (JSON) · errors               │
└──────────────────────────────────────────────────────────────────────┘
```

### Regla de dependencia

```
core  →  (nada del proyecto)
layout → core
exporters → core
validation → core
cli / mcp_server → core, layout, exporters, validation
sheets/fv588 → core
```

`core` **no importa** `xml.etree.ElementTree` en sus estructuras de datos:
el XML del `.elmt` se relee en el exportador cuando hay que embeberlo.
Esto permite añadir un exportador nuevo (DXF, HTML, PDF) sin tocar el núcleo.

---

## 3. Módulos

### 3.1 `core/` — el dominio

| Módulo | Responsabilidad | Garantía |
|---|---|---|
| `models.py` | `Project`, `Sheet`, `Component`, `Port`, `Connection`, `Label`, `Shape` | Pydantic v2 estricto: tipos, campos obligatorios, rangos obvios, alias `from`/`to`. |
| `catalog.py` | Clave lógica → `.elmt` real: terminales, caja envolvente, hotspot, posición de etiqueta | Todo dato extraído del archivo real; nada asumido. |
| `sheet.py` | Formatos de hoja, zona segura, banda del cajetín | `height = rows×rowsize + 20` (129/129 folios reales). |
| `geometry.py` | `Vec2`, `BBox` (AABB pura, inmutable) | Primitivas sin dependencias. |
| `io.py` | Carga/guardado JSON canónico, formato plano heredado | Ida y vuelta **sin pérdida** (la v0.1 perdía `author`/`date`/`indexrev`). |
| `errors.py` | Jerarquía de excepciones con código | El CLI y el MCP mapean cada fallo a un mensaje accionable. |

### 3.2 `layout/` — el motor geométrico

| Módulo | Responsabilidad |
|---|---|
| `geometry.py` | Motor: intersección, inflado, recorte, transformación de cajas. |
| `grid.py` | *Snap-to-grid* configurable (paso en px, alineación por eje). |
| `collision.py` | Detección de solapes reales entre símbolos, etiquetas y bloques. |
| `textmetrics.py` | Estimación métrica del tamaño de un texto (ancho/alto) a partir de fuente, tamaño y contenido. |
| `labels.py` | Colocación de etiquetas: candidatas N/E/S/O con respiro, elección de la primera libre. |
| `router.py` | Routing Manhattan con A*: penalización de giros, penalización de cruces, separación mínima entre líneas paralelas. |
| `autolayout.py` | Reubicación de elementos **respetando `locked: true`**. |

### 3.3 `exporters/` — las salidas

| Exportador | Salida | Notas |
|---|---|---|
| `qet/` | `.qet` (XML plano UTF-8, sin BOM) | Escritura **atómica**; orden de hijos y atributos conforme a la evidencia. |
| `json/` | JSON canónico | Simétrico con `core.io`. |
| `svg/` | SVG de previsualización | Dibuja las rutas calculadas por el router (QET no expone su propio trazado). |

### 3.4 `validation/` — los diagnósticos

* `structural.py`: reglas de dominio → **errores** (bloquean) y **avisos** (informan).
* `aesthetics.py`: auditoría geométrica → márgenes, solapes, legibilidad, densidad, cruces.

Un error impide exportar; un aviso deja decidir al usuario o a la IA.

### 3.5 `cli/` y `mcp_server/` — las interfaces

* `cli/`: subcomandos `build`, `validate`, `export`, `symbols`, `sheets`, `fv588`,
  `layout`, `serve`. Salida JSON opcional para integraciones.
* `mcp_server/`: servidor MCP por `stdio` con SDK oficial si está disponible y
  **fallback propio** (JSON-RPC 2.0) si no, para que funcione sin instalar nada.

### 3.6 `sheets/fv588/` — el caso de aplicación

Contenido de ingeniería del sistema de 588 módulos: 18 folios, registry
documental y plantillas paramétricas (MÓDULO TIPO × 588). **No** pertenece al
núcleo: el motor no sabe nada de fotovoltaico.

---

## 4. Flujo de datos completo

```
JSON  ──▶ core.io.load_spec ──▶ Project (Pydantic, estricto)
                                      │
                                      ├──▶ validation.structural ──▶ errores/avisos
                                      │
                                      ├──▶ layout (opcional)
                                      │      snap · colisiones · etiquetas · rutas
                                      │      → escribe coordenadas y waypoints
                                      │
                                      ├──▶ validation.aesthetics ──▶ calidad del plano
                                      │
                                      └──▶ exporters.qet ──▶ .qet (UTF-8, sin BOM)
                                                 └──────▶ exporters.svg ──▶ preview
```

El `.qet` **no** contiene la geometría de rutas: QElectroTech recalcula el
trazado de los conductores al abrir el proyecto (evidencia §4 del formato).
Nuestra ruta ortogonal vive en el modelo (`Connection.waypoints`) y alimenta
el SVG, el validador estético y el auto-layout.

---

## 5. Contrato del formato `.qet`

Todo lo que el exportador escribe está en [`QET_FORMAT_NOTES.md`](QET_FORMAT_NOTES.md).
Resumen:

| Elemento | Atributos clave | Estado |
|---|---|---|
| `<project>` | `title`, `version="0.100.0"` | CONFIRMADO |
| `<diagram>` | `cols`, `rows`, `colsize`, `rowsize`, `height`, `order` | CONFIRMADO |
| `<element>` | `uuid`, `orientation`, `type="embed://import/…"`, `x`, `y`, `z`, `prefix` | CONFIRMADO |
| `<terminals>` | `id` **global por folio**, `orientation` numérica, `x`/`y` relativas al hotspot, `uuid` de la definición | CONFIRMADO |
| `<conductor>` | `element1`/`terminal1`/`element2`/`terminal2` (UUID) | CONFIRMADO |
| `<input>` | texto en HTML richtext de Qt, `size`, `font` | CONFIRMADO |
| `<shape>` | `x1/y1/x2/y2`, `<pen/>`, `<brush/>` | CONFIRMADO |
| `<collection>` | una por proyecto, un `<element>` por símbolo usado | CONFIRMADO |

---

## 6. Reglas de evolución

1. **Un cambio de formato JSON es un cambio incompatible**: se documenta en
   `CHANGELOG.md` y se migran los ejemplos afectados.
2. **Un cambio del exportador `.qet` exige evidencia nueva**: primero se
   analiza un archivo real con `tools/inspect_qet.py` / `tools/deep_qet.py`,
   después se documenta en `QET_FORMAT_NOTES.md`, después se implementa.
3. **La v0.1 sigue funcionando** mientras exista `qet_generator/` (fachada).
   Se elimina en la v2.0.
4. **Todo commit que cambia código cambia tests y docs.**

---

## 7. Metodología de evidencia

El repositorio incluye las herramientas que sostienen las afirmaciones:

| Herramienta | Para qué |
|---|---|
| `tools/inspect_qet.py` | Censo de etiquetas, atributos y tipos de un `.qet`. |
| `tools/deep_qet.py` | Análisis profundo: UUID, conductores, ids de terminal, inputs, colección. |
| `tools/scan_multifolio.py` | Compara ids de terminal entre folios. |
| `tools/scan_element_types.py` | Clasifica cómo se referencian los símbolos. |
| `tools/build_sheets.py` | Regenera el JSON del caso FV 588. |
| `tools/md_to_docx.py` | Markdown → Word con formato profesional (Pandoc + python-docx). |

Y las **evidencias de formato** medidas sobre la instalación real:

| Medición | Resultado | Dónde |
|---|---|---|
| `height == rows×rowsize + 20` | **129/129 folios (100 %)** | `QET_FORMAT_NOTES.md` §12 |
| Anchura = `cols×colsize` | 129/129 folios | `QET_FORMAT_NOTES.md` §12 |
| Tamaños de hoja distintos | 12 presets en uso real | `core/sheet.py` |
| Elementos dentro del área útil | 105/114 folios (92 %) | `QET_FORMAT_NOTES.md` §12 |
| Primitivas de los `.elmt` | 8 tipos sobre 8.597 archivos | `core/catalog.py` |
