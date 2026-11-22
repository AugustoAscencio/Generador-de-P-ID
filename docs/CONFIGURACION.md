# CONFIGURACION.md — Configuración central de qetgen

> Un único archivo gobierna **todo** lo que un usuario puede ajustar sin tocar
> código: hoja, márgenes, cuadrícula, tipografía, cableado, estilos y rutas
> de las fuentes.
>
> - Archivo entregado: [`config/default.yaml`](../config/default.yaml)
> - Formatos aceptados: **YAML** (`.yaml`, `.yml`) o **JSON** (`.json`).
> - Validación: **Pydantic v2 estricto** (`extra="forbid"`): una clave
>   desconocida o un valor fuera de rango se **rechazan al cargar**, no a
>   mitad de un cálculo.
> - Modelo de referencia: `src/qetgen/config.py`.

```bash
qetgen doctor --config mi_config.yaml     # comprueba que carga
qetgen layout spec.json --config mi_config.yaml
```

---

## 1. Cómo se usa

```bash
# La configuración por defecto (config/default.yaml del repositorio)
qetgen layout examples/proyecto_fv_588.json

# Una configuración propia
qetgen layout examples/proyecto_fv_588.json --config config/mi_proyecto.yaml

# Un perfil en JSON
qetgen doctor --config config/perfil_planta.json
```

El mismo parámetro `--config` está disponible en **todos** los subcomandos
(`build`, `validate`, `export`, `symbols`, `sheets`, `fv588`, `layout`,
`doctor`, `serve`).

### Precedencia

1. `--config <ruta>` en la línea de comandos.
2. `config/default.yaml` del repositorio (instalado).
3. Los valores por defecto del modelo (idénticos al archivo entregado — hay
   un test que lo verifica: `tests/test_config.py::test_los_valores_por_defecto_coinciden_con_el_yaml`).

> Para **heredarlo** del archivo por defecto en vez de redefinirlo entero,
> copia `config/default.yaml` y cambia solo lo que necesites. Las secciones no
> incluidas toman el valor por defecto.

---

## 2. `sheet` — Hoja, zona segura y cajetín

| Clave | Tipo | Por defecto | Qué hace |
|---|---|---|---|
| `format` | `str` | `A3_17x8` | Preset de folio. Debe ser uno de los 12 nombres de la tabla §2.1; cualquier otro valor se rechaza al cargar. |
| `margin` | `float ≥ 0` | `8` | **Margen interior de seguridad** (px): ningún símbolo, texto ni cable puede invadirlo. El cajetín inferior está excluido por definición. |
| `titleblock_height` | `float ≥ 0` | `20` | Banda inferior reservada al cajetín (px). |
| `edge_tolerance` | `float ≥ 0` | `36` | Tolerancia de borde (px). Un texto que se sale menos que esto es un **aviso**; más que esto, un **error** (`OUT_OF_SHEET`). |
| `show_grid` | `bool` | `true` | Mostrar la rejilla visible de QET. |

### 2.1 Formatos de folio disponibles

Derivados de los tamaños **reales** de la biblioteca de QElectroTech 0.100.0
(129 folios reales medidos; ver `docs/QET_FORMAT_NOTES.md` §12).

| Preset | Celdas | Celda (px) | Folio útil (px) | Folio completo (px) | Folios reales |
|---|---|---|---|---|---|
| `A3_17x8` | 17×8 | 60×80 | 1020×640 | 1020×660 | 58 ← **estándar del proyecto** |
| `A3_18x9` | 18×9 | 60×80 | 1080×720 | 1080×740 | 51 |
| `A3_20x11` | 20×11 | 60×80 | 1200×880 | 1200×900 | 1 |
| `A4_11x7` | 11×7 | 60×80 | 660×560 | 660×580 | 1 |
| `A4_10x5` | 10×5 | 60×80 | 600×400 | 600×420 | 5 |
| `A4_15x6` | 15×6 | 50×80 | 750×480 | 750×500 | 6 |
| `A2_24x11` | 24×11 | 60×80 | 1440×880 | 1440×900 | 1 |
| `A1_39x20` | 39×20 | 60×80 | 2340×1600 | 2340×1620 | 2 |
| `A0_42x21` | 42×21 | 60×80 | 2520×1680 | 2520×1700 | 1 |

### 2.2 De dónde salen estos números (evidencia)

- El **ancho no se serializa** en `<diagram>` (0 de 129 folios reales lo
  tienen): se **deriva** como `cols × colsize`. El motor nunca inventa el
  atributo `width`.
- `height == rows × rowsize + 20` — exacto en **129/129 folios**. Los 20 px
  son la banda del cajetín (`displayAt="bottom"`).
- **3486 de 3525 elementos (98,9 %)** reales caen dentro del área de dibujo
  útil, y **ninguno** rebasa el borde derecho (desbordamiento máximo: 0 px).
