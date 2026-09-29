# MEMORIA TÉCNICA
## SISTEMA FOTOVOLTAICO CON SEGUIMIENTO SOLAR BIAXIAL
### 588 módulos × 8 paneles de 650 Wp — Documentación eléctrica completa

| | |
|---|---|
| **Proyecto** | Sistema fotovoltaico con seguidor solar biaxial — 588 módulos |
| **Ubicación** | Puerto Madryn, provincia de Chubut, Argentina |
| **Alcance de esta memoria** | Ingeniería eléctrica del módulo tipo y arquitectura de repetición ×588 |
| **Documentación asociada** | Paquete de 18 planos eléctricos (D-001 a D-018), QElectroTech 0.100.0 |
| **Revisión** | A — Septiembre de 2026 |
| **Elaborado por** | ______________________ (ingeniería eléctrica responsable) |

---

## 1. DESCRIPCIÓN GENERAL DEL PROYECTO

### 1.1 Objeto

El proyecto consiste en un sistema de generación fotovoltaica con **seguimiento solar de doble eje (biaxial)**, compuesto por **588 módulos (seguidores)**. Cada módulo es una unidad electromecánica completa e independiente que agrupa:

- **8 paneles fotovoltaicos de 650 Wp** conectados en serie (un string), con una potencia unitaria de **5,2 kWp**;
- una **estructura de seguidor biaxial** accionada por un motorreductor de doble eje (SVH7);
- un **sistema de control dedicado** (Creasol DomBusTracker2) con seguimiento astronómico/óptico, protección por viento y comunicación remota;
- las **protecciones, canalizaciones, puesta a tierra y borneras** propias del módulo.

La potencia del conjunto resulta:

> **588 módulos × 5,2 kWp = 3.057,6 kWp ≈ 3,06 MWp** *(cálculo derivado del alcance)*

### 1.2 Filosofía de diseño: MÓDULO TIPO × 588

Toda la ingeniería repetitiva se resuelve **una sola vez** sobre el **módulo tipo** (planos D-002 a D-016) y se escala mediante una **arquitectura de repetición** (planos D-001, D-017, D-018). Los 588 módulos son **instancias idénticas** del módulo tipo: no se dibujan 588 juegos de planos, lo que garantiza coherencia total, mantenibilidad y revisiones centralizadas.

```
SISTEMA COMPLETO (588 MÓDULOS)
        │
ARQUITECTURA DE REPETICIÓN            → D-001 · D-017 · D-018
        │
MÓDULO TIPO — ingeniería unitaria     → D-002 … D-016
        │
M-001 · M-002 · … · M-588             → instancias del mismo diseño
```

### 1.3 Condiciones de sitio y normativa aplicable

| Parámetro | Valor |
|---|---|
| Ubicación | Puerto Madryn, Chubut (suelo árido gravoso-arenoso) |
| Viento de diseño (estructura) | **50 m/s** — CIRSOC 102-2025 |
| Viento operativo (umbral de seguridad) | **20 m/s** → posición STOW |
| Categoría de riesgo | I |
| Categoría de exposición | C (campo abierto) |
| Clasificación del cerramiento | Estructura abierta (Ao ≥ 0,8·Ag) |

**Normativa y referencias de diseño:** CIRSOC 102-2025 (acción del viento); AEA 90364 (instalaciones eléctricas) y AEA 90364-7-712 (sistemas fotovoltaicos); EN 50618 (cables solares); IRAM 2183 (conductores aislados PVC); IRAM 2206-3 (caños PVC rígidos); IEC 61131-3 (direccionamiento de E/S); IEEE Std 80 (malla de planta, fuera del alcance).

---

## 2. GENERACIÓN FOTOVOLTAICA

### 2.1 Panel seleccionado

**Modelo: JKM625-650N-66HL4M-BDV-Z1** (Jinko Solar, bin 650 Wp), bifacial de doble vidrio.

