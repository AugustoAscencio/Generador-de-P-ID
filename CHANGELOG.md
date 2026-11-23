# CHANGELOG — qetgen

Todas las versiones relevantes del proyecto. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es/1.1.0/) y el versionado es
[SemVer](https://semver.org/lang/es/).

---

## [No publicado] — trabajo en curso

---

## [1.0.1] — 2026-11-22

### Corregido

- **CI de GitHub Actions en rojo en las 8 combinaciones de la matriz**
  (Python 3.10 → 3.13 × Ubuntu + Windows) y el job de empaquetado omitido
  por dependencia de los tests. Dos causas distintas, ambas resueltas:
  - **Los checks de consola se ejecutaban con un *here-doc* de bash**
    (`python - <<'PY'`), que `pwsh` no entiende: en Windows el paso
    *Verificar la versión declarada* fallaba y el resto del job se
    omitía. Ahora los checks son **scripts de Python**
    (`tools/check_version.py`, `tools/check_doc_links.py`), que se ejecutan
    igual en `bash` y en `pwsh`.
  - **Los tests dependían de que QElectroTech estuviera instalado** en la
    máquina que los ejecutaba: en los runners de Linux (sin QET) fallaban
    34 tests (16 fallos + 18 errores), y la suite no verificaba nada de
    la geometría real. La suite es ahora **hermética**.
- **La suite de tests ya no depende de la instalación local de
  QElectroTech.** Los 14 `.elmt` reales que usa el catálogo están
  versionados en `tests/fixtures/qet_elements/` (44 KB, copia byte-exacta
  de la biblioteca 0.100.0) y `tests/test_fixtures.py` garantiza que:
  - cubren **exactamente** el catálogo (ni uno de más, ni uno de menos);
  - son **byte-idénticos** (SHA-256) al `.elmt` de la biblioteca instalada
    — comparación que se **omite** si QElectroTech no está presente.
  La **producción** (CLI y MCP) sigue usando siempre la biblioteca
  instalada: los fixtures son material de prueba, nunca una fuente de
  símbolos en tiempo de ejecución.
- `qetgen sheets` no aceptaba las opciones comunes (`--catalog`,
  `--library`, `--config`): era el único subcomando que las ignoraba.
- `sdk_server.py` usaba el tipo `Any` sin importarlo (`F821`): el
  servidor MCP con SDK oficial fallaba al arrancar.
- `session.py` asignaba una variable que no se usaba (`F841`).

### Añadido

- **`tools/sync_fixtures.py`**: refresca los fixtures desde la biblioteca
  instalada y verifica sus SHA-256 (`--check` solo verifica). El CI lo
  ejecuta para detectar que los fixtures han derivado.
- **`tests/fixtures/README.md`**: procedencia, justificación y procedimiento
  de refresco de los fixtures.

### Cambiado

- **Lint (`ruff`)**: el CI ejecutaba `ruff` pero nunca llegó a correr
  (los tests fallaban antes). Con la regla activa se han corregido
  **110 avisos** del código: imports sin usar, anotaciones obsoletas,
  `zip()` sin `strict=` explícito (con la decisión documentada caso por
  caso: `strict=True` donde las longitudes deben coincidir,
  `strict=False` en ventanas deslizantes) y 22 sentencias con `;` en
  `sheets/fv588/sheets.py`. El código no cambia de comportamiento: el
  `.qet` de FV 588 sigue siendo **estructuralmente idéntico** al de la
  v1.0.0.
- `qetgen doctor` y `qetgen build` del job de empaquetado usan la
  biblioteca de fixtures: el smoke test ejercita catálogo, diagnóstico y
  generación **sin** depender de QElectroTech en el runner.

### Verificación

- **227 tests** en verde (221 + 6 nuevos de cobertura e integridad de los
  fixtures), con QElectroTech instalado **y sin él**.
- `ruff check src tests tools`: **0 errores**.
- Simulación completa del CI (los 6 pasos, en un entorno sin QET): todo OK.
- El `.qet` de FV 588 y su JSON de especificación: **idénticos** a los de
  la v1.0.0.

---

## [1.0.0] — 2026-11-22

### Añadido

- **Servidor MCP universal** (`src/qetgen/mcp_server/`): expone el motor como
  herramientas MCP por `stdio`.
  - **8 herramientas atómicas y tipadas**: `crear_diagrama`, `listar_simbolos`,
    `agregar_elemento`, `conectar_elementos`, `ejecutar_auto_layout`,
    `validar_estetica`, `obtener_resumen_canvas`, `exportar_archivo`.
    El `inputSchema` de cada una se **genera del modelo Pydantic** que la
    valida: una sola fuente de verdad para los tipos.
  - **4 recursos**: `qetgen://catalogo`, `qetgen://config`,
    `qetgen://formatos-hoja`, `qetgen://proyecto`.
  - **2 prompts**: `system_prompt` (contrato de trabajo de la IA) y
    `revisar_plano` (flujo de revisión accionable).
  - **Dos transportes, una interfaz**: con el **SDK oficial** (`mcp>=1.0`) o
    con un **fallback propio** (JSON-RPC 2.0 sobre JSON Lines) si el SDK no
    está instalado. Ambos delegan en el mismo dispatcher.
  - Errores **accionables** (nunca `KeyError` desnudo) y resultados con
    `isError` + `structuredContent`.
- **`qetgen serve`**: arranca el servidor MCP (`--fallback` fuerza el
  transporte propio).
- **`mcp_config_example.json`**: configuración de cliente lista para copiar.
- **Documentación nueva**:
  - `docs/CONFIGURACION.md`: **cada clave** de la configuración central, con
    su calibración y su evidencia.
  - `docs/MCP.md`: guía completa del servidor MCP (herramientas, recursos,
    prompts, diagnóstico).
  - `README.md`: reescrito para v1.0.0 (arquitectura, referencia de la CLI,
    motor, MCP, caso FV 588, evidencia).
  - `CONTRIBUTING.md`: entorno, reglas, flujo de trabajo, estilo y proceso de
    publicación.
- **`LICENSE`**: MIT.
- **CI de GitHub Actions** (`.github/workflows/ci.yml`): Python 3.10 → 3.13 en
  Ubuntu y Windows, `unittest` + `ruff`, empaquetado (`build` + `twine
  check`) y verificación de los enlaces de la documentación.
- `qetgen` instalado como comando (`pip install -e .` → `qetgen …`).

### Cambiado

- `SKILL.md` y `.opencode/skill/qet-generator/SKILL.md` reescritos para la
  arquitectura actual: rutas `src/qetgen/`, CLI `qetgen`, configuración
  central, motor de layout, códigos de diagnóstico y servidor MCP.
- `AGENTS.md` actualizado al estado v1.0.0, con los defectos **reales**
  detectados en el caso FV 588 registrados (8 textos desbordados, 2
  terminales reutilizadas).
- `docs/ARCHITECTURE.md`: `layout/` incluye `placement.py` y `pipeline.py`;
  `cli/` y `mcp_server/` documentados con sus subcomandos.

### Verificación

- **221 tests** en verde (55 heredados de la v0.1 + 166 nuevos), incluidos
  **30 tests del protocolo MCP** (dispatcher JSON-RPC, recursos, prompts y
  un proceso real `qetgen serve --fallback` de extremo a extremo).
- Sonda MCP de extremo a extremo: **17/17 respuestas** correctas y un `.qet`
  válido de 10 469 bytes exportado desde el servidor.
- El `.qet` de FV 588 sigue siendo **estructuralmente idéntico** al de la
  v0.4.0: el servidor MCP y el motor geométrico no alteran el entregable.

---

## [0.4.0] — 2026-11-22

### Añadido

- **`qetgen layout`**: ejecuta el motor de layout desde la línea de comandos.
  - `--snap` / `--snap-texts`: alineación a la rejilla de lo no bloqueado.
  - `--auto-layout`: reubicación en columnas lógicas (modo híbrido).
  - `--check`: auditoría estética; **código de salida 1** si hay defectos.
  - `--preview DIR`: previsualización SVG (respeta `--folio`).
  - `--apply`: persiste el JSON resultante (por defecto es **simulación**).
  - `--folio N`: opera sobre un solo folio; un folio inexistente es un error
    claro, no un silencio.
  - `--json`: salida estructurada para integraciones.
- **`qetgen doctor`**: diagnóstico del entorno (Python, Pydantic, PyYAML, SDK
  de MCP, configuración, biblioteca de QElectroTech, catálogo de símbolos y,
  opcionalmente, el proyecto). Cada comprobación tiene estado
  (`ok`/`warn`/`error`) y un consejo accionable.
- **`layout/pipeline.py`**: orquestación (snap → auto-layout → routing) con
  informe de lo movido, lo bloqueado y lo no resuelto. La comparten la CLI y
  el servidor MCP.
- Nuevos parámetros de configuración: `column_gap`, `row_gap`, `clearance`,
  `route_clearance`.

### Corregido

- El **auto-layout sacaba símbolos del folio** (colocaba un panel en x=1030
  en un folio de 1020): ahora calcula la caja rotada de cada símbolo, acota
  la posición del hotspot y **comprime el hueco entre columnas** si no caben.
- El **ajuste de seguridad rompía la rejilla** (x=25 en vez de 30): el
  ajuste se hace sobre los múltiplos de la rejilla que caben.
- Una capa con demasiados elementos se quedaba **sin colocar**: el flujo
  envuelve a una columna nueva a la derecha.
- El router **tragaba las terminales** con una holgura de 18 px: la holgura
  del cableado (`route_clearance`, 6 px) es ahora independiente de la del
  reubicado (`clearance`, 18 px).
- Un terminal situado dentro de la caja de un símbolo vecino ya puede
  **salir** de ella (antes no había ningún nodo de rejilla válido).
- La previsualización SVG respetaba `--folio` (exportaba los 18 folios).

### Verificación

- **191 tests** en verde (55 heredados de la v0.1 + 136 nuevos).
- Caso real FV 588: auto-layout de los **111 símbolos sin dejar ninguno sin
  colocar**, **0 solapes entre símbolos** y **60/60 rutas** trazadas.
- `qetgen doctor` detecta honestamente los 8 defectos de texto desbordado
  del proyecto FV 588 (código de salida 1).

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

[1.0.1]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v1.0.1
[1.0.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v1.0.0
[0.4.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.4.0
[0.3.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.3.0
[0.2.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.2.0
[0.1.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.1.0
