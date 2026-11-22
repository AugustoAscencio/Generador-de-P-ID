# AGENTS.md — Instrucciones para agentes (IA) que trabajen en este workspace

> **Repositorio:** https://github.com/AugustoAscencio/Generador-de-P-ID
> **Paquete:** `qetgen` v1.0.0 · **Skill disponible:** `qet-generator`
> (`.opencode/skill/qet-generator/SKILL.md`) — se descubre automáticamente en
> opencode. **Úsala** para generar/modificar planos.
>
> **PROMPT DE ARRANQUE para una nueva sesión (cópialo y pégalo):**
> *"Estamos en el repo del Generador de P&ID (QElectroTech). Usa la skill
> qet-generator. Lee AGENTS.md y respeta sus reglas sin excepciones. La
> herramienta es `qetgen` (src/qetgen, CLI `python -m qetgen.cli`); los
> entregables del caso FV 588 están en entregables/ (18 planos .qet + memoria).
> Continúa desde «Próximos pasos» de AGENTS.md."*

## Qué es este proyecto

Motor **CAD/EDA** que genera proyectos **QElectroTech (.qet)** a partir de una
especificación JSON, para producir documentación eléctrica editable.
Caso de uso final: proyecto **fotovoltaico de 588 módulos × 8 paneles** con
seguimiento solar (DomBusTracker2, actuadores, sensores, RS485, USR-W610/DR404…).

Desde la v0.2.0 la herramienta vive en `src/qetgen/` (arquitectura por capas);
`qet_generator/` es una **fachada de compatibilidad** de la v0.1 (se elimina en
la v2.0).

## Reglas NO negociables

1. **Basado en evidencia.** Está PROHIBIDO inventar etiquetas/atributos XML del
   formato .qet. Ante cualquier duda: analizar archivos reales con las
   herramientas de `tools/` (inspect_qet.py, deep_qet.py) sobre
   `C:\Program Files\QElectroTech\examples\*.qet` (dos de ellos, `photovoltaique.qet`
   y `schema_unifilaire_voltaique2.qet`, son de la MISMA versión instalada 0.100.0)
   o sobre cualquier .qet guardado por el usuario. El formato documentado está en
   `docs/QET_FORMAT_NOTES.md` (marcado CONFIRMADO vs INFERIDO).
   *Dato clave verificado:* `<diagram>` **no** guarda `width` (0/129 folios);
   `height == rows × rowsize + 20` en 129/129.
2. **La ingeniería no la decide el agente** (jerarquía FASE 15):
   Documentación del cliente → Especificación técnica maestra → JSON → Generador → QET.
   El generador solo representa; nunca sustituye a la ingeniería.
3. **Discrepancia registrada del proyecto real (NO resolverla en silencio):**
   el cliente indica **588 módulos** de 8 paneles «650 kW» (texto del cliente);
   el documento técnico usa paneles de **625–650 Wp** y calcula ~**1539 módulos**
   para 8 MW. Requisito vigente para generar: **588 módulos**. Todo valor técnico
   del módulo debe salir del documento técnico o marcarse como SUPUESTO/PENDIENTE.
4. **No escalar a 588 módulos** hasta que las pruebas por fases pasen en QElectroTech
   (el usuario abre los archivos; el agente valida estructura por su cuenta).
5. Ante cambios de formato JSON o del generador: actualizar `docs/`, tests y
   explicar qué cambió y qué proyectos anteriores se ven afectados (FASE 16).
6. **Nada se inventa en el motor tampoco**: si una cifra no está medida
   (geometría de folio, métrica tipográfica, holguras), se calibra con una sonda
   reproducible (`tools/measure_sheet_geometry.py`) o se marca como estimación
   calibrada en la documentación.

## Estado actual (actualizar al avanzar)

### MISIÓN ACTIVA: documentación eléctrica de 18 planos (caso FV 588)

**Fuentes ÚNICAS de ingeniería** (regla del proyecto — no usar otras):
`fuentes/01_Sistema_Fotovoltaico_8paneles.md` (Doc1 = ingeniería
del módulo) y `fuentes/02_Referencia_TSC2_Avance.md` (Doc2 =
criterios generales; ⚠ describe un sistema agrivoltaico 500 kWp DISTINTO — sus valores
no se aplican al módulo). Requisito vigente: **588 módulos × 8 paneles**; potencia en
esquemas = **650 Wp** (nunca "650 kW"; discrepancia registrada).

**Matriz de ingeniería extraída:** `docs/SPEC_INVENTARIO.md`
(componentes, señales, protecciones, interfaces, discrepancias, estructura 18 hojas,
todo con cita de fuente Doc1 §x).

