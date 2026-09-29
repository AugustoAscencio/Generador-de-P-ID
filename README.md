# Generador de P&ID y Planos de Ingeniería — QElectroTech

> **De especificación estructurada (JSON) a planos eléctricos profesionales, editables y trazables — automáticamente.**
>
> Demostrado en un caso real: la documentación eléctrica completa de un sistema
> fotovoltaico de **588 módulos × 8 paneles** con seguimiento solar biaxial
> (18 planos industriales generados, validados y editables en QElectroTech).

---

## ¿Qué es este proyecto?

Una **herramienta de ingeniería documental** que convierte especificaciones
técnicas en **proyectos QElectroTech (.qet) reales**: diagramas, símbolos
normalizados, conexiones entre terminales, referencias, textos, bloques
funcionales, borneras y metadatos BOM. El resultado no es un dibujo
"parecido": es un **proyecto nativo de QElectroTech 0.100.0** que se abre,
se edita y se re-guarda en la aplicación sin pérdidas.

```
ESPECIFICACIÓN (JSON)  →  GENERADOR PYTHON  →  PROYECTO .QET  →  QElectroTech (editable)  →  PDF
```

## El método: ingeniería inversa con evidencia

El punto diferencial de esta herramienta es que **nada del formato interno se
inventó**. El formato `.qet` fue descifrado analizando archivos reales
producidos por la versión instalada de QElectroTech:

1. Se censaron los 23 proyectos de ejemplo de la instalación (2 de ellos
   guardados por la misma versión 0.100.0) con herramientas de análisis propias.
2. Se documentó el formato etiqueta por etiqueta, marcando **CONFIRMADO vs
   INFERIDO** (`qet_generator/docs/QET_FORMAT_NOTES.md`, 11 secciones).
3. Se validó con **round-trip**: el proyecto generado se abrió y re-guardó
   en QElectroTech; el diff confirmó que la aplicación entendió el 100 %
   de UUIDs, terminales, conductores, etiquetas y colección embebida
   (evidencia preservada en `evidencia/roundtrip/`).

## Caso de éxito incluido: proyecto FV 588 módulos

| Entregable | Contenido |
|---|---|
| `entregables/Proyecto_FV_588_Modulos.qet` | **18 planos** (D-001…D-018): arquitectura, string FV, protección DC, 24 VDC, ejes elevación/azimut, sensores, viento/STOW, mapa E/S, estados, enclavamientos, comunicaciones RS485/IoT, tierra TT, canalizaciones, borneras, interfaz de planta y módulo tipo × 588 |
| `entregables/MEMORIA_TECNICA_FV_588.docx` | Memoria técnica con todos los cálculos (string 332,8 V / 20,55 A, protecciones, tierra, CIRSOC, FEM) |
| `qet_generator/` | El generador completo: 55 tests, 14 símbolos reales de biblioteca, plantillas paramétricas de hojas |

**Filosofía de escalado:** MÓDULO TIPO × 588 — la ingeniería repetitiva se
documenta una sola vez y se escala mediante arquitectura de repetición
(nunca 588 dibujos duplicados).

## Arquitectura del generador

```
qet_generator/
├── main.py               CLI: python main.py entrada.json [-o salida.qet]
├── generator/
│   ├── model.py          JSON → modelo (mono y multi-folio, shapes, BOM)
│   ├── validate.py       validación previa (IDs, conexiones, terminales…)
│   ├── builders.py       plantillas paramétricas (create_pv_string, ejes…)
│   ├── sheets.py         los 18 planos del caso FV (regenerables)
│   ├── project.py        ensamblado <project> + colección embebida + export
│   ├── diagram.py        folios <diagram> (IDs de terminal globales/folio)
│   ├── elements.py       catálogo de símbolos + elementos (terminales, labels)
│   ├── conductors.py     conductores estilo UUID moderno
│   ├── text.py           textos independientes (HTML richtext de Qt)
│   └── shapes.py         bloques funcionales <shape> (rectángulos)
├── templates/symbol_catalog.json   tipo lógico → .elmt real de la biblioteca
├── examples/                       JSONs de los proyectos (basic, pv_8, fv_588)
├── output/                         .qet generados
├── tests/                          55 tests (unittest, solo stdlib)
├── tools/                          análisis de evidencia + demos + md_to_docx
└── docs/                           formato .qet, arquitectura, entorno, inventario
```

## Uso en 3 comandos

```bash
cd qet_generator
python tools/build_sheets.py                                   # plantillas → JSON
python main.py examples/proyecto_fv_588.json -o ../entregables/Proyecto_FV_588_Modulos.qet
python -m unittest discover -s tests                           # 55 tests OK
```

Requisitos: Python 3.10+ (solo biblioteca estándar) y QElectroTech 0.100.0
instalado (los símbolos se leen de su biblioteca real).

## Calidad incluida

- **55 tests automáticos** (formato, validaciones, multi-folio, 18 planos).
- **Validación antes de generar**: IDs duplicados, conexiones inválidas,
  terminales fuera de rango, textos vacíos, coordenadas fuera de folio.
- **Trazabilidad total** en los planos: cada dato cita su fuente técnica;
  lo no confirmado se marca *PENDIENTE DE VERIFICACIÓN* — nunca se inventa.
- **Regenerable**: cualquier revisión de ingeniería actualiza los 18 planos
  en un solo paso (paramétrico, no dibujo manual).

## Para agentes de IA

- `AGENTS.md` — reglas, estado y hoja de ruta del proyecto.
- `SKILL.md` y `.opencode/skill/qet-generator/SKILL.md` — skill lista para
  que cualquier sesión de IA use la herramienta correctamente.

## Autoría y contexto

Proyecto personal de automatización de documentación de ingeniería.
Desarrollado con metodología de evidencia (ingeniería inversa del formato
real + validación por round-trip) y aplicado a un caso fotovoltaico real
de 588 módulos con seguimiento biaxial.