- `edge_tolerance = 36 px` está **calibrada con 416 textos reales**: 10 de
  ellos (2,40 %) se saldrían del folio con la métrica estimada, y 9 de esos
  10 lo hacen en 36 px o menos. El caso extremo (184 px) es un rótulo de 84
  caracteres, no un error de la métrica.

Reproduce la medición con:

```bash
python -X utf8 tools/measure_sheet_geometry.py
```

---

## 3. `layout` — Motor de layout

| Clave | Tipo | Por defecto | Qué hace |
|---|---|---|---|
| `grid_size` | `float > 0` | `10` | Paso de la cuadrícula de alineación (px). 10 px ≈ 1/6 de celda QET (60 px). |
| `snap_to_grid` | `bool` | `true` | Alinea a la rejilla lo que el ingeniero no ha bloqueado. |
| `min_separation` | `float > 0` | `12` | Separación mínima entre dos cables paralelos (px). |
| `label_margin` | `float ≥ 0` | `4` | Respiro mínimo alrededor de una etiqueta (TAG, calibre, descripción). |
| `label_max_candidates` | `int 1..32` | `8` | Posiciones de etiqueta a probar por componente (N/E/S/O…). |
| `respect_locked` | `bool` | `true` | **Modo híbrido**: los elementos con `locked: true` no se mueven. |
| `column_gap` | `float ≥ 0` | `70` | Separación horizontal entre columnas del auto-layout (px). Se comprime si no caben. |
| `row_gap` | `float ≥ 0` | `35` | Separación vertical entre elementos de una columna (px). |
| `clearance` | `float ≥ 0` | `18` | Holgura mínima alrededor de cada símbolo **al reubicar** (px). |
| `route_clearance` | `float ≥ 0` | `6` | Holgura alrededor de cada símbolo **al trazar cables** (px). |
| `route_manhattan` | `bool` | `true` | Calcula rutas ortogonales con A*. |
| `turn_penalty` | `float ≥ 0` | `20` | Penalización por giro (px equivalentes). |
| `crossing_penalty` | `float ≥ 0` | `40` | Penalización por cruzar otro conductor. |
| `max_search_nodes` | `int ≥ 100` | `60000` | Límite de nodos explorados por el router (protección contra runaway). |

### 3.1 Por qué `clearance` y `route_clearance` son distintos

Son dos holguras con propósitos distintos y **no deben igualarse**:

| | `clearance` (18 px) | `route_clearance` (6 px) |
|---|---|---|
| Se aplica… | al **reubicar** símbolos | al **trazar cables** |
| Evita… | que dos símbolos se pisen | que un cable atraviese un símbolo |
| Por qué no más | — | si fuera igual a `clearance`, la holgura **engullía la terminal** y el cable no tenía por dónde salir (fallo real detectado en el folio D-008) |

### 3.2 Modo híbrido (`locked: true`)

El elemento con `locked: true` es **intocable**: ni el *snap*, ni el
auto-layout, ni el router recalculan su posición. Es la decisión del
ingeniero sobre el plano.

```jsonc
{ "id": "Q1", "type": "circuit_breaker_2p", "x": 200, "y": 150,
  "locked": true }        // el auto-layout no lo mueve
```

Para desactivarlo: `--ignore-locked` en la CLI, o `ignorar_bloqueados: true`
en la herramienta MCP `ejecutar_auto_layout`.

### 3.3 Cómo el auto-layout decide las columnas

1. Agrupa los elementos en **capas** según el grafo de conexiones.
2. Mide el ancho de la caja **rotada** de cada símbolo (el *hotspot* no es el
   centro del símbolo).
3. Si las columnas no caben con `column_gap`, **comprime el hueco** (nunca saca
   un símbolo del folio).
4. Coloca cada capa en su columna, alineada a la rejilla y acotada al folio
   (el ajuste se hace sobre los múltiplos de la rejilla que caben).
5. Si una capa llena la columna, **envuelve** a una columna nueva a la derecha.

---

## 4. `typography` — Tipografía

| Clave | Tipo | Por defecto | Qué hace |
|---|---|---|---|
| `font_family` | `str` | `Sans Serif` | Familia tipográfica de los textos del folio. |
| `default_size` | `int ≥ 1` | `9` | Tamaño por defecto (pt). |
| `min_size` | `int ≥ 1` | `5` | Tamaño mínimo admitido (pt). |
| `max_size` | `int ≥ 1` | `24` | Tamaño máximo admitido (pt). |
| `char_width_ratio` | `float > 0` | `0.58` | Ancho medio de carácter como fracción del tamaño de fuente. |
| `line_height_ratio` | `float > 0` | `1.25` | Alto de línea como fracción del tamaño de fuente. |
| `px_per_pt` | `float > 0` | `1.3333333…` | Píxeles por punto tipográfico (96 dpi = 4/3). |