| Característica | Especificación |
|---|---|
| Potencia nominal | 625 – 650 W (se adopta **650 Wp** para el cálculo del módulo) |
| Eficiencia máxima | 24,1 % |
| Tecnología de celda | N-Type TOPCon HOT 2.0 |
| Configuración | 132 medias celdas (66 × 2) |
| Dimensiones / peso | 2382 × 1134 × 30 mm / 32,4 kg |
| Tensión máxima de sistema | 1500 V DC |
| Carga mecánica | Frontal 5400 Pa / Posterior 2400 Pa |
| Temperatura de operación | −40 °C a +70 °C |
| Bifacialidad | 85 ± 5 % |
| Garantías | 12 años (producto) / 30 años (potencia) |

**Parámetros eléctricos (ficha del fabricante):**

| Parámetro | Símbolo | Valor |
|---|---|---|
| Tensión en máxima potencia | Vmp | 41,6 V |
| Corriente en máxima potencia | Imp | 15,64 A |
| Tensión de circuito abierto | Voc | 50,28 V |
| Corriente de cortocircuito | Isc | 16,44 A |
| Corriente máx. admisible de fusible de serie | — | 35 A |

> **Nota terminológica:** la potencia del panel se especifica en **vatios pico (650 Wp)**, unidad correcta para módulos fotovoltaicos.

### 2.2 Configuración del string

Se adopta **un (1) string de 8 paneles en serie** por módulo, alimentando un único punto de conexión (tablero de continua del módulo). La conexión serie suma tensiones manteniendo la corriente:

| Magnitud del string | Cálculo | Resultado |
|---|---|---|
| Vmp,string | 8 × 41,6 V | **332,8 V** |
| Voc,string | 8 × 50,28 V | **402,2 V** |
| Isc,string | = Isc del módulo (serie no suma corriente) | **16,44 A** |
| Potencia del módulo | 8 × 650 Wp | **5,2 kWp** |

**Verificación:** Voc,string (402,2 V) queda muy por debajo de la tensión máxima de sistema del panel (1500 V DC) → **configuración serie de 8 unidades válida**.

### 2.3 Corriente de diseño del circuito de continua

Los generadores fotovoltaicos operan en sobrecorriente continua; el criterio reglamentario (AEA 90364-7-712) aplica un factor de 1,25 sobre Isc:

> **Ib = 1,25 × Isc,string = 1,25 × 16,44 A = 20,55 A**

Este valor gobierna la selección de la protección y la verificación de ampacidad del conductor.

---

## 3. PROTECCIÓN Y CABLEADO DEL CIRCUITO DC

### 3.1 Criterio de protección

Al tratarse de **un único string** (sin strings en paralelo), **no existe riesgo de corrientes inversas entre strings**, por lo que no se requiere protección de sobrecorriente por string. Se dispone igualmente un **interruptor-seccionador de continua** para maniobra y protección del tablero:

| Selección | Valor | Verificación |
|---|---|---|
| Interruptor termomagnético **bipolar DC**, curva C | In = 25 A | Ib (20,55) ≤ In (25) ✓ |
| Tensión nominal de aislación | ≥ 600 V DC | > Voc,string (402,2 V) — margen amplio ✓ |
| Límite superior | In ≤ 35 A (fusible de serie máx. del módulo) | 25 A ≤ 35 A ✓ |

Criterio completo: **Ib ≤ In ≤ Iz** (AEA 90364-5), verificado además contra la ampacidad corregida del conductor en obra.

### 3.2 Protección contra sobretensiones

Se incorpora un **descargador de sobretensiones (SPD) tipo 2** en el tablero de continua, conforme a las recomendaciones de AEA 90364-7-712 para protección ante sobretensiones de origen atmosférico. El conexionado interno del SPD se instala según indicaciones del fabricante (plano D-004).

### 3.3 Conductores

| Circuito | Cable | Sección | Norma |
|---|---|---|---|
| String (panel → tablero DC) | H1Z2Z2-K unipolar, cobre estañado clase 5, goma reticulada libre de halógenos, 1,5/1,5 (1,8) kV DC, 90 °C (120 °C transitorio) | **6 mm²** | EN 50618 |
| Protección PE (circuito FV) | Cobre | **6 mm²** (= activo, criterio < 16 mm², AEA 90364-5) | AEA 90364-5 |
| Accionamiento 24 VDC | Multipolar apantallado | **1,5 mm²** | IRAM 2183 |
| Protección PE (24 VDC) | Cobre | **2,5 mm²** | AEA 90364-5 |