**Arquitectura del entregable:** MÓDULO TIPO (D-002…D-016) + arquitectura de repetición
(D-001, D-017, D-018). Nunca 588 dibujos. Cada hoja se define en
`src/qetgen/sheets/fv588/` (build_dXXX) → `examples/proyecto_fv_588.json` →
`qetgen fv588` genera el .qet ÚNICO del proyecto.

- ✅ ETAPA A/B/C: documentos leídos; inventario + nomenclatura + discrepancias hechos.
- ✅ **LOS 18 PLANOS GENERADOS** en `output/Proyecto_FV_588_Modulos.qet`
  (D-001…D-018, 111 elementos, 60 conductores, 412 textos, ~130 bloques; 628 KB).
  D-002/D-003 validados visualmente por el usuario; D-001 y D-004…D-018 generados
  bajo las mismas reglas (**pendiente revisión visual**).
- ✅ Catálogo de **14 símbolos reales** de la biblioteca (incl. disyuntor bipolar
  4 terminales, SPD, tierra, motor DC, condensador, sensor NPN 3 cables,
  pulsador, selector).
- ✅ Hojas D-006/D-007 paramétricas (`_axis_sheet`) — plantilla de eje reutilizable.
- ⚠ Marcas "PENDIENTE DE VERIFICACIÓN" en los planos (regla de trazabilidad):
  Q0.4/Q0.5 no físicas, numeración de bornes, internos del SPD, polaridad por
  terminal del panel, red de planta (fuera de alcance según Doc1).
- Documentación final en voz de proyecto: `PROYECTO_FV_588.md` (raíz).

### Base técnica: qetgen v1.0.0 (publicada en GitHub)

| Versión | Tag | Contenido |
|---|---|---|
| v0.1.0 | `v0.1.0` | Generador v0.1 (solo stdlib), 14 símbolos, 18 planos, 55 tests. |
| v0.2.0 | `v0.2.0` | Arquitectura por capas (`src/qetgen/`), Pydantic v2 estricto, CLI `qetgen`, E/S atómica, 116 tests. |
| v0.3.0 | `v0.3.0` | Motor geométrico: colisiones con cajas reales, routing Manhattan A\*, auto-layout, preview SVG, auditoría estética, config central, 174 tests. |
| v0.4.0 | `v0.4.0` | CLI profesional (`qetgen layout`, `qetgen doctor`), pipeline de layout compartido, 191 tests. |
| **v1.0.0** | `v1.0.0` | **Servidor MCP universal**, documentación completa (README, CONFIGURACION, MCP), LICENSE, CONTRIBUTING, CI. **221 tests.** |

- ✅ **Motor geométrico** (`src/qetgen/layout/`): rejilla, cajas reales rotadas,
  colisiones con criterio (containment ≠ overlap, salvo cajas idénticas),
  métrica tipográfica calibrada, routing Manhattan A\* con intersección exacta
  (Liang–Barsky), auto-layout híbrido con salto de columna.
- ✅ **Configuración central** (`config/default.yaml`, YAML o JSON, Pydantic
  estricto `extra="forbid"`) con test de sincronía con el código.
- ✅ **Validadores**: estructura (`validation/structural.py`) + estética
  (`validation/aesthetics.py`) con códigos estables y sugerencias accionables.
- ✅ **Servidor MCP universal** (`src/qetgen/mcp_server/`): 8 herramientas
  atómicas y tipadas, 4 recursos, 2 prompts; **SDK oficial** si está instalado y
  **fallback propio** (JSON-RPC 2.0) si no — interfaz idéntica.
- ✅ **CI** (`.github/workflows/ci.yml`): Python 3.10→3.13 en Ubuntu y Windows,
  `unittest` + `ruff`, empaquetado y verificación de enlaces de la documentación.
- ✅ **Round-trip** con QET 0.100.0 (evidencia en `evidencia/roundtrip/` y
  `docs/QET_FORMAT_NOTES.md` §9b).

### Defectos REALES detectados en el proyecto FV 588 (NO son fallos del motor)

El motor los **detecta y los reporta**; no hay que "arreglarlos" en el validador.

1. **8 textos desbordados** (`OUT_OF_SHEET`, error) — el texto se sale del folio
   por más de la tolerancia calibrada (36 px):
   D-006 texto[15], D-007 texto[15], D-008 texto[10]/[12]/[14]/[15],
   D-012 texto[13], D-017 texto[18].
2. **2 terminales reutilizadas** (aviso de estructura):
   `D005-FU[1]` (folio D-005) y `D009-XW[0]` (folio D-009) — cada una usada en
   2 conductores. **Requiere criterio de ingeniería**: puede ser intencionado
   (punto común) o un error. **No resolver en silencio.**
3. Avisos de legibilidad (textos/etiquetas que se pisan, cables que se cruzan o
   van demasiado juntos) y 1 info de cruce de bloque.

Comprobación reproducible:

```bash
python -m qetgen.cli doctor examples/proyecto_fv_588.json   # exit 1 (hay errores)
python -m qetgen.cli validate examples/proyecto_fv_588.json # 2 avisos
```

## Próximos pasos (hoja de ruta)

1. **Revisión visual del usuario de los 18 planos** (abrir
   `output/Proyecto_FV_588_Modulos.qet`; D-002/D-003 ya validados). Ajustes de
   posiciones/textos si se piden.
2. **Decidir los 8 textos desbordados**: moverlos o reducirlos en las hojas
   paramétricas de `src/qetgen/sheets/fv588/` (nunca a mano en el `.qet`).
3. **Decidir las 2 terminales reutilizadas** con criterio de ingeniería
   (Documento 1 → registro en `docs/SPEC_INVENTARIO.md`).
4. ETAPA N: revisión cruzada completa (consistencia de referencias entre hojas,
   checklist de la misión) — automatizable con un test de consistencia de señales.
5. Export a PDF por folio (función nativa de QET) cuando el usuario lo solicite.
6. Si se requiere escalar a dibujo de planta (colección DC, red de com de planta),
   pedir la ingeniería correspondiente: está declarada FUERA DE ALCANCE (D-017).

## Cómo trabajar aquí

```bash
# Instalar (una vez)
pip install -e ".[dev]"

# Diagnóstico del entorno (SIEMPRE al empezar)
python -m qetgen.cli doctor

# Generar / validar
python -m qetgen.cli build examples/NOMBRE.json -o salida.qet
python -m qetgen.cli validate examples/NOMBRE.json
python -m qetgen.cli fv588                      # regenera el paquete de 18 planos

# Motor de layout y auditoría
python -m qetgen.cli layout examples/NOMBRE.json --check
python -m qetgen.cli layout examples/NOMBRE.json --folio 3 --auto-layout
python -m qetgen.cli layout examples/NOMBRE.json --preview preview/

# Servidor MCP
python -m qetgen.cli serve [--fallback]

# Tests (SIEMPRE tras cualquier cambio)
python -m unittest discover -s tests            # 221 tests

# Análisis de evidencia del formato
python tools/inspect_qet.py <archivo.qet>        # censar estructura real
python tools/deep_qet.py <archivo.qet>           # análisis profundo
python tools/measure_sheet_geometry.py           # calibración del folio
```

Entorno (verificado): Windows 11, QElectroTech 0.100.0 en
`C:\Program Files\QElectroTech`, Python 3.13.7, PowerShell 5.1 (ojo: consola cp1252,
usar `python -X utf8` y `$env:PYTHONIOENCODING="utf-8"` para UTF-8 sin BOM).

## Archivos clave

| Ruta | Contenido |
|---|---|
| `SKILL.md` + `.opencode/skill/qet-generator/SKILL.md` | **Skill para IA** (cómo usar la herramienta; autodescubierta en opencode) |
| `README.md` | Presentación del proyecto (portfolio) |
| `CONTRIBUTING.md` | Cómo contribuir, ejecutar tests y publicar una versión |
| `CHANGELOG.md` | Historial por versión (Keep a Changelog / SemVer) |
| `src/qetgen/` | **La herramienta**: `core/`, `layout/`, `exporters/`, `validation/`, `cli/`, `mcp_server/`, `sheets/` |
| `qet_generator/` | Fachada de compatibilidad v0.1 (se elimina en la v2.0) |
| `config/default.yaml` | Configuración central (hoja, rejilla, tipografía, cableado, estilos) |
| `resources/symbol_catalog.json` | Símbolos disponibles (14) |
| `entregables/` | Caso FV 588: `Proyecto_FV_588_Modulos.qet` (18 planos) + memoria técnica (MD/Word) + doc del paquete |
| `fuentes/` | Documentación técnica fuente (Doc1/Doc2) — fuentes ÚNICAS de ingeniería |
| `evidencia/` | Round-trip con QET 0.100.0 (prueba del formato) + proyectos de referencia |
| `docs/QET_FORMAT_NOTES.md` | El formato .qet real (CONFIRMADO/INFERIDO) + §12 geometría del folio |
| `docs/ARCHITECTURE.md` | Arquitectura por capas y reglas de dependencia |
| `docs/CONFIGURACION.md` | Cada clave de configuración, con su calibración |
| `docs/MCP.md` | El servidor MCP: herramientas, recursos, prompts |
| `docs/SPEC_INVENTARIO.md` | Matriz de ingeniería del caso FV (trazabilidad Doc §x) |
| `tools/` | Análisis de evidencia, medición de geometría, `md_to_docx.py` |
| `.github/workflows/ci.yml` | CI: tests (3.10→3.13 × 2 SO), lint, empaquetado, enlaces |
