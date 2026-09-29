"""sheets.py — Planos D-001…D-018 del proyecto FV 588 módulos.

Cada plano devuelve un FolioSpec. Trazabilidad: los datos provienen de la
documentación técnica del proyecto (Doc1 §x citado en cada texto) o son
CÁLCULO DERIVADO explícito. Lo no confirmado se marca PENDIENTE.

Geometrías usadas (leídas de los .elmt reales):
  dc_terminal(borne_finale): t0=(0,-10)n
  circuit_breaker_2p:  t0 IN.1(-10,-30)  t1 OUT.2(-10,20)  t2 IN.3(10,-30)  t3 OUT.4(10,20)
  proximity_npn(3p):  t0(10,-30)  t1(-10,-30)  t2(0,30)
  push_button/selector_2pos/capacitor/spd_dc: t0(0,-21) t1(0,21)
  ground: t0 PE(0,-11) · dc_motor: t0(0,-30) t1(0,30) · ac_source: t0(0,-20) t1(0,20)
"""

from __future__ import annotations

from .builders import _arrow_down, _block, build_d002, build_d003
from .model import ConnectionSpec, ElementSpec, FolioSpec, ShapeSpec, TextSpec


def _t(x, y, text, size=9):
    return TextSpec(x=x, y=y, text=text, size=size)


def _el(id_, type_, x, y, label=None, info=None) -> ElementSpec:
    return ElementSpec(id=id_, type=type_, x=x, y=y,
                       label=label if label is not None else id_,
                       info=info or {})


def _cn(f, ft, t, tt):
    return ConnectionSpec(from_id=f, from_terminal=ft, to_id=t, to_terminal=tt)


# ---------------------------------------------------------------------------
# D-001 — ARQUITECTURA DEL SISTEMA E ÍNDICE
# ---------------------------------------------------------------------------