---

## 4. SISTEMA DE SEGUIMIENTO Y ACCIONAMIENTO

### 4.1 Motorreductor de doble eje SVH7

**Modelo: SVH7-71-60-RC-24H30100-REV.A** (Coresun Drive), slewing drive de doble eje para seguidores solares.

| Característica | Valor |
|---|---|
| Alimentación del motor | 24 VDC |
| Relación de transmisión | 71:1 |
| Torque de salida | 937 N·m |
| Torque de momento de inclinación | 13,5 kN·m |
| Torque de retención (holding) | 10,4 kN·m |
| Velocidad de salida | 0,042 rpm |
| Clase de protección / eficiencia | IP65 / 40 % |
| Peso | 85 kg |
| Capacidad | 6–10 paneles (200–600 kg) |

### 4.2 Verificación de ejes y frenado

- **Eje de elevación:** momento neto calculado por presión diferencial a 45° (caso más desfavorable en posición de trabajo). Índice de aprovechamiento **I = 0,62** (< 0,85, sobredimensionado). La salida de la posición STOW por peso propio también se verifica con margen.
- **Eje de azimut:** el momento de viento dominante actúa sobre el eje de elevación, no sobre el eje vertical. Torque requerido = fricción (416 N·m, ≈ 4 % del torque de retención) + desalineación aerodinámica (57,9 N·m) + inercia (0,9 N·m, despreciable a 0,042 rpm) = **474,8 N·m → I = 0,51**.
- **Frenado:** el mecanismo de tornillo sinfín con relación 71:1 es **autoblocante** (λ < arctan μ), propiedad geométrica que no depende de energía ni electrónica. El frenado requerido en la condición más desfavorable es 1,25 × 579,1 = 723,9 N·m frente a una retención de 10,4 kN·m (**I = 0,070**, margen > 14×). **Conclusión: no se requiere freno electromecánico adicional**; ambos ejes quedan bloqueados de forma pasiva y redundante.

### 4.3 Cinemática (referencia para la lógica de control)

Mecanismo serial de 2 GDL (convención Denavit-Hartenberg):

| Eslabón | ai | αi | di | θi |
|---|---|---|---|---|
| 1 (azimut) | 0 | 90° | 3,00 m (columna) | θ1 (0–360°) |
| 2 (elevación) | 2,30 m | 0° | 0 | θ2 (0–90°) |

θ2 = 90° corresponde a la **posición de bandera (STOW)**. Sin offset entre ejes, la cinemática inversa admite solución cerrada directa a partir del azimut y la elevación solar.

---

## 5. SISTEMA DE CONTROL

### 5.1 Controlador Creasol DomBusTracker2

| Característica | Descripción |
|---|---|
| Función | Controlador de seguidor solar de uno/dos ejes (Rev. 2) |
| Consumo | 15 mW |
| Salidas | 4 relés → comando de 2 actuadores (hasta 800 kgf) |
| Alimentación de actuadores | 24 Vcc (recomendada) o 12 Vcc |
| Entradas de posición | Sensores de proximidad **NPN**, lógica *sinking*, referencia común a GND |
| Entrada de viento | Anemómetro analógico **3–5 V**, con **condensador de 100–220 µF entre Wind y GND** (supresión de picos/ruido) |
| Sensado solar | Sensores de luz impermeables incluidos (2 ejes, 0–10 V) |
| Comunicación | Bus RS485 (A/B); hasta 1000 m con cable apantallado |

### 5.2 Mapa de entradas y salidas

**Entradas digitales (DI):**

| Dirección | Señal | Descripción |
|---|---|---|
| I0.0 | FC-ELEV-N | Fin de carrera Norte — elevación máxima (NPN) |
| I0.1 | FC-ELEV-S | Fin de carrera Sur — elevación mínima (NPN) |
| I0.2 | FC-AZ-E | Límite de giro Este (NPN) |
| I0.3 | FC-AZ-O | Límite de giro Oeste (NPN) |
| I0.4 / I0.5 | PB-ELEV +/− | Pulsadores manuales de elevación |
| I0.6 / I0.7 | PB-AZ +/− | Pulsadores manuales de azimut |
| I1.0 | SEL-AUTO/MAN | Selector de modo (1 = Automático) |
| I1.1 | AL-WIND | Alarma de viento (umbral superado, derivada de AI0) |

