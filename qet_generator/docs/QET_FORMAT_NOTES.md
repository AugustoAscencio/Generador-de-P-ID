# QET_FORMAT_NOTES.md — El formato `.qet` tal como lo escribe QElectroTech 0.100.0

> **Metodología:** todo lo marcado como **[CONFIRMADO]** fue verificado directamente en
> archivos reales generados por la versión **0.100.0** instalada en este equipo
> (`photovoltaique.qet` y `schema_unifilaire_voltaique2.qet`, ambos con
> `<project version="0.100.0">`, más `.elmt` de la biblioteca instalada).
> Lo marcado como **[INFERIDO]** es razonable pero aún sin confirmación experimental.
> **Nada de este documento es suposición presentada como hecho.**

## 1. Estructura general del proyecto

Un `.qet` es **XML plano UTF-8, sin declaración XML ni BOM** [CONFIRMADO: los primeros
bytes de `photovoltaique.qet` son `3C 70 72 6F 6A 65 63 74` = `<project`].

```
<project title="..." version="0.100.0">
  ├─ <properties>                      (metadatos de guardado; QET los reescribe)
  ├─ <newdiagrams>                     (valores por defecto para folios nuevos)
  │    ├─ <border .../>
  │    ├─ <inset .../>
  │    ├─ <conductors .../>
  │    ├─ <report .../>
  │    ├─ <xrefs><xref .../></xrefs>
  │    ├─ <conductors_autonums .../>
  │    ├─ <folio_autonums/>
  │    └─ <element_autonums .../>
  ├─ <diagram ...>                      (un folio; puede haber varios)
  │    ├─ <properties>                  (visibilidad de campos del cartucho)
  │    ├─ <defaultconductor .../>
  │    ├─ <elements>                    (contenedor de elementos)
  │    │    └─ <element .../> × N
  │    ├─ <conductors>                  (contenedor de conductores)
  │    │    └─ <conductor .../> × M
  │    ├─ <inputs>                      (textos independientes del folio)
  │    │    └─ <input .../> × T
  │    └─ <shapes/>                      (formas dibujadas: rect, ellipse, etc.)
  └─ <collection>                       (biblioteca embebida en el proyecto)
       └─ <category name="import">
            └─ ... categorías anidadas según la ruta ...
                 └─ <element name="xxx.elmt">
                      └─ <definition ...>  (copia del .elmt real)
```

## 2. Referencia a símbolos `.elmt` — mecanismo `embed://` [CONFIRMADO]

- **Ninguno** de los 23 ejemplos instalados referencia símbolos por ruta de la biblioteca:
  o bien embeben la definición (`type="embed://import/..."`) o son herencia antigua.
- El `type` del elemento apunta a la colección embebida:
  `type="embed://import/10_electric/10_allpole/.../parafoudre.elmt"` se resuelve como:
  `<collection><category name="import"><category name="10_electric"><category name="10_allpole">…<element name="parafoudre.elmt"><definition>…`
- El `<definition>` embebido es una **copia exacta del archivo `.elmt`** (con su `<uuid>` propio).
- **Decisión del generador:** embeber las definiciones tomadas literalmente de la
  biblioteca instalada (`C:\Program Files\QElectroTech\elements\...`) y referenciarlas
  con `embed://`. Ventajas: 100 % evidencial, portable, y usa los símbolos reales instalados.

## 3. Elemento colocado (`<element>` dentro de `<elements>`) [CONFIRMADO]

Atributos presentes en **63/63** elementos reales de la versión 0.100.0
(→ los 9 se consideran obligatorios para nuestra generación):

