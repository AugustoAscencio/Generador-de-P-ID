# SPEC_INVENTARIO.md — Matriz de ingeniería extraída de los 2 documentos fuente

> **Fuentes ÚNICAS:** `fuentes/01_Sistema_Fotovoltaico_8paneles.md` (**Doc1**)
> y `fuentes/02_Referencia_TSC2_Avance.md` (**Doc2**).
> Requisito del cliente (mensaje vigente): **588 módulos × 8 paneles**.
> Cada dato cita su origen: Doc1 §x / Doc2 §x / CLIENTE / PENDIENTE.

## 1. Componentes del módulo tipo

| Tag | Componente | Datos clave | Fuente |
|---|---|---|---|
| PV-01…PV-08 | Panel JKM625-650N-66HL4M-BDV-Z1 | 650 Wp · Vmp 41,6 V · Imp 15,64 A · Voc 50,28 V · Isc 16,44 A · fusible serie máx 35 A · 1500 V DC | Doc1 §2.1.1, §4.1.1 |
| STRING | 8 paneles en serie | Vmp 332,8 V · Voc 402,2 V · Isc 16,44 A · Ib=1,25×Isc=20,55 A · 5,2 kWp | Doc1 §4.1.1–4.1.2 |
| QF-DC | Interruptor termomagnético bipolar DC | Curva C · In 25 A · aislación ≥600 VDC (único string: sin fusible por string) | Doc1 §4.1.4 |
| SPD-DC | Descargador de sobretensiones | Tipo 2, tablero de continua. Conexionado interno NO documentado → bloque | Doc1 §4.1.4 |
| FU-24VDC | Fuente 24 VDC | Alimenta controlador y actuadores (24 Vcc recomendado) | Doc1 §2.2.2, §4.1.5 |
| F-ELEV / F-AZ | Protección 24 VDC por eje | Termomagnético bipolar curva C, In 6 A por eje | Doc1 §4.1.5 |
| CTRL-01 | Creasol DomBusTracker2 | 4 relés (2 actuadores) · entradas NPN ref. GND · anemómetro 3–5 V · consumo 15 mW · sensores de luz 0–10 V · RS485 A/B · 1000 m cable apantallado | Doc1 §2.2.2, §2.5.1 |
| M-ELEV / M-AZ | SVH7-71-60-RC-24H30100-REV.A | Motorreductor doble eje 24 VDC · 71:1 · 937 N·m · retención 10,4 kN·m · 0,042 rpm · IP65 · autobloqueante (sin freno adicional) | Doc1 §2.2.1, §4.6 |
| FC-ELEV-N/S, FC-AZ-E/O | Sensores proximidad NPN ×4 | Sinking (0 V al activar) · 6–36 VDC · 3 cables · finales de carrera | Doc1 §2.3.2, §4.8.1, Anexo 4 |
| AN-WIND | Anemómetro analógico | Salida 3–5 V → AI0 · condensador 100–220 µF entre Wind y GND | Doc1 §2.2.2, §2.3.1 |
| — | Sensores de luz (2 ejes) | Impermeables, incluidos en el equipo · 0–10 V · AI1 (N/S) y AI2 (E/O) | Doc1 §2.2.2, §4.8.2 |
| — | Pulsadores ×4 y selector | Mando manual local · selector Manual/Auto | Doc1 §4.8.1 |
| — | Comunicaciones | RS485 A/B → USB-RS485/USR-DR404 (32 disp., <1200 m) → Ethernet/Wi-Fi → USR-W610 (RJ45/2,4 GHz) → Domoticz · terminación 120 Ω en extremos · 115200 bps | Doc1 §2.4, §2.5.1, §2.5.3 |
| TB-DC / TB-CTRL / TB-RS485 | Borneras | Numeración física de terminales NO documentada → PENDIENTE | Propuesta organizativa (mision) + Doc1 §2.5.1 |
| — | Puesta a tierra TT | 8 jabalinas acero cobreado L 1,5 m Ø 5/8″, s=L, cobre desnudo, bentonita/GEM −30–50 % ρ · PE 6 mm² (FV) y 2,5 mm² (24 VDC) · equipotencial: columna+vigas+gabinete+bastidores | Doc1 §4.2 |
| — | Canalización | 2 caños PVC pesado IRAM 2206-3 Ø20 mm (3/4″) separados: potencia DC vs señal/control · relleno ≤35 % | Doc1 §4.3 |
| — | Cables | String: H1Z2Z2-K 6 mm² (EN 50618) unipolar · actuadores: multipolar apantallado 1,5 mm² (IRAM 2183) | Doc1 §4.1.3, §4.1.5 |

## 2. Señales (Doc1 §4.8 — arquitectura genérica IEC 61131)