def build_d001() -> FolioSpec:
    shapes, texts = [], []
    texts.append(_t(60, 36, "SISTEMA FOTOVOLTAICO CON SEGUIMIENTO SOLAR BIAXIAL", 13))
    texts.append(_t(60, 60, "588 MÓDULOS × 8 PANELES 650 Wp · UBICACIÓN: PUERTO MADRYN, "
                            "CHUBUT (CAP. 1)"))
    for (b, t) in [
        _block(60, 100, 420, 150, "SISTEMA COMPLETO — 588 MÓDULOS (M-001…M-588)"),
        ([], [_arrow_down(230, 155)]),
        _block(60, 168, 420, 218, "ARQUITECTURA DE REPETICIÓN — VER D-018"),
        ([], [_arrow_down(230, 223)]),
        _block(60, 236, 420, 286, "MÓDULO TIPO — ESQUEMAS D-002 A D-016"),
        ([], [_arrow_down(230, 291)]),
        _block(60, 304, 420, 354, "INTERFAZ CON PLANTA — VER D-017"),
        ([], [_arrow_down(230, 359)]),
        _block(60, 372, 420, 422, "COMUNICACIÓN CON SISTEMA SUPERIOR — VER D-013"),
    ]:
        shapes.extend(b)
        texts.extend(t)

    # Índice de planos
    shapes.append(ShapeSpec(480, 90, 960, 540, color="#1f4e79", width=1.5))
    texts.append(_t(492, 100, "ÍNDICE DE PLANOS", 11))
    indice = [
        "D-001  ARQUITECTURA DEL SISTEMA E ÍNDICE",
        "D-002  DIAGRAMA GENERAL DEL MÓDULO TIPO",
        "D-003  STRING FOTOVOLTAICO 8 PANELES",
        "D-004  PROTECCIÓN DC (QF-DC + SPD)",
        "D-005  ALIMENTACIÓN 24 VDC",
        "D-006  EJE DE ELEVACIÓN",
        "D-007  EJE DE AZIMUT",
        "D-008  SENSORES Y ENTRADAS",
        "D-009  SISTEMA DE VIENTO / STOW",
        "D-010  MAPA DE ENTRADAS Y SALIDAS",
        "D-011  DIAGRAMA DE ESTADOS",
        "D-012  SEGURIDAD Y ENCLAVAMIENTOS",
        "D-013  COMUNICACIONES RS485 / IoT",
        "D-014  PUESTA A TIERRA TT",
        "D-015  CANALIZACIONES",
        "D-016  BORNERAS E INTERFACES",
        "D-017  INTERFAZ CON PLANTA",
        "D-018  MÓDULO TIPO × 588",
    ]
    for i, line in enumerate(indice):
        texts.append(_t(492, 130 + i * 22, line, 8))

    texts.append(_t(60, 452, "POTENCIA TOTAL: 588 × 5,2 kWp = 3.057,6 kWp ≈ 3,06 MWp "
                             "(CÁLCULO DERIVADO DEL REQUISITO)"))
    texts.append(_t(60, 474, "SEGURIDAD ESTRUCTURAL: CIRSOC 102-2025 · VIENTO DE DISEÑO "
                             "50 m/s · STOW A 20 m/s (§3.2 / §4.9)"))
    return FolioSpec(title="D-001 — ARQUITECTURA DEL SISTEMA E ÍNDICE DE PLANOS",
                     order=1, texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-004 — PROTECCIÓN DC
# ---------------------------------------------------------------------------

def build_d004() -> FolioSpec:
    els, cns, texts, shapes = [], [], [], []
    texts.append(_t(60, 36, "PROTECCIÓN DC — TABLERO DE CONTINUA", 13))
    texts.append(_t(60, 60, "STRING: 332,8 V VMP / 402,2 V VOC · IB = 20,55 A (§4.1)"))

    # Entradas desde string (D-003) — alineadas con los polos del bipolar
    els.append(_el("D004-X1", "dc_terminal", 250, 80, "X1"))
    els.append(_el("D004-X2", "dc_terminal", 270, 80, "X2"))
    texts.append(_t(295, 66, "X1 (+) / X2 (−) DESDE STRING — VER D-003"))

    # QF-DC bipolar: polos en (250/270, 140 arriba / 190 abajo)
    els.append(_el("D004-QF", "circuit_breaker_2p", 260, 170, "QF-DC",
                   {"designation": "Interruptor termomagnético bipolar DC 25A curva C "
                                  "≥600 VDC (§4.1.4)", "quantity": "1"}))
    cns.append(_cn("D004-X1", 0, "D004-QF", 0))
    cns.append(_cn("D004-X2", 0, "D004-QF", 2))

    # Salidas protegidas
    els.append(_el("D004-X3", "dc_terminal", 250, 330, "X3"))
    els.append(_el("D004-X4", "dc_terminal", 270, 330, "X4"))
    cns.append(_cn("D004-QF", 1, "D004-X3", 0))     # OUT.2 → X3
    cns.append(_cn("D004-QF", 3, "D004-X4", 0))      # OUT.4 → X4
    texts.append(_t(295, 316, "SALIDA PROTEGIDA → INTERFAZ DE PLANTA (VER D-017)"))

    # SPD tipo 2 — sin conexionado interno (no documentado)
    els.append(_el("D004-SPD", "spd_dc", 520, 260, "SPD-DC",
                   {"designation": "Descargador de sobretensiones tipo 2 (§4.1.4)",
                    "quantity": "1"}))
    texts.append(_t(545, 235, "SPD TIPO 2 EN TABLERO DE CONTINUA (§4.1.4)"))
    texts.append(_t(545, 257, "CONEXIONADO SEGÚN FABRICANTE:"))
    texts.append(_t(545, 277, "NO DETALLADO EN LA DOCUMENTACIÓN (PENDIENTE)"))

    # PE del circuito FV
    els.append(_el("D004-PE", "ground", 700, 330, "PE"))
    texts.append(_t(720, 306, "PE 6 mm² (§4.2.4)"))
    texts.append(_t(720, 326, "EQUIPOTENCIALIDAD — VER D-014"))

    texts.extend([
        _t(60, 400, "QF-DC: INTERRUPTOR TERMOMAGNÉTICO BIPOLAR DC · CURVA C · "
                    "IN = 25 A · AISLACIÓN ≥ 600 VDC (§4.1.4)"),
        _t(60, 422, "CRITERIO: IB (20,55 A) ≤ IN ≤ IZ · IN ≤ 35 A (FUSIBLE DE SERIE "
                    "MÁX. DEL PANEL — §4.1.4)"),
        _t(60, 444, "ÚNICO STRING → SIN PROTECCIÓN DE SOBRECORRIENTE POR STRING (§4.1.4)"),
        _t(60, 466, "ENTRADA: D-003 (X1/X2) · SALIDA: D-017 (X3/X4) · PE: D-014"),
    ])
    return FolioSpec(title="D-004 — PROTECCIÓN DC DEL STRING", order=4,
                     elements=els, connections=cns, texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-005 — ALIMENTACIÓN 24 VDC
# ---------------------------------------------------------------------------

def build_d005() -> FolioSpec:
    els, cns, texts = [], [], []
    texts.append(_t(60, 36, "ALIMENTACIÓN 24 VDC — CONTROL Y ACTUADORES", 13))
    texts.append(_t(60, 60, "SEPARACIÓN DE ALIMENTACIÓN DE CONTROL Y DE ACTUADORES "
                            "(§2.5.1 / §4.1.5)"))

    # Fuente 24 VDC
    els.append(_el("D005-FU", "ac_source", 250, 100, "FU-24VDC",
                   {"designation": "Fuente 24 VDC según alimentación de motores (§2.5.1)"}))
    # Alimentación de control (borna directa)
    els.append(_el("D005-XCTRL", "dc_terminal", 500, 80, "X-CTRL"))
    cns.append(_cn("D005-FU", 0, "D005-XCTRL", 0))     # (250,80)→(500,70)
    texts.append(_t(520, 66, "ALIMENTACIÓN DE CONTROL → CTRL-01 — VER D-010"))
    texts.append(_t(520, 86, "SEPARADA DE LA ALIMENTACIÓN DE ACTUADORES"))

    # Protección por eje: F-ELEV (polo A) y F-AZ
    els.append(_el("D005-FE", "circuit_breaker_2p", 260, 220, "F-ELEV",
                   {"designation": "Termomagnético bipolar 24VDC curva C 6 A — eje "
                                  "elevación (§4.1.5)", "quantity": "1"}))
    els.append(_el("D005-FA", "circuit_breaker_2p", 420, 220, "F-AZ",
                   {"designation": "Termomagnético bipolar 24VDC curva C 6 A — eje "
                                  "azimut (§4.1.5)", "quantity": "1"}))
    cns.append(_cn("D005-FU", 1, "D005-FE", 0))    # (250,120)→(250,190)
    cns.append(_cn("D005-FU", 1, "D005-FA", 0))      # (250,120)→(410,190)

    # Salidas a actuadores
    els.append(_el("D005-E1", "dc_terminal", 250, 340, "X-E1"))
    els.append(_el("D005-E2", "dc_terminal", 270, 340, "X-E2"))
    els.append(_el("D005-A1", "dc_terminal", 410, 340, "X-A1"))
    els.append(_el("D005-A2", "dc_terminal", 430, 340, "X-A2"))
    cns.append(_cn("D005-FE", 1, "D005-E1", 0))
    cns.append(_cn("D005-FE", 3, "D005-E2", 0))
    cns.append(_cn("D005-FA", 1, "D005-A1", 0))
    cns.append(_cn("D005-FA", 3, "D005-A2", 0))
    texts.append(_t(300, 330, "→ M-ELEV (+) — VER D-006"))
    texts.append(_t(300, 350, "→ M-ELEV (−)"))
    texts.append(_t(460, 330, "→ M-AZ (+) — VER D-007"))
    texts.append(_t(460, 350, "→ M-AZ (−)"))

    texts.extend([
        _t(60, 420, "F-ELEV / F-AZ: TERMOMAGNÉTICO BIPOLAR 24 VDC · CURVA C · "
                    "IN = 6 A POR EJE (§4.1.5)"),
        _t(60, 442, "CABLE DE ACTUADORES: MULTIPOLAR APANTALLADO 1,5 mm² (IRAM 2183) · "
                    "PE 2,5 mm² (§4.1.5 / §4.2.4)"),
        _t(60, 464, "FU-24VDC SEGÚN ALIMENTACIÓN DE LOS MOTORES SVH7 (§2.5.1)"),
    ])
    return FolioSpec(title="D-005 — ALIMENTACIÓN 24 VDC Y PROTECCIONES", order=5,
                     elements=els, connections=cns, texts=texts)


# ---------------------------------------------------------------------------
# D-006 / D-007 — EJES DE ELEVACIÓN Y AZIMUT (plantilla paramétrica)
# ---------------------------------------------------------------------------

def _axis_sheet(order, title, header, q_plus, plus_desc, q_minus, minus_desc,
                f_label, axis_name, fc_a, fc_b, svh_line2) -> FolioSpec:
    """Plantilla de plano de eje: salidas de relé → protección → SVH7 + FC NPN.

    fc_a/fc_b = (id, label, borne_I, texto descriptivo)
    """
    els, cns, texts, shapes = [], [], [], []
    texts.append(_t(60, 36, header, 13))
    texts.append(_t(60, 60, f"SALIDAS {q_plus} / {q_minus} DEL CTRL-01 → {f_label} → "
                            f"SVH7 — {axis_name} (§4.8 / §4.1.5)"))

    # Bloque del controlador
    b, t = _block(60, 110, 340, 330, "CTRL-01 — DomBusTracker2 (VER D-010)",
                  f"{q_plus} → {plus_desc} · {q_minus} → {minus_desc}")
    shapes.extend(b)
    texts.extend(t)
    texts.append(_t(70, 190, f"ENTRADAS {fc_a[2]} / {fc_b[2]} ← FINALES DE CARRERA"))
    texts.append(_t(70, 212, "ENCLAVAMIENTOS DE SEGURIDAD — VER D-012"))

    # Cadena de salida: bornas Q → F-{eje} (bipolar) → bornas hacia SVH7
    p = f"D{order}-"                      # IDs únicos por plano (etiquetas intactas)
    els.append(_el(f"{p}{q_minus}", "dc_terminal", 370, 150, q_minus))
    els.append(_el(f"{p}{q_plus}", "dc_terminal", 390, 150, q_plus))
    texts.append(_t(240, 140, f"{q_minus} → {minus_desc}"))
    texts.append(_t(415, 140, f"{q_plus} → {plus_desc}"))

    els.append(_el(f"{p}{f_label}", "circuit_breaker_2p", 380, 250, f_label,
                   {"designation": f"Termomagnético bipolar 24VDC curva C 6 A — "
                                  f"{axis_name} (§4.1.5)"}))
    cns.append(_cn(f"{p}{q_minus}", 0, f"{p}{f_label}", 0))   # (370,140)→(370,220)
    cns.append(_cn(f"{p}{q_plus}", 0, f"{p}{f_label}", 2))    # (390,140)→(390,220)

    els.append(_el(f"{p}M1", "dc_terminal", 370, 360, "X-M1"))
    els.append(_el(f"{p}M2", "dc_terminal", 390, 360, "X-M2"))
    cns.append(_cn(f"{p}{f_label}", 1, f"{p}M1", 0))         # (370,280)→(370,350)
    cns.append(_cn(f"{p}{f_label}", 3, f"{p}M2", 0))         # (390,280)→(390,350)
    texts.append(_t(240, 352, f"→ SVH7 {axis_name} (−) — VER D-016"))
    texts.append(_t(415, 352, f"→ SVH7 {axis_name} (+) — VER D-016"))

    # Bloque SVH7 del eje
    b, t = _block(60, 400, 340, 470, f"SVH7 — EJE {axis_name}",
                  svh_line2)
    shapes.extend(b)
    texts.extend(t)

    # Finales de carrera NPN (sensor inductivo 3 terminales, símbolo real)
    for i, fc in enumerate((fc_a, fc_b)):
        sx = 700 + i * 160
        fc_id, fc_label, fc_in, fc_text = fc
        els.append(_el(f"{p}{fc_id}", "proximity_npn", sx, 260, fc_label,
                       {"designation": "Sensor de proximidad NPN NO 3 cables 6–36 VDC "
                                      "(§2.3.2, Anexo 4)"}))
        els.append(_el(f"{p}V{fc_in}", "dc_terminal", sx + 10, 150, "+24V"))
        els.append(_el(f"{p}G{fc_in}", "dc_terminal", sx - 10, 150, "GND"))
        els.append(_el(f"{p}IN{fc_in}", "dc_terminal", sx, 350, fc_in))
        cns.append(_cn(f"{p}V{fc_in}", 0, f"{p}{fc_id}", 0))    # (+24V)
        cns.append(_cn(f"{p}G{fc_in}", 0, f"{p}{fc_id}", 1))   # (GND)
        cns.append(_cn(f"{p}{fc_id}", 2, f"{p}IN{fc_in}", 0))  # señal
    texts.append(_t(560, 400, fc_a[3]))
    texts.append(_t(560, 422, fc_b[3]))
    texts.append(_t(560, 444, "SENSOR NPN SINKING · REFERENCIA COMÚN A GND (§2.3.2)"))
    texts.append(_t(560, 466, "EL FINAL DE CARRERA ENCLAVA EL MOVIMIENTO HACIA SU "
                              "LÍMITE EN CUALQUIER MODO (§4.9.2 — VER D-012)"))
    texts.append(_t(60, 496, f"{q_plus} / {q_minus} MUTUAMENTE EXCLUYENTES — VER D-012"))

    return FolioSpec(title=title, order=order, elements=els, connections=cns,
                    texts=texts, shapes=shapes)


def build_d006() -> FolioSpec:
    return _axis_sheet(
        order=6, title="D-006 — EJE DE ELEVACIÓN",
        header="EJE DE ELEVACIÓN — CONTROL POR RELÉS Q0.0/Q0.1",
        q_plus="Q0.0", plus_desc="ELEVACIÓN + (RL1)",
        q_minus="Q0.1", minus_desc="ELEVACIÓN − (RL2)",
        f_label="F-ELEV", axis_name="ELEVACIÓN",
        fc_a=("FC-ELEV-N", "FC-ELEV-N", "I0.0",
              "FC-ELEV-N → I0.0: FIN DE CARRERA NORTE — ELEVACIÓN MÁXIMA (§4.8.1)"),
        fc_b=("FC-ELEV-S", "FC-ELEV-S", "I0.1",
              "FC-ELEV-S → I0.1: FIN DE CARRERA SUR — ELEVACIÓN MÍNIMA (§4.8.1)"),
        svh_line2="24 VDC · 71:1 · 937 N·m · RETENCIÓN 10,4 kN·m · AUTOBLOQUEANTE "
                  "(§2.2.1 / §4.6)")


def build_d007() -> FolioSpec:
    return _axis_sheet(
        order=7, title="D-007 — EJE DE AZIMUT",
        header="EJE DE AZIMUT — CONTROL POR RELÉS Q0.2/Q0.3",
        q_plus="Q0.2", plus_desc="AZIMUT + (RL3)",
        q_minus="Q0.3", minus_desc="AZIMUT − (RL4)",
        f_label="F-AZ", axis_name="AZIMUT",
        fc_a=("FC-AZ-E", "FC-AZ-E", "I0.2",
              "FC-AZ-E → I0.2: LÍMITE DE GIRO ESTE (§4.8.1)"),
        fc_b=("FC-AZ-O", "FC-AZ-O", "I0.3",
              "FC-AZ-O → I0.3: LÍMITE DE GIRO OESTE (§4.8.1)"),
        svh_line2="24 VDC · 71:1 · TORQUE 937 N·m · INERCIA DESPRECIABLE (§4.5)")


# ---------------------------------------------------------------------------
# D-008 — SENSORES Y ENTRADAS
# ---------------------------------------------------------------------------

def build_d008() -> FolioSpec:
    els, cns, texts, shapes = [], [], [], []
    texts.append(_t(60, 36, "SENSORES Y ENTRADAS — DIGITALES Y ANALÓGICAS", 13))
    texts.append(_t(60, 60, "ALIMENTACIÓN 24 VDC · NPN SINKING · REFERENCIA COMÚN A GND "
                            "(§2.3.2 / §4.8)"))

    # --- Finales de carrera (4 × NPN 3 terminales) ---
    fcs = [
        ("FC-ELEV-N", "I0.0", "FC N — ELEV. MÁXIMA"),
        ("FC-ELEV-S", "I0.1", "FC S — ELEV. MÍNIMA"),
        ("FC-AZ-E", "I0.2", "FC E — AZIMUT"),
        ("FC-AZ-O", "I0.3", "FC O — AZIMUT"),
    ]
    for i, (fc_id, fc_in, fc_desc) in enumerate(fcs):
        x = 100 + i * 160
        els.append(_el(f"D008-{fc_id}", "proximity_npn", x, 260, fc_id,
                       {"designation": "Sensor proximidad NPN NO 3 cables (§4.8.1)"}))
        els.append(_el(f"D008-V{fc_in}", "dc_terminal", x + 10, 180, "+24V"))
        els.append(_el(f"D008-G{fc_in}", "dc_terminal", x - 10, 180, "GND"))
        els.append(_el(f"D008-IN{fc_in}", "dc_terminal", x, 340, fc_in))
        cns.append(_cn(f"D008-V{fc_in}", 0, f"D008-{fc_id}", 0))
        cns.append(_cn(f"D008-G{fc_in}", 0, f"D008-{fc_id}", 1))
        cns.append(_cn(f"D008-{fc_id}", 2, f"D008-IN{fc_in}", 0))
        texts.append(_t(x - 40, 372, fc_desc, 8))

    # --- Pulsadores manuales (I0.4–I0.7) ---
    pbs = [("PB-ELEV-P", "I0.4", "PB ELEV +"), ("PB-ELEV-N", "I0.5", "PB ELEV −"),
           ("PB-AZ-P", "I0.6", "PB AZ +"), ("PB-AZ-N", "I0.7", "PB AZ −")]
    for i, (pb_id, pb_in, pb_desc) in enumerate(pbs):
        x = 100 + i * 160
        els.append(_el(f"D008-{pb_id}", "push_button", x, 440, pb_id,
                       {"designation": "Pulsador manual local (§4.8.1)"}))
        els.append(_el(f"D008-IN{pb_in}", "dc_terminal", x, 525, pb_in))
        cns.append(_cn(f"D008-{pb_id}", 1, f"D008-IN{pb_in}", 0))
        texts.append(_t(x - 40, 552, pb_desc, 8))

    # --- Selector Manual/Automático (I1.0) ---
    els.append(_el("D008-SEL", "selector_2pos", 700, 440, "SEL-AM",
                   {"designation": "Selector Manual/Automático (§4.8.1)"}))
    els.append(_el("D008-INI1.0", "dc_terminal", 700, 525, "I1.0"))
    cns.append(_cn("D008-SEL", 1, "D008-INI1.0", 0))
    texts.append(_t(750, 552, "SEL-AUTO/MAN: I1.0=1 AUTO · I1.0=0 MANUAL (§4.9.1)", 8))

    # --- Bloques de señales analógicas y alarma (columna derecha) ---
    right = [
        ("AN-WIND → AI0: ANEMÓMETRO 3–5 V — VER D-009", 110),
        ("I1.1: ALARMA DE VIENTO (UMBRAL SUPERADO) — VER D-009/D-012", 174),
        ("AI1: SENSOR DE LUZ EJE NORTE/SUR · 0–10 V (§4.8.2)", 238),
        ("AI2: SENSOR DE LUZ EJE ESTE/OESTE · 0–10 V (§4.8.2)", 302),
        ("SENSORES DE LUZ IMPERMEABLES INCLUIDOS EN EL EQUIPO (§2.2.2)", 366),
    ]
    for line, y in right:
        b, t = _block(700, y, 960, y + 40, line)
        shapes.extend(b)
        texts.extend(t)

    texts.append(_t(700, 430, "ENTRADAS DEL CONTROLADOR — VER D-010 (MAPA DE E/S)", 8))
    texts.append(_t(60, 560 - 30, "NUMERACIÓN FÍSICA DE BORNES: PENDIENTE DE VERIFICACIÓN", 8))
    return FolioSpec(title="D-008 — SENSORES Y ENTRADAS", order=8,
                     elements=els, connections=cns, texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-009 — SISTEMA DE VIENTO / STOW
# ---------------------------------------------------------------------------

def build_d009() -> FolioSpec:
    els, cns, texts, shapes = [], [], [], []
    texts.append(_t(60, 36, "SISTEMA DE VIENTO — DETECCIÓN, ALARMA Y POSICIÓN STOW", 13))
    texts.append(_t(60, 60, "FUNCIÓN DE SEGURIDAD ANTE VIENTO EXCESIVO (§2.2.2 / §4.9)"))

    # Bornas + condensador real entre Wind y GND
    els.append(_el("D009-XW", "dc_terminal", 150, 200, "WIND"))
    els.append(_el("D009-CW", "capacitor", 260, 250, "C-WIND",
                   {"designation": "Condensador 100–220 µF entre Wind y GND (§2.2.2)"}))
    els.append(_el("D009-XG", "dc_terminal", 150, 320, "GND"))
    els.append(_el("D009-AI0", "dc_terminal", 360, 200, "AI0"))
    cns.append(_cn("D009-XW", 0, "D009-CW", 0))    # WIND → condensador
    cns.append(_cn("D009-CW", 1, "D009-XG", 0))    # condensador → GND
    cns.append(_cn("D009-XW", 0, "D009-AI0", 0))   # WIND → AI0
    texts.append(_t(60, 166, "SEÑAL DE ANEMÓMETRO: 3–5 V (§2.2.2)"))
    texts.append(_t(290, 235, "C-WIND: 100–220 µF ENTRE WIND Y GND (§2.2.2)"))
    texts.append(_t(390, 166, "→ ENTRADA ANALÓGICA AI0 DEL CTRL-01"))

    # Cadena funcional derecha
    chain = [
        ("AI0: VELOCIDAD DE VIENTO (3–5 V)", 110),
        ("UMBRAL OPERATIVO: VIENTO > 20 m/s (§4.9.1)", 184),
        ("ALARMA DE VIENTO → I1.1 = 1 (§4.8.1)", 258),
        ("INTERRUMPE SEGUIMIENTO → STOW: θ2 = 90° (VER D-011)", 332),
        ("RETORNO: SELECTOR EN AUTO + RETARDO DE SEGURIDAD (§4.9.2)", 406),
    ]
    for i, (line, y) in enumerate(chain):
        b, t = _block(560, y, 960, y + 40, line)
        shapes.extend(b)
        texts.extend(t)
        if i < len(chain) - 1:
            texts.append(_arrow_down(760, y + 44))

    texts.extend([
        _t(60, 430, "EL STOW TIENE PRIORIDAD ABSOLUTA SOBRE AUTOMÁTICO Y MANUAL (§4.9.2)"),
        _t(60, 452, "POSICIÓN STOW: PANELES VERTICALES (θ2 = 90°) — MÍNIMA RESISTENCIA "
                    "AERODINÁMICA (§4.9)"),
        _t(60, 474, "DISEÑO ESTRUCTURAL DE VIENTO: 50 m/s (CIRSOC 102-2025) — VER D-002"),
    ])
    return FolioSpec(title="D-009 — SISTEMA DE VIENTO Y POSICIÓN STOW", order=9,
                     elements=els, connections=cns, texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-010 — MAPA DE ENTRADAS Y SALIDAS
# ---------------------------------------------------------------------------

def build_d010() -> FolioSpec:
    texts, shapes = [], []
    texts.append(_t(60, 36, "MAPA DE ENTRADAS Y SALIDAS — CTRL-01 DomBusTracker2", 13))
    texts.append(_t(60, 60, "ARQUITECTURA DE E/S SEGÚN §4.8 (CONVENCIÓN IEC 61131-3)"))

    shapes.append(ShapeSpec(60, 90, 960, 520, color="#1f4e79", width=1.5))
    shapes.append(ShapeSpec(60, 90, 960, 118, color="#1f4e79", width=1.0,
                            fill="#dbe7f3"))
    texts.append(_t(80, 97, "DIR", 9))
    texts.append(_t(200, 97, "SEÑAL / DESCRIPCIÓN", 9))
    texts.append(_t(560, 97, "ELEMENTO / NOTAS", 9))

    filas = [
        ("I0.0", "FIN DE CARRERA NORTE — ELEVACIÓN MÁXIMA", "FC-ELEV-N (NPN) — VER D-006"),
        ("I0.1", "FIN DE CARRERA SUR — ELEVACIÓN MÍNIMA", "FC-ELEV-S (NPN) — VER D-006"),
        ("I0.2", "FIN DE CARRERA ESTE — AZIMUT", "FC-AZ-E (NPN) — VER D-007"),
        ("I0.3", "FIN DE CARRERA OESTE — AZIMUT", "FC-AZ-O (NPN) — VER D-007"),
        ("I0.4", "PULSADOR MANUAL ELEVACIÓN +", "PB-ELEV+ — VER D-008"),
        ("I0.5", "PULSADOR MANUAL ELEVACIÓN −", "PB-ELEV− — VER D-008"),
        ("I0.6", "PULSADOR MANUAL AZIMUT +", "PB-AZ+ — VER D-008"),
        ("I0.7", "PULSADOR MANUAL AZIMUT −", "PB-AZ− — VER D-008"),
        ("I1.0", "SELECTOR MANUAL / AUTOMÁTICO", "SEL-AUTO/MAN — VER D-008"),
        ("I1.1", "ALARMA DE VIENTO (UMBRAL SUPERADO)", "DERIVADA DE AI0 — VER D-009"),
        ("AI0", "ANEMÓMETRO — VELOCIDAD DE VIENTO", "AN-WIND · 3–5 V — VER D-009"),
        ("AI1", "SENSOR DE LUZ EJE NORTE/SUR", "LUZ N/S · 0–10 V (EN EQUIPO)"),
        ("AI2", "SENSOR DE LUZ EJE ESTE/OESTE", "LUZ E/O · 0–10 V (EN EQUIPO)"),
        ("Q0.0", "RELÉ RL1 — ELEVACIÓN, SENTIDO POSITIVO", "→ M-ELEV — VER D-006"),
        ("Q0.1", "RELÉ RL2 — ELEVACIÓN, SENTIDO NEGATIVO", "→ M-ELEV — VER D-006"),
        ("Q0.2", "RELÉ RL3 — AZIMUT, SENTIDO POSITIVO", "→ M-AZ — VER D-007"),
        ("Q0.3", "RELÉ RL4 — AZIMUT, SENTIDO NEGATIVO", "→ M-AZ — VER D-007"),
    ]
    y = 122
    for dir_, desc, elem in filas:
        texts.append(_t(80, y, dir_, 8))
        texts.append(_t(200, y, desc, 8))
        texts.append(_t(560, y, elem, 8))
        y += 23

    texts.append(_t(60, 532, "Q0.4 (RL5 ZUMBADOR) / Q0.5 (RL6 RESERVA): ARQUITECTURA "
                             "GENÉRICA §4.8.3 — NO CONFIRMADAS COMO SALIDAS FÍSICAS "
                             "(EQUIPO: 4 RELÉS) — PENDIENTE DE VERIFICACIÓN", 8))
    return FolioSpec(title="D-010 — MAPA DE ENTRADAS Y SALIDAS", order=10,
                     texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-011 — DIAGRAMA DE ESTADOS
# ---------------------------------------------------------------------------

def build_d011() -> FolioSpec:
    texts, shapes = [], []
    texts.append(_t(60, 36, "DIAGRAMA DE ESTADOS DEL CONTROL DE SEGUIMIENTO", 13))
    texts.append(_t(60, 60, "CUATRO ESTADOS SEGÚN §4.9.1 · TRANSICIONES POR ENTRADAS "
                            "DIGITALES Y ANALÓGICAS"))

    b, t = _block(60, 110, 360, 170, "ESTADO 0 — REPOSO / INICIALIZACIÓN",
                  "VERIFICA FINALES DE CARRERA I0.0–I0.3 · HOMOLOGA POSICIÓN (§4.9.1)")
    shapes.extend(b); texts.extend(t)
    texts.append(_arrow_down(200, 175))
    texts.append(_t(220, 172, "INICIALIZACIÓN COMPLETA →"))

    b, t = _block(60, 190, 360, 250, "ESTADO 1 — SEGUIMIENTO AUTOMÁTICO",
                  "I1.0 = 1 · I1.1 = 0 · CINEMÁTICA INVERSA → Q0.0–Q0.3 (§4.9.1)")
    shapes.extend(b); texts.extend(t)

    b, t = _block(60, 330, 360, 390, "ESTADO 3 — MODO MANUAL",
                  "I1.0 = 0 · PULSADORES I0.4–I0.7 · ENCLAVADO POR FC (§4.9.1)")
    shapes.extend(b); texts.extend(t)

    b, t = _block(500, 110, 840, 170, "ESTADO 2 — STOW / POSICIÓN DE SEGURIDAD",
                  "θ2 = 90° · AI0 > 20 m/s → I1.1 = 1 (§4.9.1)")
    shapes.extend(b); texts.extend(t)
    texts.append(_t(500, 180, "ACCESIBLE DESDE E0 / E1 / E3 CON VIENTO > UMBRAL — "
                              "PRIORIDAD ABSOLUTA (§4.9.2)", 8))

    # Transiciones
    texts.append(_t(370, 205, "→", 10))
    texts.append(_t(386, 202, "SELECTOR → MANUAL (I1.0 = 0)", 8))
    texts.append(_t(370, 260, "←", 10))
    texts.append(_t(386, 257, "SELECTOR → AUTOMÁTICO (I1.0 = 1)", 8))
    texts.append(_t(370, 135, "→", 10))
    texts.append(_t(386, 132, "VIENTO > 20 m/s (AI0 → I1.1 = 1)", 8))
    texts.append(_t(370, 290, "→", 10))
    texts.append(_t(386, 287, "VIENTO > 20 m/s (DESDE MANUAL)", 8))
    texts.append(_t(370, 300, "←", 10))
    texts.append(_t(386, 317, "CESÓ ALARMA + RETARDO + SELECTOR EN AUTO (§4.9.2)", 8))

    texts.append(_t(500, 220, "PERMANECE EN E2 MIENTRAS I1.1 = 1 ", 8))
    texts.append(_t(500, 240, "MÁS RETARDO DE SEGURIDAD TRAS EL CESE (§4.9.1)", 8))
    texts.append(_t(60, 440, "PRIORIDAD: E2 (STOW) SOBRE E1 (AUTOMÁTICO) Y E3 (MANUAL) — "
                             "ENCLAVAMIENTO DE MÁXIMA PRIORIDAD (§4.9.2)"))
    texts.append(_t(60, 462, "LOS FINALES DE CARRERA BLOQUEAN EL MOVIMIENTO HACIA SU "
                             "LÍMITE EN CUALQUIER MODO (§4.9.2 — VER D-012)"))
    return FolioSpec(title="D-011 — DIAGRAMA DE ESTADOS", order=11,
                     texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-012 — SEGURIDAD Y ENCLAVAMIENTOS
# ---------------------------------------------------------------------------

def build_d012() -> FolioSpec:
    texts, shapes = [], []
    texts.append(_t(60, 36, "SEGURIDAD Y ENCLAVAMIENTOS DEL CONTROL", 13))
    texts.append(_t(60, 60, "ENCLAVAMIENTOS VÁLIDOS EN CUALQUIER ESTADO (§4.9.2)"))

    b, t = _block(60, 100, 960, 150, "STOW (ESTADO 2) — PRIORIDAD MÁXIMA SOBRE "
                                     "SEGUIMIENTO Y MANUAL")
    shapes.extend(b); texts.extend(t)

    reglas = [
        "1) FINAL DE CARRERA (I0.0–I0.3) IMPIDE EL MOVIMIENTO HACIA EL LÍMITE "
        "CORRESPONDIENTE EN CUALQUIER MODO",
        "2) ALARMA DE VIENTO (I1.1) INTERRUMPE EL SEGUIMIENTO E INICIA STOW",
        "3) RETORNO TRAS STOW: SOLO CON SELECTOR EN AUTOMÁTICO — SIN REINICIOS "
        "NO SUPERVISADOS",
        "4) AUTOBLOQUEO MECÁNICO SVH7 (TORNILLO SINFIN 71:1): RETENCIÓN 10,4 kN·m "
        "— SIN FRENO ADICIONAL (§4.6)",
    ]
    y = 170
    for r in reglas:
        b, t = _block(60, y, 620, y + 50, r)
        shapes.extend(b); texts.extend(t)
        y += 70

    # Pares mutuamente excluyentes
    b, t = _block(660, 170, 800, 220, "Q0.0 — ELEVACIÓN +")
    shapes.extend(b); texts.extend(t)
    b, t = _block(820, 170, 960, 220, "Q0.1 — ELEVACIÓN −")
    shapes.extend(b); texts.extend(t)
    texts.append(_t(660, 228, "MUTUAMENTE EXCLUYENTES (ENCLAVAMIENTO LÓGICO — §4.9.2)", 8))
    b, t = _block(660, 250, 800, 300, "Q0.2 — AZIMUT +")
    shapes.extend(b); texts.extend(t)
    b, t = _block(820, 250, 960, 300, "Q0.3 — AZIMUT −")
    shapes.extend(b); texts.extend(t)
    texts.append(_t(660, 308, "MUTUAMENTE EXCLUYENTES (ENCLAVAMIENTO LÓGICO — §4.9.2)", 8))
    texts.append(_t(660, 330, "LOS DOS SENTIDOS DE UN MISMO EJE NO PUEDEN ACTIVARSE "
                               "SIMULTÁNEAMENTE (§4.9.2)", 8))

    texts.append(_t(60, 470, "EL MOVIMIENTO HACIA STOW SE EJECUTA AUMENTANDO θ2 HASTA "
                             "90° INDEPENDIENTEMENTE DEL MODO (§4.9.1)"))
    return FolioSpec(title="D-012 — SEGURIDAD Y ENCLAVAMIENTOS", order=12,
                     texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-013 — COMUNICACIONES
# ---------------------------------------------------------------------------

def build_d013() -> FolioSpec:
    els, texts, shapes = [], [], []
    texts.append(_t(60, 36, "COMUNICACIONES — RS485 / IoT", 13))
    texts.append(_t(60, 60, "DomBusTracker2 → USR-DR404 → Ethernet/Wi-Fi → USR-W610 → "
                            "Domoticz (§2.4 / §2.5)"))

    b, t = _block(60, 110, 300, 190, "CTRL-01 — DomBusTracker2",
                  "BORNES A / B DEL BUS RS485 (§2.5.1)")
    shapes.extend(b); texts.extend(t)

    # Bornera RS485
    els.append(_el("D013-A", "dc_terminal", 400, 140, "A"))
    els.append(_el("D013-B", "dc_terminal", 480, 140, "B"))
    els.append(_el("D013-SH", "dc_terminal", 560, 140, "SH"))
    texts.append(_t(388, 166, "A", 8))
    texts.append(_t(468, 166, "B", 8))
    texts.append(_t(548, 166, "APANTALLADO (2×0,22 mm — FIG. 2.4)", 8))
    texts.append(_t(388, 200, "NUMERACIÓN DE BORNES: PENDIENTE DE VERIFICACIÓN — "
                              "VER D-016", 8))

    b, t = _block(400, 240, 700, 300, "USR-DR404 — CONCENTADOR",
                  "RS485 → ETHERNET/WI-FI · HASTA 32 DISPOSITIVOS · < 1200 m (§2.4.1)")
    shapes.extend(b); texts.extend(t)
    texts.append(_arrow_down(550, 304))
    b, t = _block(400, 318, 700, 368, "ETHERNET / WI-FI")
    shapes.extend(b); texts.extend(t)
    texts.append(_arrow_down(550, 372))
    b, t = _block(400, 386, 700, 446, "USR-W610 — SERVIDOR SERIAL",
                  "RS232/RS485 → RJ45 / WI-FI 2,4 GHz · 280 m · 24 DISP. (§2.4.4)")
    shapes.extend(b); texts.extend(t)
    texts.append(_t(710, 405, "→", 10))
    b, t = _block(730, 386, 960, 446, "DOMOTICZ / SISTEMA SUPERIOR",
                  "MONITOREO REMOTO EN TIEMPO REAL (§2.4.5)")
    shapes.extend(b); texts.extend(t)

    texts.extend([
        _t(60, 240, "BUS DEL MÓDULO: CTRL-01 → TB-RS485 (A/B)"),
        _t(60, 262, "TERMINACIÓN: RESISTENCIA DE 120 Ω EN LOS EXTREMOS DEL BUS (§2.5.1)"),
        _t(60, 284, "VELOCIDAD DEL BUS: 115200 bps (§2.5.3)"),
        _t(60, 306, "PROTOCOLO MODBUS MAESTO-ESCLAVO (§2.4.1)"),
        _t(60, 470, "RED DE COMUNICACIONES A NIVEL DE PLANTA: NO DISEÑADA — FUERA DEL "
                    "ALCANCE DE LA DOCUMENTACIÓN (§2.4.1) — VER D-017"),
        _t(60, 492, "TOPOLOGÍA PARA 588 MÓDULOS: PENDIENTE DE INGENIERÍA DE PLANTA"),
    ])
    return FolioSpec(title="D-013 — COMUNICACIONES RS485 / IoT", order=13,
                     elements=els, texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-014 — PUESTA A TIERRA
# ---------------------------------------------------------------------------

def build_d014() -> FolioSpec:
    els, texts, shapes = [], [], []
    texts.append(_t(60, 36, "PUESTA A TIERRA DEL MÓDULO — ESQUEMA TT", 13))
    texts.append(_t(60, 60, "ELECTRODOS DE DISPERSIÓN + EQUIPOTENCIALIDAD DE MASAS "
                            "(§4.2)"))

    for i, (x, name) in enumerate([(180, "ESTRUCTURA — BASTIDORES + VIGAS"),
                                   (460, "COLUMNA"),
                                   (740, "GABINETE CTRL-01 + TABLERO DC")]):
        b, t = _block(x - 120, 110, x + 120, 160, name)
        shapes.extend(b); texts.extend(t)
        texts.append(_arrow_down(x, 166))

    b, t = _block(60, 184, 860, 234, "CONDUCTOR DE PROTECCIÓN PE — BARRA DE "
                                     "EQUIPOTENCIALIDAD DEL MÓDULO",
                  "PE 6 mm² (CIRCUITO FV) · PE 2,5 mm² (24 VDC) — §4.2.4")
    shapes.extend(b); texts.extend(t)
    texts.append(_arrow_down(450, 240))

    b, t = _block(60, 256, 860, 306, "SISTEMA DE TIERRA LOCAL — ESQUEMA TT (§4.2.1)")
    shapes.extend(b); texts.extend(t)
    texts.append(_arrow_down(450, 312))

    # 8 jabalinas (símbolo real de tierra)
    shapes.append(ShapeSpec(60, 340, 900, 470, color="#7f7f7f", dash=True))
    texts.append(_t(70, 350, "8 × JABALINA DE ACERO COBRADO · L = 1,5 m · Ø 5/8″ · "
                             "SEPARACIÓN s = L = 1,5 m · INTERCONECTADAS CON CONDUCTOR "
                             "DE COBRE DESNUDO (§4.2.3)", 8))
    for i in range(8):
        x = 100 + i * 100
        els.append(_el(f"E{i+1}", "ground", x, 400, f"E{i+1}"))

    texts.extend([
        _t(60, 490, "TRATAMIENTO QUÍMICO DEL TERRENO: BENTONITA SÓDICA / GEL "
                    "ELECTROLÍTICO (−30 A 50 % ρ) — §4.2.3"),
        _t(60, 512, "VERIFICAR CON TELURÍMETRO · OBJETIVO DE DISEÑO ≤ 10 Ω (§4.2.2)"),
        _t(60, 534, "MALLA GENERAL DE PLANTA: FUERA DEL ALCANCE (IEEE 80) — VER D-017", 8),
    ])
    return FolioSpec(title="D-014 — PUESTA A TIERRA DEL MÓDULO (TT)", order=14,
                     elements=els, texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-015 — CANALIZACIONES
# ---------------------------------------------------------------------------

def build_d015() -> FolioSpec:
    texts, shapes = [], []
    texts.append(_t(60, 36, "FILOSOFÍA DE CANALIZACIÓN — SEGREGACIÓN DE CIRCUITOS", 13))
    texts.append(_t(60, 60, "CONDUCTOS INDEPENDIENTES PARA POTENCIA, CONTROL Y SEÑAL "
                            "(§4.3 / AEA 90364-5)"))

    caños = [
        (110, "#e8f5e9", "#1e7d32", "CAÑO 1 — CIRCUITO DE CONTINUA (POTENCIA)",
         "2 × H1Z2Z2-K 6 mm² (+ / − DEL STRING) + PE 6 mm² · PVC PESADO Ø 20 mm "
         "IRAM 2206-3 (§4.1.3 / §4.2.4 / §4.3.3)",
         "TRAMO: PANELES → TABLERO DE CONTINUA"),
        (230, "#e8f0f8", "#1f4e79", "CAÑO 2 — CONTROL / ACCIONAMIENTO 24 VDC",
         "MULTIPOLAR APANTALLADO 1,5 mm² (IRAM 2183) + PE 2,5 mm² (§4.1.5)",
         "TRAMO: FUENTE → F-ELEV / F-AZ → ACTUADORES SVH7"),
        (350, "#fdf3e3", "#b26a00", "CAÑO 3 — SEÑAL / COMUNICACIÓN",
         "PAR APANTALLADO RS485 2 × 0,22 mm + SEÑALES ANALÓGICAS AI0–AI2 (§2.5.1)",
         "TRAMO: SENSORES / GATEWAY → GABINETE CTRL-01"),
    ]
    for y, fill, color, l1, l2, l3 in caños:
        shapes.append(ShapeSpec(60, y, 960, y + 90, color=color, width=1.5, fill=fill))
        texts.append(_t(75, y + 8, l1))
        texts.append(_t(75, y + 30, l2, 8))
        texts.append(_t(75, y + 52, l3, 8))

    texts.extend([
        _t(60, 470, "SEGREGACIÓN POTENCIA / CONTROL / SEÑAL EN CONDUCTOS "
                    "INDEPENDIENTES PARA REDUCIR INTERFERENCIAS (§4.3.3)"),
        _t(60, 492, "FACTOR DE RELLENO MÁXIMO 35 % DE LA SECCIÓN INTERNA PARA "
                    "≥ 3 CONDUCTORES (§4.3.1)"),
    ])
    return FolioSpec(title="D-015 — CANALIZACIONES", order=15,
                     texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-016 — BORNERAS E INTERFACES
# ---------------------------------------------------------------------------

def build_d016() -> FolioSpec:
    els, texts, shapes = [], [], []
    texts.append(_t(60, 36, "BORNERAS E INTERFACES DEL MÓDULO", 13))
    texts.append(_t(60, 60, "ETIQUETAS POR SEÑAL / FUNCIÓN — VER D-002 / D-004 / "
                            "D-013"))

    # TB-DC
    shapes.append(ShapeSpec(60, 100, 400, 250, color="#1e7d32", width=1.5))
    texts.append(_t(70, 108, "TB-DC — BORNERA DE CONTINUA", 10))
    for i, (x, lab) in enumerate([(110, "X1+"), (190, "X2−"), (270, "PE")]):
        els.append(_el(f"TBDC{i}", "dc_terminal", x, 200, lab))
    texts.append(_t(70, 225, "STRING (D-003) · PROTECCIÓN (D-004) · PLANTA (D-017)", 8))

    # TB-CTRL entradas
    shapes.append(ShapeSpec(460, 100, 960, 250, color="#1f4e79", width=1.5))
    texts.append(_t(470, 108, "TB-CTRL — ENTRADAS (SENSORES / ANALÓGICAS)", 10))
    in_labels = ["+24V", "GND", "I0.0", "I0.1", "I0.2", "I0.3", "AI0", "AI1", "AI2"]
    for i, lab in enumerate(in_labels):
        els.append(_el(f"TBCI{i}", "dc_terminal", 500 + i * 45, 200, lab))
    texts.append(_t(470, 225, "FC NPN I0.0–I0.3 (D-006/D-007/D-008) · AI0–AI2 "
                              "(D-009/§4.8.2)", 8))

    # TB-CTRL salidas
    shapes.append(ShapeSpec(460, 280, 960, 400, color="#1f4e79", width=1.5))
    texts.append(_t(470, 288, "TB-CTRL — SALIDAS A ACTUADORES (DESDE F-ELEV / F-AZ)", 10))
    for i, lab in enumerate(["Q0.0", "Q0.1", "Q0.2", "Q0.3"]):
        els.append(_el(f"TBCO{i}", "dc_terminal", 500 + i * 60, 350, lab))
    texts.append(_t(470, 375, "→ M-ELEV / M-AZ (SVH7) — VER D-005/D-006/D-007", 8))

    # TB-RS485
    shapes.append(ShapeSpec(60, 280, 400, 400, color="#b26a00", width=1.5))
    texts.append(_t(70, 288, "TB-RS485 — COMUNICACIÓN", 10))
    for i, lab in enumerate(["A", "B", "SH"]):
        els.append(_el(f"TBRS{i}", "dc_terminal", 110 + i * 80, 350, lab))
    texts.append(_t(70, 375, "BUS 2 × 0,22 mm APANTALLADO — VER D-013", 8))

    texts.extend([
        _t(60, 430, "NUMERACIÓN FÍSICA DE TERMINALES DEL DISPOSITIVO: NO DOCUMENTADA — "
                    "PENDIENTE DE VERIFICACIÓN (SEÑALES SEGÚN §2.5.1 / §4.8)"),
        _t(60, 452, "LAS ETIQUETAS INDICAN SEÑAL / FUNCIÓN, NO NÚMEROS DE BORNE"),
    ])
    return FolioSpec(title="D-016 — BORNERAS E INTERFACES", order=16,
                     elements=els, texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-017 — INTERFAZ CON PLANTA
# ---------------------------------------------------------------------------

def build_d017() -> FolioSpec:
    texts, shapes = [], []
    texts.append(_t(60, 36, "INTERFAZ DEL MÓDULO CON EL SISTEMA DE NIVEL SUPERIOR", 13))
    texts.append(_t(60, 60, "QUÉ SALE DEL MÓDULO Y QUÉ REQUIERE INGENIERÍA DE PLANTA"))

    b, t = _block(60, 100, 400, 160, "MÓDULO TIPO — ESQUEMAS D-002 A D-016")
    shapes.extend(b); texts.extend(t)

    # Cadena DC
    b, t = _block(60, 200, 400, 250, "SALIDA DC PROTEGIDA — TB-DC: X1+ / X2− / PE "
                                     "(D-004 / D-016)")
    shapes.extend(b); texts.extend(t)
    texts.append(_arrow_down(230, 254))
    shapes.append(ShapeSpec(60, 270, 400, 350, color="#c0392b", width=1.5,
                            dash=True))
    texts.append(_t(70, 280, "INTERFAZ DE PLANTA — RED DE COLECCIÓN DC", 9))
    texts.append(_t(70, 300, "FUERA DEL ALCANCE DE LA DOCUMENTACIÓN (§4.1)", 8))
    texts.append(_t(70, 320, "REQUIERE INGENIERÍA DE PLANTA", 8))

    # Cadena comunicación
    b, t = _block(460, 200, 800, 250, "RS485 — TB-RS485: A / B / SH (D-013 / D-016)")
    shapes.extend(b); texts.extend(t)
    texts.append(_arrow_down(630, 254))
    shapes.append(ShapeSpec(460, 270, 800, 350, color="#c0392b", width=1.5,
                            dash=True))
    texts.append(_t(470, 280, "INTERFAZ DE COMUNICACIÓN — RED DE PLANTA", 9))
    texts.append(_t(470, 300, "NO DISEÑADA EN LA DOCUMENTACIÓN (§2.4.1)", 8))
    texts.append(_t(470, 320, "CONCENTRADORES USR-DR404: ~19 RAMALES DE 32 PARA 588 "
                               "MÓDULOS (CÁLCULO DERIVADO)", 8))

    # Cadena tierra
    b, t = _block(60, 380, 400, 430, "TIERRA LOCAL TT — 8 JABALINAS (D-014)")
    shapes.extend(b); texts.extend(t)
    texts.append(_arrow_down(230, 434))
    shapes.append(ShapeSpec(60, 450, 400, 520, color="#c0392b", width=1.5, dash=True))
    texts.append(_t(70, 460, "EQUIPOTENCIALIDAD CON MALLA GENERAL", 9))
    texts.append(_t(70, 480, "FUERA DEL ALCANCE — IEEE 80 (§4.2.4)", 8))

    texts.append(_t(460, 380, "LO QUE SALE DEL MÓDULO: DC PROTEGIDO (332,8 / 402,2 V) · "
                              "BUS RS485 · TIERRA LOCAL"))
    texts.append(_t(460, 404, "LA CONEXIÓN ENTRE MÓDULOS (COLECCIÓN DC Y RED DE "
                              "COMUNICACIÓN) CORRESPONDE A LA ETAPA DE INGENIERÍA "
                              "DE PLANTA", 8))
    texts.append(_t(460, 428, "ESTE PLANO DELIMITA EL ALCANCE: MÓDULO TIPO (D-002…D-016) "
                              "↔ SISTEMA DE PLANTA", 8))
    return FolioSpec(title="D-017 — INTERFAZ CON PLANTA", order=17,
                     texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# D-018 — MÓDULO TIPO × 588
# ---------------------------------------------------------------------------

def build_d018() -> FolioSpec:
    texts, shapes = [], []
    texts.append(_t(60, 36, "MÓDULO TIPO × 588 — INSTANCIAS DEL MÓDULO TIPO", 13))
    texts.append(_t(60, 60, "CADA MÓDULO (M-001 … M-588) SE CONSTRUYE CON LOS ESQUEMAS "
                            "D-002 A D-017 — NO SE DUPLICAN PLANOS"))

    # 21 celdas de 28 módulos (21 × 28 = 588)
    per = 28
    for k in range(21):
        start = k * per + 1
        end = min((k + 1) * per, 588)
        col, row = k % 7, k // 7
        x = 60 + col * 135
        y = 120 + row * 90
        b, t = _block(x, y, x + 125, y + 70,
                      f"M-{start:03d} … M-{end:03d}",
                      "D-002…D-017")
        shapes.extend(b)
        texts.extend(t)

    texts.extend([
        _t(60, 420, "TOTAL: 588 MÓDULOS · 21 GRUPOS × 28 INSTANCIAS DEL MÓDULO TIPO"),
        _t(60, 442, "POTENCIA: 588 × 8 × 650 Wp = 3.057.600 Wp ≈ 3,06 MWp "
                    "(CÁLCULO DERIVADO DEL REQUISITO)"),
        _t(60, 464, "REFERENCIA CRUZADA: D-001 (ÍNDICE) · D-002 (MÓDULO TIPO) · "
                    "D-017 (INTERFAZ)"),
        _t(60, 486, "EL DISEÑO DEL MÓDULO TIPO ES EL DE D-002 A D-016 · CUALQUIER "
                    "INSTANCIA HEREDA LA MISMA INGENIERÍA"),
    ])
    return FolioSpec(title="D-018 — MÓDULO TIPO × 588", order=18,
                     texts=texts, shapes=shapes)


# ---------------------------------------------------------------------------
# Ensamblado completo
# ---------------------------------------------------------------------------

def build_all() -> list[FolioSpec]:
    """Los 18 planos en orden D-001…D-018."""
    return [
        build_d001(),
        build_d002(),
        build_d003(),
        build_d004(), build_d005(), build_d006(), build_d007(),
        build_d008(), build_d009(), build_d010(), build_d011(), build_d012(),
        build_d013(), build_d014(), build_d015(), build_d016(), build_d017(),
        build_d018(),
    ]