**Entradas analógicas (AI):**

| Dirección | Señal | Rango |
|---|---|---|
| AI0 | Anemómetro (velocidad de viento) | 3–5 V |
| AI1 | Sensor de luz — eje Norte/Sur | 0–10 V |
| AI2 | Sensor de luz — eje Este/Oeste | 0–10 V |

**Salidas digitales (DO) — 4 relés físicos:**

| Dirección | Relé | Función |
|---|---|---|
| Q0.0 | RL1 | Elevación + |
| Q0.1 | RL2 | Elevación − |
| Q0.2 | RL3 | Azimut + |
| Q0.3 | RL4 | Azimut − |

> Las direcciones Q0.4 (RL5, señalización) y Q0.5 (RL6, reserva) figuran en la arquitectura genérica IEC 61131-3 del control; el equipo dispone de **4 bornes de relé físicos (Q0.0–Q0.3)**, por lo que Q0.4/Q0.5 quedan **pendientes de verificación** como salidas físicas.

### 5.3 Lógica de estados

| Estado | Denominación | Condición / comportamiento |
|---|---|---|
| 0 | Reposo / Inicialización | A la energización verifica finales de carrera (I0.0–I0.3) y homologa la posición |
| 1 | Seguimiento automático | I1.0 = 1 y I1.1 = 0; calcula (θ1, θ2) por cinemática inversa y activa Q0.0–Q0.3 hasta equilibrio de iluminación entre cuadrantes (AI1/AI2) |
| 2 | **STOW / posición de bandera** | AI0 > 20 m/s → I1.1 = 1; interrumpe el seguimiento y lleva θ2 = 90°, **independientemente del selector**; permanece mientras dure la alarma más un retardo de seguridad |
| 3 | Modo manual | I1.0 = 0; los pulsadores I0.4–I0.7 accionan directamente las salidas, enclavadas por los finales de carrera |

### 5.4 Enclavamientos de seguridad (válidos en cualquier estado)

1. **STOW tiene prioridad absoluta** sobre el seguimiento automático y el modo manual.
2. Ninguna salida (Q0.0–Q0.3) puede activarse si el final de carrera del sentido de movimiento solicitado está accionado (I0.0–I0.3).
3. **Las salidas de un mismo eje son mutuamente excluyentes** (Q0.0↔Q0.1 y Q0.2↔Q0.3): nunca se activan ambos sentidos simultáneamente.
4. Tras un evento de viento, el retorno al seguimiento solo ocurre con el selector en Automático (sin reinicios no supervisados en manual) y respetando el retardo de seguridad.

---

## 6. SEGURIDAD POR VIENTO

La protección por viento es una **función de seguridad del sistema** (plano D-009):

```
ANEMÓMETRO (3–5 V) → AI0 → umbral 20 m/s → ALARMA I1.1 → STOW (θ2 = 90°)
        └─ condensador 100–220 µF entre Wind y GND (supresión de ruido)
```

- **Umbral operativo: 20 m/s** → interrupción del seguimiento y posición de bandera.
- **Condición de viento excesivo:** interrupción del seguimiento → posición de seguridad (STOW).
- **Diseño estructural: 50 m/s** (CIRSOC 102-2025). Cargas máximas verificadas: 724 N/m² (posición de trabajo, 45° a barlovento) y 770,4 N/m² (STOW, 90°), con qh(20) = 181,3 N/m² y qh(50) = 1133 N/m².
- Parámetros CIRSOC adoptados: Kd = 0,85 · Kz = 0,87 · Kzt = 1 · G = 0,85 · estructura abierta.
- No se incorporan mecanismos de seguridad adicionales a los definidos por la ingeniería.

---

## 7. ALIMENTACIÓN 24 VDC

El circuito de accionamiento se alimenta a **24 VDC** (coherente con los motores SVH7), con **separación explícita entre la alimentación del control y la de los actuadores**:

```
FU-24VDC ──┬──→ alimentación de control (CTRL-01)
           ├──→ [F-ELEV 6 A, curva C, bipolar] ──→ M-ELEV (SVH7 elevación)
           └──→ [F-AZ   6 A, curva C, bipolar] ──→ M-AZ   (SVH7 azimut)
```

- Protección individual: **interruptor termomagnético bipolar 24 VDC, curva C, In = 6 A por eje**, coherente con los 4 relés de salida del controlador.
- Cableado de actuadores: multipolar apantallado de cobre 1,5 mm² (IRAM 2183); PE 2,5 mm².

---

## 8. PUESTA A TIERRA (ESQUEMA TT)

### 8.1 Diseño del electrodo

| Parámetro | Valor |
|---|---|
| Esquema | **TT** (masas a tierra local propia) |
| Electrodo | Jabalinas de acero cobreado, L = 1,5 m, Ø 14,3 mm (5/8″) |
| Configuración | **8 jabalinas en paralelo**, separadas s = L = 1,5 m (mínimo apantallamiento mutuo) |
| Interconexión | Conductor de cobre desnudo |
| Tratamiento del terreno | Bentonita sódica / gel electrolítico (GEM): reducción típica 30–50 % de ρ |
| Objetivo de diseño | ≤ 10 Ω (equipos electrónicos sensibles; límite asociado al diferencial) |
| Verificación | Medición con telurímetro en obra |

### 8.2 Equipotencialidad y conductores PE

Se unen al sistema de tierra local del módulo: **columna, viga principal, vigas secundarias/bastidores de paneles y gabinete del controlador**. Secciones de PE: **6 mm²** (circuito FV) y **2,5 mm²** (circuito 24 VDC), aplicando el criterio AEA 90364-5 (PE = conductor activo para secciones < 16 mm²).

> **Límite de alcance:** la vinculación de cada tierra local con la **malla general de planta y subestación** (IEEE Std 80-2013) pertenece a la ingeniería de balance de planta y se declara en el plano de interfaz (D-017).

---

## 9. CANALIZACIONES

| Canalización | Circuito | Contenido | Norma |
|---|---|---|---|
| Caño 1 | Continua (potencia) | 2 × H1Z2Z2-K 6 mm² (+/− del string) + PE 6 mm² | PVC pesado Ø 20 mm (3/4″), IRAM 2206-3 |
| Caño 2 | Control / actuación 24 VDC | Multipolar apantallado 1,5 mm² + PE 2,5 mm² | PVC pesado Ø 20 mm, IRAM 2206-3 |
| Caño 3 | Señal / comunicación | Par apantallado RS485 2 × 0,22 mm + señales AI0–AI2 | PVC pesado Ø 20 mm, IRAM 2206-3 |

- **Factor de ocupación máximo: 35 %** de la sección interna del conducto (≥ 3 conductores).
- **Segregación obligatoria potencia / control / señal** en conductos independientes, para reducir interferencias electromagnéticas (criterio AEA 90364-5).

---

## 10. COMUNICACIONES Y MONITOREO (IoT)

### 10.1 Arquitectura del módulo

```
DomBusTracker2 ── RS485 (A/B, 2×0,22 mm apantallado) ──→ USR-DR404 ──→ Ethernet/Wi-Fi
                                                                    └──→ USR-W610 ──→ Domoticz / sistema superior
```

| Elemento | Función / dato |
|---|---|
| Bus RS485 | Bornes A/B del controlador; **resistencia de terminación de 120 Ω en los extremos del bus**; velocidad **115200 bps** |
| USR-DR404 | Concentrador serie RS485 → Wi-Fi/Ethernet; hasta **32 dispositivos por ramal**, distancia < 1200 m |
| USR-W610 | Servidor serial RS232/RS485 → **RJ45 (Ethernet) / Wi-Fi 2,4 GHz**; alcance 280 m; hasta 24 dispositivos |
| Domoticz | Plataforma de monitoreo con plugin CreasolDomBus (hardware tipo "Creasol DomBus", puerto serie, 115200 bps): mandos manuales, lecturas de sensores de luz, estado de viento, estados/consumos de actuadores |
| Protocolo | Modbus, modelo maestro-esclavo |

### 10.2 Escala de planta (declaración de alcance)