| Atributo | Ejemplo | Nota |
|---|---|---|
| `uuid` | `{fb0256f2-e197-4fe8-8b0f-1883b66e6912}` | UUIDv4 entre llaves, único por instancia |
| `orientation` | `0` | rotación del elemento (0 = sin rotar) |
| `type` | `embed://import/....elmt` | referencia a la colección embebida |
| `x`, `y` | `330`, `260` | posición del *hotspot* del elemento en el folio |
| `z` | `10` | capa/orden Z |
| `freezeLabel` | `false` | congela la etiqueta frente a autonumeración |
| `prefix` | `F` | prefijo para autonumeración |
| `name` | en 0.100.0 solo aparece en wrappers embebidos | no escribirlo en instancias |

Hijos (en este orden observado):

```xml
<terminals>
  <terminal id="0" orientation="0" x="0" y="-17"
            uuid="{f11be9a0-479e-49ab-b234-86c4d6dc44f9}"
            type="Generic" name="" number="" nameHidden="0"/>
</terminals>
<inputs/>
<elementInformations>
  <elementInformation show="1" name="location"/>
  <elementInformation show="1" name="comment"/>
  <elementInformation show="1" name="formula"/>
  <elementInformation show="1" name="label">F1</elementInformation>
</elementInformations>
<dynamic_texts>
  <dynamic_elmt_text frame="false" uuid="{...}" Halignment="AlignLeft"
      Valignment="AlignTop" rotation="0" text_from="ElementInfo"
      x="-20" font="Sans Serif,9,-1,5,0,0,0,0,0,0,normal" text_width="-1"
      keep_visual_rotation="true" y="10">
    <text/>
    <info_name>label</info_name>
  </dynamic_elmt_text>
</dynamic_texts>
<texts_groups/>
```

Puntos críticos confirmados:

- **El texto de la etiqueta** va como **contenido de texto** de
  `<elementInformation name="label">` (visto: `Panneau PV`, `Q7 32A`, `SHDM2`).
- **Los UUID de terminal se copian de la definición `.elmt`**: la terminal
  `{f11be9a0-…}` del `disjonct-m.elmt` embebido es la misma UUID que aparece en el
  elemento colocado. La identidad de una terminal ES su UUID de definición.
- **Los `id` de terminal son únicos en todo el diagrama** (171 terminales, 0 duplicados,
  max=170) → el generador debe usar un contador global por folio.
- La orientación de terminal en el elemento colocado va **numérica**:
  `n→0`, `s→2` [CONFIRMADO]; `e→1`, `w→3` [INFERIDO de la convención QET, pendiente
  de ver un símbolo e/w real guardado por QET].
- El `x`/`y` de `<dynamic_elmt_text` es la posición de la etiqueta relativa al
  hotspot (por defecto, la del `dynamic_text` del `.elmt`); su `uuid` es **nuevo**
  por instancia (no se hereda del `.elmt`).
- Metadatos disponibles (útiles para BOM futuro) [CONFIRMADO]: `label`, `comment`,
  `location`, `formula`, `designation`, `description`, `manufacturer`,
  `manufacturer_reference`, `machine_manufacturer_reference`, `supplier`, `plant`,
  `unity`, `quantity`.

## 4. Conductor (`<conductor>` dentro de `<conductors>`) [CONFIRMADO]

Hay DOS estilos en los archivos reales:

- **Numérico heredado** (`terminal1="118"`): terminales referenciadas por su `id`
  global. Proviene de archivos antiguos actualizados por versiones nuevas.
- **UUID moderno** (el que usamos): atributos `element1`/`element2` (uuid de cada
  instancia) + `terminal1`/`terminal2` (uuid de cada terminal). **[CONFIRMADO]**

Atributos escritos por el generador (set observado, sin personalizaciones de color):

```xml
<conductor dash-size="2" x="0" bus="" color2="#000000" text_color="#000000"
  terminal2="{uuid-term-2}" element2="{uuid-elem-2}" bicolor="false"
  horizrotatetext="0" type="multi" num="" displaytext="1"
  element1="{uuid-elem-1}" y="0" conductor_color="" conductor_section=""
  terminal1="{uuid-term-1}" formula="" numsize="7"
  horizontal-alignment="AlignBottom" onetextperfolio="0" function=""
  freezeLabel="false" vertirotatetext="270" tension_protocol="" condsize="1"
  cable="" vertical-alignment="AlignRight">
  <sequentialNumbers/>
</conductor>
```

