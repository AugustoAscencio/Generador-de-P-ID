# CHANGELOG — qetgen

Todas las versiones relevantes del proyecto. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es/1.1.0/) y el versionado es
[SemVer](https://semver.org/lang/es/).

---

## [No publicado] — trabajo en curso

### Añadido

- Servidor MCP universal (`mcp_server/`).

---

## [0.3.0] — 2026-11-22

### Añadido

- **Motor geométrico completo** (`layout/`):
  - `grid.py`: cuadrícula de alineación (*snap-to-grid*) configurable.
  - `placement.py`: cajas reales de símbolos (rotación 0..3 incluida),
    posición y dirección de terminales, cajas de texto y de bloque.
  - `collision.py`: detección de solapes distinguiendo **contención
    intencional** (texto dentro de un bloque, etiqueta de su propio símbolo)
    de **solape real**.
  - `textmetrics.py`: métrica tipográfica aproximada pero reproducible.
  - `labels.py`: colocación de etiquetas en la primera posición libre.
  - `router.py`: routing **Manhattan con A\*** (estado nodo+dirección,
    penalización de giros, cruces y separación de paralelos).
  - `autolayout.py`: reubicación automática en **modo híbrido**
    (`locked: true` = el ingeniero manda).
- **Exportador SVG** (`exporters/svg/`): previsualización que dibuja las
  **primitivas reales** de cada `.elmt` (no aproximaciones) y las rutas
  calculadas.
- **Validador estético** (`validation/aesthetics.py`): auditoría con códigos
  estables (`OUT_OF_SHEET`, `SYMBOL_OVERLAP`, `TEXT_OVERLAP`,
  `ROUTE_CROSSING`, `ROUTE_TOO_CLOSE`, `BLOCK_CROSSING`, …), severidad
  (`error`/`warning`/`info`) y **sugerencia accionable**.
- **Configuración central** (`config/default.yaml`) con la carga validada por
  Pydantic (`extra="forbid"`) y test de sincronía con el código.
- Sonda de evidencia reproducible `tools/measure_sheet_geometry.py`.
- `docs/QET_FORMAT_NOTES.md` §12: geometría del folio y calibración del
  motor, con las cifras medidas.

### Cambiado

- `core/catalog.py` distingue **caja de tinta** (primitivas reales de
  `<description>`, la que colisiona) de **caja reservada** (`width`/`height`
  del `.elmt`, la que define el margen de colocación).
- `core/geometry.py` incorpora `rotate_point()` y `rotated_bbox()` con la
  convención de QElectroTech (`orientation` 0..3 = 0°, 90°, 180°, 270°).

### Corregido

- Dos cajas **idénticas** se trataban como "contención" y no se reportaba el
  solape: ahora es un error real.
- La intersección segmento-obstáculo del router era un **muestreo** (podía
  dejar pasar obstáculos finos): ahora es exacta (Liang–Barsky) y los
  tramos de acceso a la rejilla también se comprueban.

### Verificación

- **174 tests** en verde (55 heredados de la v0.1 + 119 nuevos).
- Caso real FV 588: **0 solapes entre símbolos** en las 18 hojas y **9/9
  rutas** trazadas en 6 ms.
- Auditoría sobre las 18 hojas: 8 errores reales (texto desbordado),
  116 avisos y 1 info.
- Control de regresión: el `.qet` generado es **idéntico** al de la v0.2.0
  (el motor geométrico no altera el formato entregable).

---

## [0.2.0] — 2026-11-22

### Cambiado

- **Arquitectura reorganizada** en capas limpias: `core/`, `exporters/`,
  `validation/`, `cli/`, `sheets/` (y `layout/`, `mcp_server/` en curso).
- **Modelos a Pydantic v2 estrictos** (`extra="forbid"`, validación al
  asignar). Los modelos v0.1 se conservan como alias en `qetgen.legacy`.
- El motor pasa de *solo biblioteca estándar* a **Pydantic + PyYAML**
  (declarados en `pyproject.toml`).
- La E/S JSON es **canónica y simétrica**: la ida y la vuelta ya no pierde
  `author`, `date` ni `indexrev` de folio.
- La escritura del `.qet` es **atómica** (archivo temporal + `replace`).
- El texto de los planos se **escapa como HTML** antes de incrustarse.
- Estructura del repositorio plana: `src/`, `tests/`, `examples/`, `docs/`,
  `tools/`, `config/`, `resources/`, `output/`.

### Añadido

- **CLI profesional** (`qetgen`) con subcomandos `build`, `validate`, `export`,
  `symbols`, `sheets` y `fv588`; salida JSON opcional.
- **Empaquetado**: `pyproject.toml` (instalable con `pip install -e .`).
- Formatos de hoja parametrizados (12 presets derivados de tamaños reales).
- Catálogo: extracción de la **caja envolvente real** de cada símbolo a
  partir de las primitivas reales del `.elmt` (8 tipos sobre 8.597 archivos).
- Validación ampliada: fecha real, órdenes contiguos, conexiones duplicadas y
  terminales reutilizadas.

### Corregido

- `dash: "false"` en JSON se convertía en `True` (`bool("false")`).
- La clave `_comment` del catálogo se cargaba como si fuera un símbolo.
- El texto con `<`, `>` o `&` se insertaba sin escapar en el HTML de Qt.
- La geometría de terminales del condensador estaba documentada al revés.
- `int()` sobre valores JSON inválidos escapaba como `ValueError` sin
  convertir en error de especificación.

### Obsoleto

- `qet_generator/` pasa a ser **fachada de compatibilidad** de la v0.1
  (`import generator.*` sigue funcionando). Se elimina en la v2.0.

### Verificación

- **116 tests** en verde (55 heredados de la v0.1 + 61 nuevos).
- **Control de regresión v0.1 → v0.2.0**: los `.qet` generados por ambas
  versiones son **estructuralmente idénticos** (normalizando los UUID de
  instancia, que son aleatorios por diseño).

---

## [0.1.0] — 2026-09-29

### Añadido

- Generador de proyectos QElectroTech (`.qet`) desde especificación JSON,
  con formato `.qet` obtenido por ingeniería inversa y verificado por
  *round-trip* con QElectroTech 0.100.0.
- Catálogo de **14 símbolos reales** de la biblioteca instalada.
- Motor multi-folio (18 planos del caso FV 588 módulos) con arquitectura
  **MÓDULO TIPO × 588**.
- 55 tests, análisis de evidencia (`inspect_qet`, `deep_qet`) y
  conversión Markdown → Word.

[1.0.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v1.0.0
[0.4.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.4.0
[0.3.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.3.0
[0.2.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.2.0
[0.1.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.1.0