La arquitectura de comunicación descrita corresponde **al módulo unitario**. La red de comunicaciones a nivel de planta (segmentación de ramales, ubicación de concentradores, redundancia) requiere su propia ingeniería: como referencia, cada USR-DR404 concentra hasta 32 controladores, por lo que 588 módulos implican del orden de **19 ramales/concentradores** *(cálculo derivado)*. Este diseño de planta **no forma parte del paquete** y así se declara en D-017.

---

## 11. ESTRUCTURA DE SOPORTE (RESUMEN)

La estructura fue dimensionada por el método de esfuerzos permisibles (A.S.D.) bajo las cargas de viento CIRSOC y validada numéricamente por elementos finitos:

| Elemento | Selección | Índice de aprovechamiento |
|---|---|---|
| Vigas secundarias (×5) | Perfil G 100x50x15x2 — ASTM A-36 | 0,34 |
| Viga principal | HSS 5 × 0,375 — ASTM A 500 Gr. C | 0,70 |
| Columna | Perfil W6 × 15 — ASTM A-588 | 0,17 |
| Placa base | 25 × 25 × 2 cm — A588 Gr. C | — |
| Pernos de anclaje | 1 pulg, ISO 8.8 (J = 6 cm; plinto 0,5 m) | — |
| Soldadura columna-placa | Electrodo E8013, L ≥ 126 mm | — |
| Refuerzo | Reticulado diagonal L 2×2×1/8″ A-36 | — |

- Cargas gravitacionales consideradas: 8 paneles (259,2 kg / 2,543 kN) + SVH7 (85 kg / 0,834 kN) + mantenimiento (200 kg / 1,962 kN) = 544,2 kg / 5,339 kN.
- **Validación FEM:** primer modo global F1 = 5,363 Hz; frecuencia de desprendimiento de vórtices (Strouhal) a 20 m/s = 31,50 Hz (separación > 5×, sin riesgo de resonancia, EN 1991-1-4 Anexo E); tensión normal máx. 89,74 MPa (I = 0,432); desplazamiento máx. 10,11 mm (cumple L/180; el criterio de servicio L/240 queda señalado como punto de atención de rigidez).
- Protección anticorrosiva: **galvanizado en caliente** (ASTM A123/A123M, ISO 1461) en todos los perfiles estructurales.

---

## 12. PAQUETE DE PLANOS ELÉCTRICOS (18 HOJAS)

Toda la ingeniería anterior queda representada en un único proyecto QElectroTech editable:

| Plano | Contenido |
|---|---|
| **D-001** | Arquitectura del sistema e índice de planos |
| **D-002** | Diagrama general del módulo tipo (potencia DC · control 24 VDC · comunicaciones) |
| **D-003** | String fotovoltaico: 8 paneles en serie, salida a borneras, datos eléctricos |
| **D-004** | Protección DC: QF-DC bipolar 25 A curva C ≥ 600 VDC + SPD tipo 2 + PE |
| **D-005** | Alimentación 24 VDC: fuente + protecciones 6 A por eje |
| **D-006** | Eje de elevación: Q0.0/Q0.1 → F-ELEV → SVH7; FC NPN I0.0/I0.1 cableados a 3 hilos |
| **D-007** | Eje de azimut: Q0.2/Q0.3 → F-AZ → SVH7; FC I0.2/I0.3 |
| **D-008** | Sensores y entradas: FC ×4, pulsadores ×4, selector, alarmas, AI0–AI2 |
| **D-009** | Sistema de viento: anemómetro → AI0, condensador 100–220 µF, umbral 20 m/s → STOW |
| **D-010** | Mapa de E/S del controlador |
| **D-011** | Diagrama de estados (reposo / automático / STOW / manual) con transiciones |
| **D-012** | Seguridad y enclavamientos (prioridad STOW, bloqueo por FC, exclusión de sentidos) |
| **D-013** | Comunicaciones RS485 / IoT (120 Ω, USR-DR404, USR-W610, Domoticz) |
| **D-014** | Puesta a tierra TT del módulo (8 jabalinas) |
| **D-015** | Canalizaciones (segregación potencia / control / señal) |
| **D-016** | Borneras e interfaces (TB-DC, TB-CTRL, TB-RS485) |
| **D-017** | Interfaz con planta (límite de alcance documentado) |
| **D-018** | Módulo tipo × 588: tabla de instancias M-001…M-588 |