- `type="multi"` es el estilo de conductor por defecto observado.
- `x`/`y` = posición del texto del conductor (0/0 = sin mover por el usuario).
- `userx`/`usery`, `color`, `style`, `rotation` solo aparecen si el usuario los cambia
  [CONFIRMADO por estadística de presencia].
- QET **recalcula la ruta** del conductor entre las dos terminales: no hace falta
  generar geometría de trazo (los `<segment>` son solo caché de render del último guardado).

## 5. Folio (`<diagram>`) [CONFIRMADO]

Atributos observados (todos presentes en los archivos 0.100.0): `title, author, version,
date, order, cols, rows, colsize, rowsize, height, displaycols, displayrows, displayAt,
folio, auto_page_num, indexrev, locmach, plant, filename, freezeNewConductor,
freezeNewElement`.

- Dimensiones por defecto: `cols=17`, `rows=8`, `colsize=60`, `rowsize=80`,
  `height=660`, `folio="%id/%total"`, `displayAt="bottom"`, `order` = número de folio.
- `date` en formato `AAAAMMDD` (ej. `20221023`).
- `version` del diagrama: `0.100.0-dev` en los ejemplos (compilación de desarrollo).
  El generador escribe `0.100.0`; el re-guardado del usuario nos dará el valor exacto
  de la build instalada [PENDIENTE].

## 6. Textos independientes (`<input>` dentro de `<inputs>`) [CONFIRMADO]

```xml
<input rotation="0" x="698.385" font="Sans Serif,9,-1,5,0,0,0,0,0,0,normal"
  text="<!DOCTYPE HTML PUBLIC …/html>…<p …>TEXTO</p>…"
  y="536.948" tagg="label" size="9" rotate="true"/>
```

- El texto va **envuelto en HTML richtext de Qt** (plantilla QTextDocument).
- Font en formato `QFont::toString()` de Qt.

## 7. Posiciones

- Origen del folio: esquina superior izquierda del área de dibujo; el cartucho
  (`displayAt="bottom"`) ocupa la franja inferior (evitar y > ~560 para no tapar).
- `x`/`y` de un elemento = posición de su **hotspot** (definido en el `.elmt` por
  `hotspot_x`/`hotspot_y`); las terminales se expresan **relativas al hotspot**.
- Área útil con 17×60 = 1020 px de ancho y 8×80 = 640 px de alto [CONFIRMADO].

## 8. Colección embebida (`<collection>`) [CONFIRMADO]

```
<collection>
  <category name="import">                       ← raíz de la colección
    <category name="10_electric">                ← anidada según ruta
      …
      <element name="parafoudre.elmt">
        <definition …> …copia exacta del .elmt… </definition>
      </element>
```

- El mapeo `embed://import/A/B/x.elmt` ↔ categorías `import/A/B` + `<element name="x.elmt">`
  está confirmado con múltiples ejemplos (incluido el caso curioso de doble `import/import`
  que existe en `photovoltaique.qet`).
- Cada símbolo usado se embebe **una sola vez** aunque haya N instancias.

## 9. Qué generamos automáticamente / qué falta conocer

**Generamos con evidencia completa:** proyecto, folio con cartucho, elementos (posición,
etiqueta, terminales con uuid), conductores uuid-uuid, textos independientes, colección
embebida desde la biblioteca instalada.

### 9b. VALIDACIÓN POR RE-GUARDADO REAL (FASE 6) — 2026-09-28

El usuario abrió en QET 0.100.0 el proyecto generado, **movió un elemento y guardó**.
Comparación del archivo re-guardado contra el generado:

**Confirmado por QET (nuestro formato fue 100 % entendido):**
1. `version="0.100.0"` es correcta para `<project>` Y para `<diagram>` [CONFIRMADO].
2. Los UUID de instancia se conservan (QET reutilizó los nuestros).
3. Las etiquetas `elementInformation name="label"` con texto se conservan tal cual.
4. Los conductores con `element1/element2/terminal1/terminal2` (uuid) funcionan.
5. Los IDs de terminal son GLOBALES por folio: QET reescribió 0..5 igual que nosotros.
6. La colección embebida se acepta y se re-guarda con nuestra misma estructura.
7. `text_from="ElementInfo"` + `info_name="label"` + posición x/y: aceptado
   (QET regeneró el uuid del dynamic_elmt_text al guardar — no es problemático).

**Aprendizajes del re-guardado (cosmética, no requiere cambios):**
- QET reescribe los atributos en otro orden (irrelevante para XML).
- Al re-guardar, las terminales colocadas se simplifican a `id/x/y/orientation`
  (los uuid de terminal se resuelven contra la definición embebida, no contra la lista).
- QET recalcula la posición de acople de terminales (p. ej. −20 → −16 en el motor).
- `<shapes>` vacío se OMITE; `location/comment/formula` vacíos se omiten → opcionales.
- QET añade en cada conductor cachés de visualización: `element1_name`,
  `element2_name`, `element1_label`, `element2_label`, `terminalname1/2` — opcionales.
- `inset` de newdiagrams usa literal `date="null"` cuando está vacío.

**Aún pendiente de confirmación (solo si llega a ser necesario):**
1. Orientación numérica de terminales `e`/`w` en la lista colocada (QET la recalcula;
   el ejercicio real con pv_cell lo validará visualmente).
2. Folios múltiples (`order`, autonumeración) — se necesitará al escalar a 588 módulos.
3. Referencias cruzadas (`xref`), `report` entre folios, titleblocks personalizados.
4. Terminales con `type` distinto de `Generic` (tierra, etc.).

## 10. Ejemplos de referencia permanentes

- `C:\Program Files\QElectroTech\examples\photovoltaique.qet` (0.100.0, fotovoltaico, 196 elementos)
- `C:\Program Files\QElectroTech\examples\schema_unifilaire_voltaique2.qet` (0.100.0)
- `C:\Program Files\QElectroTech\examples\ShellyParts.qet` (0.90, etiquetas visibles)
- `C:\Program Files\QElectroTech\elements\**\*.elmt` (símbolos reales instalados)

## 11. Multi-folio [CONFIRMADO — 2026-09-29]

Análisis de proyectos reales multi-folio (`industrial.qet` 50 folios,
`affuteuse_250h.qet` 12, `iso_sfc_example.qet` 2, `ShellyParts.qet` 3,
`tableau_domestique.qet` 5):

- Los folios son **varios `<diagram>` hermanos** dentro de `<project>`,
  cada uno con sus `properties/defaultconductor/elements/conductors/inputs/shapes`.
- `order` es secuencial: 1, 2, 3, … N [CONFIRMADO en todos los archivos].
- **Los IDs de terminal son GLOBALES POR FOLIO**: cada folio reinicia en 0
  (ej.: folio 1 → 0..65; folio 2 → 0..53; sin duplicados dentro del folio,
  pero SÍ se repiten entre folios). Evidencia: 22 folios analizados.
- La `<collection>` embebida es **UNA por proyecto**, compartida por todos
  los folios (los `embed://` de cualquier folio apuntan a ella).
- `folio_autonums` / `element_autonums` / `conductors_autonums` siguen a nivel
  de proyecto (en `<newdiagrams>`), no por folio.
- Los UUID de instancia de elemento deben ser únicos en todo el proyecto
  (los conductores los referencian; un uuid duplicado rompería el enlace).

---
*Documento generado en la FASE 2 a partir de evidencia experimental. Actualizar cuando
la FASE 6 (re-guardado por QET) aporte nuevos datos.*