La métrica estimada es:

```
ancho ≈ caracteres × tamaño × char_width_ratio × px_per_pt
alto  ≈ líneas     × tamaño × line_height_ratio × px_per_pt
```

**Calibración:** contrastada contra los 416 textos reales de los 22 proyectos
de ejemplo de QElectroTech 0.100.0, solo el **2,40 %** se saldría del borde
con esta estimación (9 de esos 10 en 36 px o menos). No es un motor de
tipografía: es una **estimación reproducible** para decidir colisiones y
desbordes.

---

## 5. `styles` — Colores y estilos de bloques

| Clave | Tipo | Por defecto | Qué aplica |
|---|---|---|---|
| `block_color` | `str` | `#1f4e79` | Color de línea de los bloques funcionales. |
| `block_fill` | `str` | `#e8f0f8` | Color de relleno de los bloques. |
| `block_width` | `float > 0` | `1.5` | Grosor de línea de los bloques. |
| `table_color` | `str` | `#7f7f7f` | Color de las tablas. |
| `warning_color` | `str` | `#b26a00` | Color de los avisos (previsualización SVG). |
| `error_color` | `str` | `#c0392b` | Color de los errores (previsualización SVG). |
| `wire_color` | `str` | `#000000` | Color de los conductores (previsualización SVG). |
| `background` | `str` | `#ffffff` | Fondo del lienzo en la previsualización SVG. |

> Los colores de la previsualización **no** se escriben en el `.qet`: QET
> guarda el color de cada símbolo en su propio `.elmt`. Esta sección afecta
> al SVG y a los informes.

---

## 6. `sources` — Rutas de las fuentes externas

| Clave | Tipo | Por defecto | Qué apunta |
|---|---|---|---|
| `library_path` | `str` | `C:\Program Files\QElectroTech\elements` | Biblioteca de elementos (`.elmt`) de QElectroTech. |
| `catalog_path` | `str` | `resources/symbol_catalog.json` | Catálogo lógico → `.elmt` real. |

Si QElectroTech está instalado en otra ruta:

```yaml
sources:
  library_path: "D:/Program Files/QElectroTech/elements"
```

Comprueba que la ruta es correcta con:

```bash
qetgen doctor
# [OK   ] qet_library  C:\Program Files\QElectroTech\elements — 8597 archivo(s) .elmt
```

---

## 7. Errores frecuentes

| Mensaje | Causa | Solución |
|---|---|---|
| `configuración inválida → sheet.format: … formato de hoja desconocido` | nombre de preset mal escrito | usa uno de los 9 presets de la tabla §2.1 |
| `configuración inválida → sheet.clave_inventada: Extra inputs are not permitted` | clave que no existe (typo) | el nombre de la clave es incorrecto: `extra="forbid"` es intencionado |
| `configuración inválida → layout.grid_size: Input should be greater than 0` | valor fuera de rango | `grid_size` debe ser > 0 |
| `No existe el archivo de configuración: …` | ruta equivocada | `qetgen doctor` muestra la ruta por defecto que está usando |
| `PyYAML no está instalado` | YAML sin la dependencia | `pip install PyYAML` o usa un `.json` |

> La consola de Windows usa `cp1252` por defecto: si ves `UnicodeEncodeError`
> al imprimir textos con `→` o `—`, usa `python -X utf8` y
> `$env:PYTHONIOENCODING="utf-8"`.

---

## 8. Referencia rápida

```yaml
# config/mi_proyecto.yaml
sheet:
  format: A3_18x9        # folio más grande
  margin: 12             # más aire en los bordes
  edge_tolerance: 24     # más estricto con los textos
layout:
  grid_size: 20          # rejilla más gruesa
  snap_to_grid: false    # no alinear (dibujo manual)
  respect_locked: true   # modo híbrido (el ingeniero manda)
  column_gap: 90
  route_clearance: 4     # cables más ceñidos a los símbolos
typography:
  default_size: 10
  char_width_ratio: 0.62 # texto más ancho (fuente distinta)
sources:
  library_path: "D:/Program Files/QElectroTech/elements"
```

```bash
qetgen layout examples/proyecto_fv_588.json --config config/mi_proyecto.yaml --check
```

---

## 9. Referencias relacionadas

- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — cómo se organiza el código por capas.
- [`docs/QET_FORMAT_NOTES.md`](QET_FORMAT_NOTES.md) — el formato `.qet` con
  evidencia (CONFIRMADO / INFERIDO) y la geometría del folio (§12).
- [`docs/MCP.md`](MCP.md) — el servidor MCP y cómo consume la misma
  configuración.
- [`tools/measure_sheet_geometry.py`](../tools/measure_sheet_geometry.py) — la
  sonda que reproduce las cifras de §2.2.