**Reglas de calidad del paquete:**

1. **Trazabilidad total** — cada valor de los planos procede de esta memoria y de la documentación técnica de los componentes, o es un cálculo derivado explícito.
2. **Nada inventado** — los ítems no confirmados (numeración física de bornes del controlador, conexionado interno del SPD, asignación de polaridad por terminal del panel, salidas Q0.4/Q0.5) figuran marcados **«PENDIENTE DE VERIFICACIÓN»**.
3. **Nomenclatura uniforme** — PV-01…08 · QF-DC · SPD-DC · CTRL-01 · FU-24VDC · F-ELEV/F-AZ · M-ELEV/M-AZ · FC-… · AN-WIND · PB-… · SEL-AM · TB-….
4. **Coherencia cruzada** — las referencias son idénticas en todas las hojas donde aparecen.
5. **Formato profesional** — símbolos eléctricos reales de biblioteca normalizada, bloques funcionales, cartucho con título/fecha/revisión/folio por plano, proyecto 100 % editable y exportable a PDF.

**Metodología de producción:** los planos se generan paramétricamente desde un modelo estructurado del proyecto (módulo tipo y plantillas de eje reutilizables), lo que garantiza la coherencia entre hojas y permite regenerar el paquete completo ante cualquier revisión de ingeniería en un solo paso.

---

## 13. NOTAS DE ALCANCE Y PENDIENTES

### 13.1 Alcance

- **Requisito vigente del proyecto: 588 módulos × 8 paneles.** La documentación técnica de referencia desarrolla el módulo de 8 paneles (5,2 kWp) y estima del orden de 1539 módulos para un objetivo de planta de 8 MW; el presente paquete documenta el alcance de **588 módulos (≈ 3,06 MWp)**. Esta diferencia queda **registrada** y no altera la ingeniería del módulo tipo, que es idéntica en ambos casos.

### 13.2 Pendientes de verificación (marcados en los planos)

1. Numeración física de terminales/bornes del DomBusTracker2 y de las borneras (se documentan por señal/función).
2. Conexionado interno del SPD (instalación según fabricante).
3. Asignación de polaridad (+/−) por terminal del panel (símbolo genérico de biblioteca).
4. Salidas Q0.4/Q0.5 como físicas o no (el equipo documenta 4 relés).

### 13.3 Fuera de alcance (declarado en D-017)

- Red de colección de continua / media tensión entre módulos hacia estaciones inversoras y subestación.
- Red de comunicaciones de planta (segmentación de ramales, ubicación de concentradores, redundancia).
- Malla de tierra general de planta y subestación (IEEE Std 80-2013).
- Cálculo de la posición solar del algoritmo de seguimiento (entrada externa al controlador).

---

## 14. CONCLUSIONES

1. El sistema se resuelve con un **módulo tipo eléctrica y mecánicamente completo** (string 5,2 kWp; 332,8 V de tensión de trabajo) que se replica ×588 mediante arquitectura de repetición, sin duplicar planos.
2. El dimensionamiento eléctrico verifica **Ib = 20,55 A ≤ In = 25 A ≤ Iz**, con margen reglamentario frente al fusible de serie del panel (35 A) y aislación ≥ 600 VDC frente a un Voc de 402,2 V.
3. El accionamiento SVH7 es **autoblocante**, por lo que la retención de posición es pasiva y redundante en ambos ejes, sin freno adicional.
4. La **seguridad por viento** (STOW a 20 m/s con prioridad absoluta, bloqueo por finales de carrera y exclusión mutua de sentidos) queda íntegramente representada en los planos de control (D-009, D-011, D-012).
5. El paquete de **18 planos** es editable, trazable, coherente entre hojas y regenerable; los ítems no confirmados por la documentación quedan explícitamente marcados, y los límites del alcance (ingeniería de planta) quedan declarados en el plano de interfaz.

---
*Memoria técnica — Sistema fotovoltaico con seguimiento solar biaxial, 588 módulos × 8 paneles. Revisión A. Documentación eléctrica en QElectroTech (planos D-001 a D-018).*