| Dir | Señal | Descripción | Física en dispositivo |
|---|---|---|---|
| I0.0 | FC-ELEV-N | Fin de carrera Norte / elevación máxima | Sí (NPN) |
| I0.1 | FC-ELEV-S | Fin de carrera Sur / elevación mínima | Sí (NPN) |
| I0.2 | FC-AZ-E | Límite giro Este | Sí (NPN) |
| I0.3 | FC-AZ-O | Límite giro Oeste | Sí (NPN) |
| I0.4–I0.7 | PB-ELEV+/−, PB-AZ+/− | Pulsadores manuales | A representar (bornera PENDIENTE) |
| I1.0 | SEL-AUTO/MAN | Selector modo | A representar |
| I1.1 | AL-WIND | Alarma de viento (umbral superado) | Derivada de AI0 |
| AI0 | AN-WIND | Anemómetro 3–5 V | Sí |
| AI1 | Luz N/S | 0–10 V | Sí |
| AI2 | Luz E/O | 0–10 V | Sí |
| Q0.0 | RL1 Elevación + | Relé 1 | Sí (4 relés físicos) |
| Q0.1 | RL2 Elevación − | Relé 2 | Sí |
| Q0.2 | RL3 Azimut + | Relé 3 | Sí |
| Q0.3 | RL4 Azimut − | Relé 4 | Sí |
| Q0.4 | RL5 Zumbador/señalización | **Genérica IEC 61131 — NO confirmada física (el equipo tiene 4 relés)** | PENDIENTE |
| Q0.5 | RL6 Reserva/alarma remota | **Genérica IEC 61131 — NO confirmada física** | PENDIENTE |

## 3. Control y seguridad (Doc1 §4.9)

- **Estados:** 0 Reposo/Init · 1 Seguimiento auto (I1.0=1, I1.1=0) · 2 STOW (AI0>20 m/s → I1.1=1) · 3 Manual (I1.0=0).
- **Enclavamientos:** STOW prioridad absoluta · FC impide movimiento hacia su límite (cualquier modo) · Q0.0↔Q0.1 y Q0.2↔Q0.3 mutuamente excluyentes · tras viento, retorno a Estado 1 solo con selector en Auto · retardo de seguridad tras cese de alarma.
- **Umbral operativo de viento: 20 m/s** (STOW). Diseño estructural: 50 m/s (CIRSOC). No añadir mecanismos no documentados.

## 4. Interfaces y escalado

- Salida DC del módulo → red de colección: **FUERA DE ALCANCE** (Doc1 §4.1 nota de escala).
- Comunicación de planta: ~49 USR-DR404 mínimo (1539/32) — pero red de planta **no diseñada** en fuentes (Doc1 §2.4 nota). Con 588 módulos: 588/32 ≈ 19 ramales — **cálculo derivado, no diseñar topología**.
- Tierra: malla general de planta IEEE Std 80 **FUERA DE ALCANCE** (Doc1 §4.2.4 nota).

## 5. Discrepancias registradas (NO resolver en silencio)

| # | Discrepancia | Tratamiento |
|---|---|---|
| 1 | CLIENTE: "588 módulos × 8 paneles de 650 **kw**" vs Doc1: paneles 625–650 **Wp**; ~1539 módulos para 8 MW | Requisito de alcance = 588. En esquemas: 650 **Wp** (terminología Doc1). El texto del cliente se conserva como requisito, no como especificación técnica. |
| 2 | Doc2 describe un sistema agrivoltaico distinto (500 kWp, 770 módulos, 22 paneles/string, 5 inversores 100 kW, BESS 1,2 MWh) | Solo se usan criterios generales de Doc2 (filosofía de protecciones Tabla 6.5, unifilar por bloques). Sus valores NO se aplican al módulo. |
| 3 | Q0.4/Q0.5 definidas solo en arquitectura genérica; dispositivo físico: 4 relés | Marcar "ARQUITECTURA GENÉRICA — NO CONFIRMADA FÍSICA" |
| 4 | Numeración de terminales/bornes del DomBusTracker2 y borneras no documentada | Marcar "PENDIENTE DE VERIFICACIÓN" |
| 5 | Conexionado interno del SPD no detallado | Representar como bloque tipo 2 sin inventar internos |
| 6 | Polaridad por terminal del panel (símbolo genérico pvcell) | Marcar "PENDIENTE DE VERIFICACIÓN" en D-003 |

## 6. Estructura de los 18 planos

D-001 Arquitectura/índice · **D-002 General del módulo tipo (HECHA)** · **D-003 String FV (HECHA)** · D-004 Protección DC · D-005 Alimentación 24 VDC · D-006 Eje elevación · D-007 Eje azimut · D-008 Sensores/entradas · D-009 Viento/STOW · D-010 Mapa E/S · D-011 Estados · D-012 Seguridad/enclavamientos · D-013 Comunicaciones · D-014 Tierra TT · D-015 Canalizaciones · D-016 Borneras · D-017 Interfaz planta · D-018 Módulo tipo × 588.
