<div align="center">

# qetgen

### Generador profesional de documentación eléctrica para QElectroTech

**De una especificación JSON a planos `.qet` nativos, editables y trazables.**

[![CI](https://github.com/AugustoAscencio/Generador-de-P-ID/actions/workflows/ci.yml/badge.svg)](https://github.com/AugustoAscencio/Generador-de-P-ID/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![QElectroTech](https://img.shields.io/badge/QElectroTech-0.100.0-blue.svg)](https://github.com/QelectroTech/qelectrotech)
[![MCP](https://img.shields.io/badge/MCP-universal-orange.svg)](docs/MCP.md)
[![Release](https://img.shields.io/github/v/release/AugustoAscencio/Generador-de-P-ID.svg)](https://github.com/AugustoAscencio/Generador-de-P-ID/releases)

</div>

---

## Qué es esto

`qetgen` es un **motor CAD/EDA para documentación eléctrica**. Convierte una
especificación estructurada (JSON) en un **proyecto nativo de QElectroTech
(`.qet`)**: diagramas, símbolos reales de biblioteca, conexiones entre
terminales, textos, bloques funcionales y metadatos BOM.

No produce un dibujo "parecido". Produce un archivo que **se abre, se edita y
se re-guarda** en QElectroTech sin pérdidas.

```
ESPECIFICACIÓN (JSON)  →  MOTOR qetgen  →  PROYECTO .QET  →  QElectroTech  →  PDF
                              │
                              ├── motor geométrico (colisiones, routing, auto-layout)
                              ├── validador de estructura + auditoría estética
                              ├── exportador SVG de previsualización
                              └── servidor MCP universal (IA / CAD / pipelines)
```

**Demostrado en un caso real:** la documentación eléctrica completa de un
sistema fotovoltaico de **588 módulos × 8 paneles** con seguimiento solar
biaxial — **18 planos industriales**, editables y trazables.

---

## Por qué este proyecto es diferente: ingeniería inversa con evidencia

El punto diferencial no es la generación: es **no inventar nada**. El formato
`.qet` es un XML interno de QElectroTech sin especificación publicada, y casi
todos los generadores de este tipo lo adivinan. Aquí se **descifró con
evidencia**:

| Paso | Qué se hizo | Evidencia |
|---|---|---|
| **Censo** | 22 proyectos de ejemplo de la instalación (129 folios, 3525 elementos, 416 textos) y **8597 archivos `.elmt`** analizados con sondas propias | [`tools/`](tools/) |
| **Documentación** | El formato etiqueta por etiqueta, con **CONFIRMADO** vs **INFERIDO** y 12 secciones | [`docs/QET_FORMAT_NOTES.md`](docs/QET_FORMAT_NOTES.md) |
| **Round-trip** | El proyecto generado se abrió y re-guardó en QElectroTech 0.100.0: el diff confirmó que la aplicación entendió el **100 %** de UUIDs, terminales, conductores, etiquetas y colección embebida | [`evidencia/roundtrip/`](evidencia/) |
| **Geometría** | El tamaño de folio y la métrica tipográfica, **calibradas** contra los 416 textos reales (no estimadas a ojo) | [`tools/measure_sheet_geometry.py`](tools/measure_sheet_geometry.py) |

> `docs/QET_FORMAT_NOTES.md` §12 documenta, por ejemplo, que `<diagram>`
> **no guarda** el atributo `width` (0 de 129 folios lo tienen) y que
> `height == rows × rowsize + 20` se cumple en **129/129**. El motor deriva
> el ancho; nunca inventa un atributo.

---

## Instalación

```bash
git clone https://github.com/AugustoAscencio/Generador-de-P-ID.git
cd Generador-de-P-ID

pip install -e .              # motor + CLI `qetgen`
pip install -e ".[mcp]"       # además, el SDK oficial de MCP (opcional)
pip install -e ".[dev]"       # herramientas de desarrollo (ruff, pytest)

qetgen doctor                 # comprueba Python, QET, catálogo y configuración
```

**Requisitos**: Python ≥ 3.10 y **QElectroTech 0.100.0** instalado (los
símbolos se leen de su biblioteca real: `C:\Program Files\QElectroTech\elements`).

---

## Uso en 30 segundos

```bash
# 1) Regenerar el caso real FV 588 (18 planos)
qetgen fv588

# 2) Auditar la estética de un proyecto (código de salida 1 si hay defectos)
qetgen layout examples/proyecto_fv_588.json --check

# 3) Reorganizar un plano en columnas lógicas (simulación: no escribe nada)
qetgen layout examples/proyecto_fv_588.json --folio 3 --auto-layout

# 4) Previsualizar en SVG (primitivas reales de cada .elmt)
qetgen layout examples/proyecto_fv_588.json --preview preview/

# 5) Generar desde una especificación propia
qetgen build mi_proyecto.json -o salida.qet
```

---

## Referencia de la CLI

| Comando | Qué hace |
|---|---|
| `qetgen build` | Valida un JSON y genera el `.qet` (escritura **atómica**). |
| `qetgen validate` | Valida un JSON sin generar nada. |
| `qetgen export` | Exporta un JSON a `.qet` o a JSON canónico. |
| `qetgen symbols` | Lista los **14 símbolos reales** de la biblioteca con sus terminales. |
| `qetgen sheets` | Lista los formatos de folio disponibles con su geometría. |
| `qetgen fv588` | Regenera el paquete completo de 18 planos del caso FV 588. |
| `qetgen layout` | **Motor de layout**: snap, auto-layout, routing, auditoría y previsualización. |
| `qetgen doctor` | **Diagnóstico del entorno**: Python, dependencias, QET, catálogo, configuración y proyecto. |
| `qetgen serve` | **Servidor MCP** por `stdio`. |

Códigos de salida: `0` OK · `1` validación fallida · `2` entrada inválida ·
`3` error de E/S.

### `qetgen layout` en detalle

```bash
qetgen layout spec.json [opciones]
```

| Opción | Efecto |
|---|---|
| `--snap` / `--snap-texts` | Alinea a la rejilla lo que no esté bloqueado. |
| `--auto-layout` | Reubica en columnas lógicas (**modo híbrido**: respeta `locked: true`). |
| `--no-route` | No calcula las rutas ortogonales. |
| `--ignore-locked` | Desactiva el modo híbrido. |
| `--folio N` | Opera sobre un solo folio (un folio inexistente es un error claro). |
| `--check` | Auditoría estética; **sale con código 1** si hay defectos. |
| `--preview DIR` | Escribe un SVG por folio. |
| `--apply` | Guarda el JSON resultante. **Sin esta opción es simulación.** |
| `--json` | Salida estructurada para integraciones. |

---

## El motor

### Motor geométrico (`layout/`)

- **Cajas reales**: cada símbolo tiene dos cajas — la de **tinta** (primitivas
  reales del `<description>`, la que colisiona) y la **reservada**
  (`width`/`height`/`hotspot` del `.elmt`, la que define el margen de
  colocación). Las 14 del catálogo están medidas y verificadas.
- **Rotación correcta**: el *hotspot* no es el centro del símbolo; el motor
  trabaja sobre la caja **rotada** (orientación 0..3).
- **Colisiones con criterio**: la contención intencional (un texto dentro de
  un bloque, la etiqueta de su propio símbolo) **no** es un solape; dos cajas
  idénticas **sí** lo son.
- **Routing Manhattan con A\\***: penalización de giros, cruces y separación de
  cables paralelos; intersección segmento-obstáculo **exacta** (Liang–Barsky),
  no muestreada.
- **Auto-layout en modo híbrido**: columnas lógicas según el grafo de
  conexiones, acotado al folio, alineado a rejilla, con salto de columna si
  una capa no cabe.

### Auditoría con diagnósticos accionables

Códigos estables y severidad graduada:

| Severidad | Códigos |
|---|---|
| **error** | `SYMBOL_OVERLAP`, `OUT_OF_SHEET` |
| **warning** | `TEXT_OVERLAP`, `LABEL_OVERLAP`, `ROUTE_CROSSING`, `ROUTE_TOO_CLOSE` |
| **info** | `BLOCK_CROSSING`, `EMPTY_SHEET` |

Cada diagnóstico lleva **qué pasa**, **por qué importa** y **qué cambiar**.

### Configuración central

Un solo archivo gobierna hoja, márgenes, rejilla, tipografía, cableado y
estilos — validado con Pydantic estricto (`extra="forbid"`): una clave
inventada se rechaza al cargar, no a mitad de un cálculo.

```yaml
sheet:
  format: A3_17x8
  margin: 8
  edge_tolerance: 36        # calibrada con 416 textos reales
layout:
  grid_size: 10
  respect_locked: true      # modo híbrido
  clearance: 18             # holgura al reubicar
  route_clearance: 6        # holgura al cablear (distinta, a propósito)
```

→ Referencia completa: [`docs/CONFIGURACION.md`](docs/CONFIGURACION.md)

---

## Servidor MCP universal

Expone el motor como **herramientas MCP** por `stdio`, para que una IA, un
cliente CAD o un pipeline pueda construir planos sin salir del protocolo.

**8 herramientas atómicas y tipadas** · **4 recursos** · **2 prompts**

| Herramienta | Qué hace |
|---|---|
| `crear_diagrama` | Crea un proyecto (o carga uno desde un JSON). |
| `listar_simbolos` | Lista los símbolos **reales** con terminales y geometría. |
| `agregar_elemento` | Coloca un símbolo (con `bloqueado` para el modo híbrido). |
| `conectar_elementos` | Conecta dos terminales, validando que existan. |
| `ejecutar_auto_layout` | Reorganiza y cablea; `aplicar: false` simula. |
| `validar_estetica` | Audita y devuelve diagnósticos con sugerencia. |
| `obtener_resumen_canvas` | Resume el estado del lienzo. |
| `exportar_archivo` | Guarda el `.qet` editable o el JSON canónico. |

Funciona **con el SDK oficial** (`pip install qetgen[mcp]`) y **con un
fallback propio** (JSON-RPC 2.0) si no está instalado: la interfaz es
idéntica en ambos casos.

```json
{
  "mcpServers": {
    "qetgen": {
      "command": "qetgen",
      "args": ["serve"]
    }
  }
}
```

→ Guía completa: [`docs/MCP.md`](docs/MCP.md) · ejemplo: [`mcp_config_example.json`](mcp_config_example.json)

---

## Arquitectura

```
src/qetgen/
├── core/         modelos Pydantic estrictos, catálogo, geometría, E/S JSON
├── layout/       motor geométrico: rejilla, colocación, colisiones, routing
├── exporters/    .qet (nativo), JSON canónico, SVG de previsualización
├── validation/   estructura (duplicados, terminales, fechas) + estética
├── cli/          interfaz de línea de comandos
├── mcp_server/   servidor MCP (SDK oficial + fallback propio)
├── sheets/       las 18 hojas paramétricas del caso FV 588
└── legacy/       alias de la v0.1 (se eliminan en la v2.0)
```

Reglas de dependencia: `core` no depende de nada; `layout` depende de `core`;
`exporters` y `validation` dependen de `core`; `cli` y `mcp_server` dependen de
todo. El **núcleo nunca contiene XML de ElementTree**: el exportador relee el
`.elmt` para embeberlo.

→ Detalle: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Caso real: FV 588 módulos

| | |
|---|---|
| **Alcance** | 588 módulos × 8 paneles, seguimiento solar biaxial (DomBusTracker2, actuadores, sensores, RS485, USR-W610/DR404) |
| **Planos** | 18 (D-001…D-018): arquitectura, string FV, protección DC, 24 VDC, ejes elevación/azimut, sensores, viento/STOW, mapa E/S, estados, enclavamientos, RS485/IoT, tierra TT, canalizaciones, borneras, interfaz de planta |
| **Contenido** | 111 elementos, 60 conductores, 412 textos, ~130 bloques |
| **Filosofía** | **MÓDULO TIPO × 588**: la ingeniería repetitiva se documenta una vez y se escala por arquitectura de repetición — nunca 588 dibujos duplicados |
| **Trazabilidad** | Cada dato cita su fuente; lo no confirmado se marca **«PENDIENTE DE VERIFICACIÓN»** — nunca se inventa |

| Entregable | Contenido |
|---|---|
| [`entregables/Proyecto_FV_588_Modulos.qet`](entregables/) | Los 18 planos, editables en QElectroTech |
| [`entregables/`](entregables/) | Memoria técnica (MD/Word) y documento del paquete |
| [`fuentes/`](fuentes/) | Las fuentes técnicas **únicas** de ingeniería |

> **Discrepancia registrada (no se resuelve en silencio):** el cliente indica
> «650 kW» y 588 módulos; el documento técnico usa paneles de 625–650 Wp y
> calcula ~1539 módulos para 8 MW. El requisito vigente es **588 módulos** y
> en los esquemas la potencia es **650 Wp**.

---

## Calidad

- **227 tests automáticos** (`unittest`, sin dependencias externas) que cubren
  formato, modelos, colisiones, routing, auditoría, CLI, configuración y el
  protocolo MCP completo.
- **Suite hermética**: los tests usan los 14 `.elmt` **reales** versionados en
  `tests/fixtures/qet_elements/` (44 KB), así que el CI verifica la geometría
  real **sin** necesidad de que QElectroTech esté instalado en el runner.
  `tests/test_fixtures.py` garantiza que son byte-idénticos (SHA-256) a la
  biblioteca instalada.
- **CI en GitHub Actions**: Python 3.10 → 3.13, `unittest` + `ruff`.
- **Control de regresión**: el `.qet` generado es **estructuralmente idéntico**
  entre versiones (normalizando los UUID de instancia, aleatorios por diseño).
- **Escritura atómica**: archivo temporal + `replace`; un fallo no deja un
  `.qet` a medias.

```bash
python -m unittest discover -s tests      # 227 tests
ruff check src tests tools
```

---

## Documentación

| Documento | Contenido |
|---|---|
| [`docs/QET_FORMAT_NOTES.md`](docs/QET_FORMAT_NOTES.md) | El formato `.qet` real, con evidencia (CONFIRMADO / INFERIDO) |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arquitectura por capas y reglas de dependencia |
| [`docs/CONFIGURACION.md`](docs/CONFIGURACION.md) | Cada clave de configuración, con su calibración |
| [`docs/MCP.md`](docs/MCP.md) | El servidor MCP: herramientas, recursos, prompts |
| [`docs/SPEC_INVENTARIO.md`](docs/SPEC_INVENTARIO.md) | Matriz de ingeniería del caso FV, con cita de fuente |
| [`CHANGELOG.md`](CHANGELOG.md) | Historial por versión (Keep a Changelog / SemVer) |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Cómo contribuir, ejecutar tests y publicar una versión |

---

## Para agentes de IA

- [`AGENTS.md`](AGENTS.md) — reglas, estado y hoja de ruta del workspace.
- [`SKILL.md`](SKILL.md) y [`.opencode/skill/qet-generator/SKILL.md`](.opencode/skill/qet-generator/SKILL.md) —
  skill autodescubierta para usar la herramienta correctamente.

Las reglas de oro son innegociables: **no inventar el formato `.qet`**, **no
decidir la ingeniería** (solo representarla), **usar símbolos reales de
biblioteca** y **validar antes de generar**.

---

## Licencia

[MIT](LICENSE) © Augusto Ascencio.

---

<div align="center">

**qetgen** — *representar la ingeniería, no decidirla.*

</div>
