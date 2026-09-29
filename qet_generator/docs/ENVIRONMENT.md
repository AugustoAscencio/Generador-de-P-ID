# FASE 0 — Informe del entorno

> Inspección realizada el 2026-09-28 por el agente de desarrollo.
> Todos los datos de este documento fueron **verificados directamente en el equipo**, no inferidos.

## 1. Sistema operativo

| Campo | Valor |
|---|---|
| SO | Windows 11 (kernel 10.0.26200, `winnt`) |
| Arquitectura | x86_64 |
| Shell disponible | PowerShell 5.1 (parámetros modernos como `-AsByteStream` no disponibles) |
| Idioma del sistema | Español (`es_ES`) — QElectroTech se ejecuta en español |
| RAM total / disponible | 11 GB / ~1 GB disponible en el momento del arranque de QET |

## 2. QElectroTech instalado

| Campo | Valor |
|---|---|
| Versión | **0.100.0** (verificada con `qelectrotech.exe --version` y con el log de la aplicación) |
| Compilación | GCC 14.3.0, Qt 5.15.18, x86_64, construida el 25-01-2026 |
| Ejecutable | `C:\Program Files\QElectroTech\bin\qelectrotech.exe` |
| ¿Arranca correctamente? | Sí. Log del propio QET fechado HOY (2026-09-28 10:41) registra un arranque sin errores |
| Directorio de instalación | `C:\Program Files\QElectroTech\` |
| Biblioteca de elementos común | `C:\Program Files\QElectroTech\elements\` (colecciones: `10_electric`, `20_logic`, `30_hydraulic`, `50_pneumatic`, `60_energy`) |
| Elementos personalizados del usuario | `C:\Users\Augusto Ascencio\AppData\Roaming\QElectroTech\QElectroTech\elements\` |
| Plantillas de cartucho comunes | `C:\Program Files\QElectroTech\titleblocks\` |
| Configuración / logs de usuario | `C:\Users\Augusto Ascencio\AppData\Roaming\QElectroTech\QElectroTech\` |

### Archivos de proyecto de ejemplo incluidos (evidencia del formato real)

La instalación incluye proyectos `.qet` reales en `C:\Program Files\QElectroTech\examples\`,
generados por la propia aplicación, entre otros:

- `741.qet`, `photovoltaique.qet` (ejemplo fotovoltaico), `industrial.qet`,
  `schema_unifilaire_voltaique2.qet`, `Habitat-Schemas_developpes.qet`, etc.

**Estos ejemplos son evidencia directa del formato XML escrito por la versión 0.100.0**
y se usarán en la FASE 2 como material de análisis complementario al proyecto manual
que creará el usuario en la FASE 1.

## 3. Python

| Campo | Valor |
|---|---|
| `python` | Python 3.13.7 (interprete por defecto) |
| `py` | Python 3.13.7 (también 3.11.9 registrado como alternativa) |

## 4. Herramientas para inspección XML

- **Python 3.13.7 con biblioteca estándar**: `xml.etree.ElementTree` (lectura/escritura XML),
  `json` (lectura del modelo), `zipfile` (por si algún `.qet` resultara comprimido).
- No se necesita instalar software adicional en esta fase. Si en el futuro se requiere
  una librería de terceros (p. ej. `jsonschema` para validación del JSON), se justificará antes.

## 4b. Límites de la CLI de QElectroTech (verificado 2026-09-28)

`qelectrotech.exe --help` solo ofrece: `--version`, `--license`,
`--common-elements-dir`, `--common-tbt-dir`, `--config-dir`, `--data-dir`,
`--lang-dir`. **No hay modo headless ni conversiones por lotes**: la única forma de
verificar que un proyecto abre correctamente es abrirlo en la interfaz (el usuario
hace doble clic). No perder tiempo buscando automatización CLI: no existe.

## 5. Hallazgo clave sobre el formato `.qet`

Verificado sobre `examples\741.qet`:

- Los archivos `.qet` de esta versión son **XML plano UTF-8, sin comprimir**
  (el archivo comienza con `<project title="..." version="0.90">`).
- El atributo `version="0.90"` aparece en el ejemplo analizado; el proyecto manual de la
  FASE 1 confirmará qué valor escribe exactamente la versión 0.100.0.

## 6. Ubicación de trabajo acordada

- Espacio de trabajo: `C:\Users\Augusto Ascencio\Downloads\QElectroTech\`
- Proyectos de referencia manuales: `evidencia\manual\`
- Generador (fases 3+): `qet_generator\`
- Salidas del generador: `qet_generator\output\`

## 7. Símbolos FV localizados en la biblioteca (preliminar)

- `elements\10_electric\10_allpole\392_generators_sources\10_generators\pvcell.elmt`
  (celda fotovoltaica) — confirmado que existe; su análisis completo corresponde a la FASE 7.
- El ejemplo `photovoltaique.qet` probablemente referencia más símbolos FV usados por
  los propios desarrolladores de QET; se analizará en la FASE 2.
