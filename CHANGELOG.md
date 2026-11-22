# CHANGELOG — qetgen

Todas las versiones relevantes del proyecto. El formato sigue
[Keep a Changelog](https://keepachangelog.com/es/1.1.0/) y el versionado es
[SemVer](https://semver.org/lang/es/).

---

## [No publicado] — trabajo en curso

### Añadido

- Motor geométrico completo (`layout/`): *snap-to-grid*, colisiones con cajas
  envolventes reales, colocación de etiquetas y routing Manhattan con A*.
- Zona segura y cajetín con base documental (129/129 folios reales).
- Exportador SVG de previsualización.
- Configuración central (`config/default.yaml`).
- Modo híbrido (`locked: true`) y validador estético.
- Servidor MCP universal (`mcp_server/`).

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
[0.2.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.2.0
[0.1.0]: https://github.com/AugustoAscencio/Generador-de-P-ID/releases/tag/v0.1.0
