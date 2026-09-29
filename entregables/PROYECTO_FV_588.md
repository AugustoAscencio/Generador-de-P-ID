# PROYECTO FOTOVOLTAICO — SISTEMA DE SEGUIMIENTO SOLAR BIAXIAL
## Documentación eléctrica · 588 módulos × 8 paneles

**Sistema:** 588 seguidores solares biaxiales, cada uno con 8 paneles fotovoltaicos de 650 Wp en serie (5,2 kWp por módulo).
**Potencia del conjunto:** 588 × 5,2 kWp = 3.057,6 kWp ≈ **3,06 MWp** (cálculo derivado del alcance).
**Ubicación:** Puerto Madryn, provincia de Chubut, Argentina.
**Herramienta de diseño:** QElectroTech 0.100.0 — proyecto editable, multiplano, exportable a PDF.
**Archivo del proyecto:** `qet_generator/output/Proyecto_FV_588_Modulos.qet` (18 planos).

---

## 1. Filosofía de la documentación

El sistema se documenta con la metodología de ingeniería industrial para plantas modulares:

```
SISTEMA COMPLETO (588 MÓDULOS)
        │
ARQUITECTURA DE REPETICIÓN          → D-001 · D-017 · D-018
        │
MÓDULO TIPO — ingeniería unitaria   → D-002 … D-016
        │
M-001 · M-002 · … · M-588           → instancias del mismo diseño
```

**El módulo tipo se documenta una sola vez.** Los 588 módulos son instancias
idénticas del mismo diseño; no se dibujan 588 juegos de planos, sino una
arquitectura de escalamiento (D-018) que los representa como grupos de
instancia, cada uno heredando la ingeniería de D-002 a D-017.

## 2. Inventario de planos (18)

| Plano | Título | Contenido técnico |
|---|---|---|
| D-001 | Arquitectura del sistema e índice | Sistema → 588 módulos → módulo tipo; índice de planos |
| D-002 | Diagrama general del módulo tipo | Mapa funcional: potencia DC · control 24 VDC · comunicaciones |
| D-003 | String fotovoltaico | 8 paneles 650 Wp en serie: 332,8 V VMP · 402,2 V VOC · 16,44 A ISC · Ib 20,55 A; salida a borneras |
| D-004 | Protección DC | Interruptor termomagnético bipolar DC 25 A curva C ≥600 VDC · SPD tipo 2 · PE |
| D-005 | Alimentación 24 VDC | Fuente 24 VDC · protecciones 6 A por eje (curva C) · separación control/actuadores |
| D-006 | Eje de elevación | Q0.0/Q0.1 → F-ELEV → SVH7 · finales de carrera NPN I0.0/I0.1 |
| D-007 | Eje de azimut | Q0.2/Q0.3 → F-AZ → SVH7 · límites I0.2/I0.3 |
| D-008 | Sensores y entradas | FC ×4 NPN · pulsadores ×4 · selector · alarma de viento · AI0–AI2 |
| D-009 | Sistema de viento | Anemómetro 3–5 V → AI0 · condensador 100–220 µF · umbral 20 m/s → STOW |
| D-010 | Mapa de E/S | I0.0–I1.1 · AI0–AI2 · Q0.0–Q0.3 (con señales no confirmadas marcadas) |
| D-011 | Diagrama de estados | Reposo · seguimiento · STOW · manual, con condiciones de transición |
| D-012 | Seguridad y enclavamientos | Prioridad STOW · bloqueo por FC · exclusión de sentidos por eje |
| D-013 | Comunicaciones | RS485 (120 Ω, 2×0,22 mm) → USR-DR404 → Ethernet/Wi-Fi → USR-W610 → Domoticz |
| D-014 | Puesta a tierra | Esquema TT · 8 jabalinas L=1,5 m Ø5/8″ · PE 6 / 2,5 mm² · equipotencialidad |
| D-015 | Canalizaciones | Segregación: potencia DC / control 24 VDC / señal-RS485 · relleno ≤35 % |
| D-016 | Borneras | TB-DC · TB-CTRL (entradas/salidas) · TB-RS485, por señal |
| D-017 | Interfaz con planta | Qué sale del módulo y qué requiere ingeniería de planta |
| D-018 | Módulo tipo × 588 | Tabla de instancias M-001…M-588 (21 grupos × 28) |

## 3. Ingeniería representada (resumen técnico)

