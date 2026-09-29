# AGENTS.md — Instrucciones para agentes (IA) que trabajen en este workspace

> **Repositorio:** https://github.com/AugustoAscencio/Generador-de-P-ID
> **Skill disponible:** `qet-generator` (`.opencode/skill/qet-generator/SKILL.md`) —
> se descubre automáticamente en opencode. **Úsala** para generar/modificar planos.
>
> **PROMPT DE ARRANQUE para una nueva sesión (cópialo y pégalo):**
> *"Estamos en el repo del Generador de P&ID (QElectroTech). Usa la skill
> qet-generator. Lee AGENTS.md y respeta sus reglas sin excepciones. Los
> entregables del caso FV 588 están en entregables/ (18 planos .qet + memoria).
> Continúa desde «Próximos pasos» de AGENTS.md."*

## Qué es este proyecto

Generador automático de proyectos **QElectroTech (.qet)** a partir de una
especificación JSON, para producir documentación eléctrica editable.
Caso de uso final: proyecto **fotovoltaico de 588 módulos × 8 paneles** con
seguimiento solar (DomBusTracker2, actuadores, sensores, RS485, USR-W610/DR404…).

## Reglas NO negociables

1. **Basado en evidencia.** Está PROHIBIDO inventar etiquetas/atributos XML del
   formato .qet. Ante cualquier duda: analizar archivos reales con las
   herramientas de `qet_generator/tools/` (inspect_qet.py, deep_qet.py) sobre
   `C:\Program Files\QElectroTech\examples\*.qet` (dos de ellos, `photovoltaique.qet`
   y `schema_unifilaire_voltaique2.qet`, son de la MISMA versión instalada 0.100.0)
   o sobre cualquier .qet guardado por el usuario. El formato documentado está en
   `qet_generator/docs/QET_FORMAT_NOTES.md` (marcado CONFIRMADO vs INFERIDO).
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

## Estado actual (actualizar al avanzar)

### MISIÓN ACTIVA (desde 2026-09-29): documentación eléctrica de 18 planos

**Fuentes ÚNICAS de ingeniería** (regla del proyecto — no usar otras):
`fuentes/01_Sistema_Fotovoltaico_8paneles.md` (Doc1 = ingeniería
del módulo) y `fuentes/02_Referencia_TSC2_Avance.md` (Doc2 =
criterios generales; ⚠ describe un sistema agrivoltaico 500 kWp DISTINTO — sus valores
no se aplican al módulo). Requisito vigente: **588 módulos × 8 paneles**; potencia en
esquemas = **650 Wp** (nunca "650 kW"; discrepancia registrada).

**Matriz de ingeniería extraída (ETAPA B/C):** `qet_generator/docs/SPEC_INVENTARIO.md`
(componentes, señales, protecciones, interfaces, discrepancias, estructura 18 hojas,
todo con cita de fuente Doc1 §x).

**Arquitectura del entregable:** MÓDULO TIPO (D-002…D-016) + arquitectura de repetición
(D-001, D-017, D-018). Nunca 588 dibujos. Cada hoja se define en
`generator/builders.py` (build_dXXX) → `tools/build_sheets.py` serializa a
`examples/proyecto_fv_588.json` → `main.py` genera el .qet ÚNICO del proyecto.

- ✅ ETAPA A/B/C: documentos leídos; inventario + nomenclatura + discrepancias hechos.
- ✅ **MISIÓN COMPLETA (2026-09-29): LOS 18 PLANOS GENERADOS** en
  `output/Proyecto_FV_588_Modulos.qet` (D-001…D-018, 111 elementos, 60 conductores,
  412 textos, ~130 bloques; 628 KB). D-002/D-003 validados visualmente por el usuario;
  D-001 y D-004…D-018 generados bajo las mismas reglas (pendiente revisión visual).
- ✅ Generador extendido: shapes/bloques `<shape>`, tamaño de texto `size`,
  validaciones; catálogo ampliado a **14 símbolos reales** de la biblioteca
  (incl. disyuntor bipolar 4 terminales, SPD, tierra, motor DC, condensador,
  sensor NPN 3 cables, pulsador, selector).