**Generación (string DC):** 8 × JKM625-650N-66HL4M-BDV-Z1 (650 Wp, Vmp 41,6 V,
Voc 50,28 V, Isc 16,44 A) en serie → Vmp,string 332,8 V · Voc,string 402,2 V ·
corriente de diseño Ib = 1,25 × Isc = 20,55 A. Cable H1Z2Z2-K 6 mm² (EN 50618).

**Protección:** interruptor termomagnético **bipolar DC, curva C, 25 A,
aislación ≥600 VDC** (criterio Ib ≤ In ≤ Iz; In ≤ 35 A) y **SPD tipo 2** en el
tablero de continua. Un único string → sin protección de sobrecorriente por string.

**Control:** Creasol **DomBusTracker2** con 4 relés de salida (elevación ±,
azimut ±), entradas NPN (finales de carrera), anemómetro 3–5 V con condensador
100–220 µF entre Wind y GND, y sensores de luz integrados (0–10 V). Lógica de
4 estados con **STOW por viento > 20 m/s** (prioridad absoluta, θ2 = 90°),
enclavamiento por finales de carrera y exclusión mutua de sentidos por eje.

**Accionamiento:** 2 motorreductores SVH7 de doble eje, 24 VDC, relación 71:1,
937 N·m, autobloqueo por tornillo sinfín (retención 10,4 kN·m — sin freno
adicional). Protección bipolar de 6 A por eje; cable multipolar apantallado 1,5 mm².

**Comunicación:** bus RS485 con terminación de 120 Ω (2×0,22 mm apantallado,
115200 bps, hasta 32 dispositivos por ramal) → USR-DR404 → Ethernet/Wi-Fi →
USR-W610 → plataforma Domoticz.

**Tierra:** esquema TT con 8 jabalinas de acero cobreado (L 1,5 m, Ø 5/8″,
separación s = L), conductor de cobre desnudo, tratamiento de terreno
(bentonita/GEM), PE de 6 mm² (DC) y 2,5 mm² (24 VDC); verificación con
telurímetro (objetivo ≤ 10 Ω).

**Seguridad estructural:** CIRSOC 102-2025, viento de diseño 50 m/s, STOW a 20 m/s.

## 4. Reglas de calidad del paquete

1. **Trazabilidad total:** cada valor representado procede de la documentación
   técnica del proyecto (citada por sección) o es un cálculo derivado explícito.
2. **Nada inventado:** los elementos cuyo conexionado no está definido en la
   documentación (numeración física de bornes del controlador, conexionado
   interno del SPD, asignación de polaridad por terminal del panel, salidas
   Q0.4/Q0.5) figuran marcados **«PENDIENTE DE VERIFICACIÓN»**.
3. **Alcance delimitado:** la red de colección DC, la red de comunicaciones de
   planta y la malla de tierra general **no forman parte** de este paquete y así
   se declara en D-017 (interfaces). El paquete documenta el módulo tipo y su
   arquitectura de repetición.
4. **Nomenclatura uniforme:** PV-01…08 · QF-DC · SPD-DC · CTRL-01 · FU-24VDC ·
   F-ELEV/F-AZ · M-ELEV/M-AZ · FC-ELEV-N/S · FC-AZ-E/O · AN-WIND · PB-… ·
   SEL-AM · TB-DC/TB-CTRL/TB-RS485.
5. **Coherencia cruzada:** las referencias (Q0.0 = Elevación +, I0.0 = FC Norte,
   etc.) son idénticas en todos los planos donde aparecen (D-002, D-006, D-008,
   D-010, D-011, D-012).

## 5. Cómo usar el paquete

- **Abrir:** doble clic en `Proyecto_FV_588_Modulos.qet` (QElectroTech 0.100.0).
  El panel izquierdo lista los 18 planos; cada uno lleva cartucho con título,
  fecha, revisión y numeración de folio.
- **Editar:** el proyecto es 100 % editable (símbolos reales de la biblioteca
  QElectroTech, conductores, textos y bloques funcionales nativos).
- **Exportar:** Archivo → Exportar → PDF (por folio o proyecto completo) para
  la entrega final.
- **Regenerar:** el paquete se produce automáticamente desde el modelo
  estructurado (`examples/proyecto_fv_588.json` → generador), por lo que
  cualquier revisión de ingeniería se aplica a los 18 planos en un paso:
  ```bash
  cd qet_generator
  python tools/build_sheets.py
  python main.py examples/proyecto_fv_588.json -o output/Proyecto_FV_588_Modulos.qet
  ```

---
*Paquete de documentación eléctrica · Proyecto FV 588 módulos con seguidor biaxial · QElectroTech 0.100.0 · 18 planos*