- ✅ Hojas D-006/D-007 paramétricas (`_axis_sheet`) — plantilla de eje reutilizable.
- Tests: **55 OK** (`python -m unittest discover -s tests`), incl. test integral
  de los 18 planos (`tests/test_sheets_all.py`).
- ⚠ Marcas "PENDIENTE DE VERIFICACIÓN" en los planos (regla de trazabilidad):
  Q0.4/Q0.5 no físicas, numeración de bornes, internos del SPD, polaridad por
  terminal del panel, red de planta (fuera de alcance según Doc1).
- Documentación final en voz de proyecto: `PROYECTO_FV_588.md` (raíz).

### Base técnica previa (validada)
- POC + FASE 8 + multi-folio + plantillas paramétricas: TODO validado por round-trip
  con QET 0.100.0 (evidencia en `evidencia/roundtrip/` y QET_FORMAT_NOTES §9b).
- Catálogo de símbolos: 6 tipos (ac_source, circuit_breaker_1p, motor_1p, pv_cell,
  lamp, dc_terminal). SPD (parafoudre.elmt) y tierra (terre.elmt) EXISTEN en la
  biblioteca — pendientes de añadir al catálogo para D-004/D-014.

## Próximos pasos (hoja de ruta de la misión activa)

1. **Revisión visual del usuario de los 18 planos** (abrir `Proyecto_FV_588_Modulos.qet`;
   D-002/D-003 ya validados). Ajustes de posiciones/textos si se piden.
2. ETAPA N: revisión cruzada completa (consistencia de referencias entre hojas,
   checklist de la misión) — automatizable con un test de consistencia de señales.
3. Export a PDF por folio (función nativa de QET) cuando el usuario lo solicite.
4. Si se requiere escalar a dibujo de planta (colección DC, red de com de planta),
   pedir la ingeniería correspondiente: está declarada FUERA DE ALCANCE (D-017).

## Cómo trabajar aquí

```bash
cd qet_generator
python main.py examples/NOMBRE.json [-o salida.qet]   # generar
python -m unittest discover -s tests                  # tests
python tools/inspect_qet.py <archivo.qet>             # censar estructura real
python tools/deep_qet.py <archivo.qet>                # análisis profundo
```

Entorno (verificado): Windows 11, QElectroTech 0.100.0 en
`C:\Program Files\QElectroTech`, Python 3.13.7, PowerShell 5.1 (ojo: consola cp1252,
usar herramientas Python para leer UTF-8; escribir JSON por consola con
UTF-8 sin BOM).

## Archivos clave

| Ruta | Contenido |
|---|---|
| `SKILL.md` + `.opencode/skill/qet-generator/SKILL.md` | **Skill para IA** (cómo usar la herramienta; autodescubierta en opencode) |
| `README.md` | Presentación del proyecto (portfolio) |
| `entregables/` | Caso FV 588: `Proyecto_FV_588_Modulos.qet` (18 planos) + memoria técnica (MD/Word) + doc del paquete |
| `fuentes/` | Documentación técnica fuente (Doc1/Doc2) — fuentes ÚNICAS de ingeniería |
| `evidencia/` | Round-trip con QET 0.100.0 (prueba del formato) + proyectos de referencia |
| `qet_generator/docs/QET_FORMAT_NOTES.md` | El formato .qet real (CONFIRMADO/INFERIDO) |
| `qet_generator/docs/ARCHITECTURE.md` | Arquitectura del generador |
| `qet_generator/docs/ENVIRONMENT.md` | Informe del entorno (FASE 0) |
| `qet_generator/docs/SPEC_INVENTARIO.md` | Matriz de ingeniería del caso FV (trazabilidad Doc §x) |
| `qet_generator/README.md` | Uso del generador |
| `qet_generator/templates/symbol_catalog.json` | Símbolos disponibles (14) |
| `qet_generator/tools/` | Análisis de evidencia + demos + `md_to_docx.py` |
