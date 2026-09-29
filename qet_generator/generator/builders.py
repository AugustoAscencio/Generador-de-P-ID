"""builders.py — Plantillas paramétricas (FASE 11).

Filosofía del proyecto: **MÓDULO TIPO × 588 MÓDULOS**. Nunca se escriben 588
circuitos: el módulo tipo se define UNA vez (aquí) y se instancia N veces.

⚠ REGLA DE INGENIERÍA (AGENTS.md nº2 y nº3): los valores técnicos incluidos
en estas plantillas son SUPUESTOS ESTRUCTURALES, pendientes de la
especificación técnica maestra del cliente. Se marcan "SUPUESTO" explícitamente.
Requisito vigente: 588 módulos × 8 paneles (discrepancia 588/1539 registrada).

Geometrías usadas (verificadas en los .elmt reales de la biblioteca):
  - pv_cell:            t0=w(-5,6)   t1=w(-5,12)  t2=e(5,9)    t3=e(5,3)
  - circuit_breaker_1p: t0=n(0,-30)  t1=s(0,20)
  - ac_source:          t0=n(0,-20)  t1=s(0,20)
  - lamp:               t0=A1(0,-20) t1=A2(0,20)
  - dc_terminal:        t0=n(0,-10)
"""

from __future__ import annotations

from .model import ConnectionSpec, ElementSpec, FolioSpec, ShapeSpec, TextSpec


def _id(module: str, name: str) -> str:
    """ID único en todo el proyecto: 'M001-PV3' o 'PV3' sin módulo."""
    return f"{module}-{name}" if module else name


def create_pv_string(count: int = 8, x0: float = 60, y: float = 150,
                     dx: float = 120, module: str = "",
                     label_base: str = "PV") -> tuple[list, list]:
    """String FV en serie: PV1 → PV2 → … → PVn (t2 este → t0 oeste).

    Devuelve (elements, connections) con IDs prefijados por módulo.
    """
    elements, connections = [], []
    prev = None
    for i in range(1, count + 1):
        eid = _id(module, f"{label_base}{i}")
        elements.append(ElementSpec(
            id=eid, type="pv_cell", x=x0 + (i - 1) * dx, y=y,
            label=f"{label_base}{i}",
            info={"designation": f"Panel FV 650Wp (SUPUESTO - doc. técnico: 625-650Wp)"},
        ))
        if prev is not None:
            connections.append(ConnectionSpec(
                from_id=prev, from_terminal=2, to_id=eid, to_terminal=0))
        prev = eid
    return elements, connections


def create_dc_protection(x: float = 905, y: float = 250, module: str = "",
                         label: str = "QDC1") -> tuple[list, list]:
    """Protección DC de salida del string + borne de salida.

    El borne queda y_borne = y + 80 debajo del disyuntor.
    Devuelve (elements, connections). El llamador conecta el último panel
    a la terminal t0 del disyuntor (posición dependiente del layout).
    """
    q_id = _id(module, label)
    x_id = _id(module, "X1")
    elements = [
        ElementSpec(id=q_id, type="circuit_breaker_1p", x=x, y=y, label=label,
                    info={"designation": "Protección DC string (SUPUESTO - pendiente doc.)",
                          "quantity": "1"}),
        ElementSpec(id=x_id, type="dc_terminal", x=x, y=y + 80, label="X1"),
    ]
    connections = [ConnectionSpec(from_id=q_id, from_terminal=1,
                                   to_id=x_id, to_terminal=0)]
    return elements, connections


def create_aux_24vdc(module: str = "", x: float = 200, y: float = 100,
                     dx_lamp: float = 150) -> tuple[list, list]:
    """Esqueleto auxiliar 24VDC: fuente → protección → indicador → borne.

    ⚠ ESTRUCTURA SUPUESTA: solo demuestra la arquitectura del folio auxiliar.
    Los componentes reales (DomBusTracker2, actuadores, sensores NPN,
    anemómetro, RS485, USR-DR404/W610) se incorporarán cuando exista el
    documento técnico maestro y/o símbolos adecuados.
    """
    fu_id = _id(module, "FU24V")
    f_id = _id(module, "F24")
    h_id = _id(module, "H1")
    x_id = _id(module, "X2")
    elements = [
        ElementSpec(id=fu_id, type="ac_source", x=x, y=y, label="FU24V",
                    info={"designation": "Fuente 24VDC (SUPUESTO)"}),
        ElementSpec(id=f_id, type="circuit_breaker_1p", x=x, y=y + 120, label="F24"),
        ElementSpec(id=h_id, type="lamp", x=x + dx_lamp, y=y + 200, label="H1",
                    info={"designation": "Indicador (SUPUESTO)"}),
        ElementSpec(id=x_id, type="dc_terminal", x=x + dx_lamp, y=y + 280, label="X2"),
    ]
    connections = [
        ConnectionSpec(from_id=fu_id, from_terminal=1, to_id=f_id, to_terminal=0),
        ConnectionSpec(from_id=f_id, from_terminal=1, to_id=h_id, to_terminal=0),
        ConnectionSpec(from_id=h_id, from_terminal=1, to_id=x_id, to_terminal=0),
    ]
    return elements, connections


def build_module_folios(module: str = "M001", panel_count: int = 8) -> list[FolioSpec]:
    """MÓDULO TIPO completo: folio 1 (string FV + DC) y folio 2 (aux 24VDC).

    Este es el bloque que se instanciará × 588 (cada módulo con su prefijo).
    """
    # --- folio 1: string + protección DC ---
    pv_elements, pv_connections = create_pv_string(
        count=panel_count, module=module)
    dc_elements, dc_connections = create_dc_protection(module=module)
    # último panel (t3, este) → disyuntor (t0, norte)
    last_panel = _id(module, f"PV{panel_count}")
    pv_connections.append(ConnectionSpec(
        from_id=last_panel, from_terminal=3,
        to_id=_id(module, "QDC1"), to_terminal=0))

    folio1 = FolioSpec(
        title=f"{module} - String FV {panel_count} paneles + protección DC",
        order=1,
        elements=pv_elements + dc_elements,
        connections=pv_connections + dc_connections,
        texts=[
            TextSpec(x=60, y=60,
                     text=f"{module} - STRING FV: {panel_count} paneles en serie "
                          f"-> proteccion DC -> borne de salida"),
            TextSpec(x=935, y=380,
                     text="X1 = salida string hacia proteccion DC"),
        ],
    )

    # --- folio 2: auxiliar 24VDC (esqueleto SUPUESTO) ---
    aux_elements, aux_connections = create_aux_24vdc(module=module)
    folio2 = FolioSpec(
        title=f"{module} - Auxiliar 24VDC (estructura supuesta)",
        order=2,
        elements=aux_elements,
        connections=aux_connections,
        texts=[
            TextSpec(x=60, y=480,
                     text="ESTRUCTURA SUPUESTA - pendiente del documento tecnico: "
                          "DomBusTracker2, actuadores azimut/elevacion, sensores NPN, "
                          "anemometro, RS485, USR-DR404/W610, PE, borneras"),
        ],
    )

    return [folio1, folio2]


def folio_to_dict(folio: FolioSpec) -> dict:
    """Serializa un FolioSpec a dict JSON (formato 'diagrams')."""
    def el_to_dict(el: ElementSpec) -> dict:
        d = {"id": el.id, "type": el.type, "x": el.x, "y": el.y}
        if el.label is not None:
            d["label"] = el.label
        if el.orientation:
            d["orientation"] = el.orientation
        if el.info:
            d["info"] = dict(el.info)
        return d

    def tx_to_dict(t: TextSpec) -> dict:
        d = {"x": t.x, "y": t.y, "text": t.text}
        if t.size != 9:
            d["size"] = t.size
        if t.rotation:
            d["rotation"] = t.rotation
        return d

    def sh_to_dict(s: ShapeSpec) -> dict:
        d = {"x1": s.x1, "y1": s.y1, "x2": s.x2, "y2": s.y2}
        if s.fill:
            d["fill"] = s.fill
        if s.dash:
            d["dash"] = True
        if s.color != "#004080":
            d["color"] = s.color
        if s.width != 1.0:
            d["width"] = s.width
        return d

    return {
        "title": folio.title,
        "order": folio.order,
        "elements": [el_to_dict(el) for el in folio.elements],
        "connections": [{"from": c.from_id, "from_terminal": c.from_terminal,
                         "to": c.to_id, "to_terminal": c.to_terminal}
                        for c in folio.connections],
        "texts": [tx_to_dict(t) for t in folio.texts],
        "shapes": [sh_to_dict(s) for s in folio.shapes],
    }


# ============================================================================
# HOJAS DEL PROYECTO FV 588 MÓDULOS (fuente: los 2 MD del cliente)
# Trazabilidad: cada valor procede del documento técnico (Doc1) o del
# requisito del cliente (588 módulos). Los SUPUESTOS/PENDIENTES se marcan.
# ============================================================================

def _block(x1, y1, x2, y2, line1, line2="", fill="#e8f0f8",
           color="#1f4e79") -> tuple[list, list]:
    """Bloque funcional: rectángulo + 2 líneas de texto dentro."""
    items_shapes = [ShapeSpec(x1=x1, y1=y1, x2=x2, y2=y2,
                              color=color, width=1.5, fill=fill)]
    items_texts = [TextSpec(x=x1 + 8, y=y1 + 7, text=line1)]
    if line2:
        items_texts.append(TextSpec(x=x1 + 8, y=y1 + 26, text=line2))
    return items_shapes, items_texts


def _arrow_down(cx, y) -> TextSpec:
    """Flecha tipográfica entre bloques (sin inventar shapes no evidenciados)."""
    return TextSpec(x=cx, y=y, text="▼", size=10)


def build_d002() -> FolioSpec:
    """D-002 — DIAGRAMA GENERAL DEL MÓDULO TIPO (mapa principal del módulo).

    Fuente: Doc1 §2 (dispositivos), §4.1 (string), §4.1.4–4.1.5 (protecciones),
    §4.2 (TT), §4.3 (canalizaciones), §2.4/§4.8 (comunicaciones y E/S).
    """
    shapes: list = []
    texts: list = []

    # Encabezado
    texts.append(TextSpec(x=60, y=36, size=13,
                          text="MÓDULO TIPO — SEGUEIDOR SOLAR BIAXIAL — 8 × 650 Wp = 5,2 kWp"))
    texts.append(TextSpec(x=60, y=60,
                          text="REQUISITO DEL CLIENTE: 588 MÓDULOS (M-001…M-588) · "
                               "ESTE ESQUEMA ES EL MÓDULO TIPO × 588 — VER D-001 / D-018"))

    # ---- Columna 1: potencia DC (Doc1 §4.1) ----
    for (b, t) in [
        _block(60, 90, 300, 144, "8 × PANEL FV 650 Wp (PV-01…PV-08)",
               "STRING 5,2 kWp EN SERIE — VER D-003"),
        ([], [_arrow_down(180, 148)]),
        _block(60, 158, 300, 212, "STRING DC",
               "332,8 V VMP · 402,2 V VOC · 16,44 A ISC"),
        ([], [_arrow_down(180, 216)]),
        _block(60, 226, 300, 280, "PROTECCIÓN DC — QF-DC 25 A CURVA C",
               "BIPOLAR ≥600 VDC + SPD-DC TIPO 2 — VER D-004"),
        ([], [_arrow_down(180, 284)]),
        _block(60, 294, 300, 348, "SALIDA DC → BORNERA TB-DC",
               "CABLE H1Z2Z2-K 6 mm² (EN 50618) — VER D-016/D-017"),
    ]:
        shapes.extend(b)
        texts.extend(t)

    # ---- Columna 2: control 24 VDC (Doc1 §4.1.5, §2.2.2) ----
    for (b, t) in [
        _block(400, 90, 640, 144, "FUENTE 24 VDC — FU-24VDC",
               "ALIMENTACIÓN DE CONTROL Y ACTUADORES — VER D-005"),
        ([], [_arrow_down(520, 148)]),
        _block(400, 158, 640, 212, "PROTECCIÓN 24 VDC — 6 A POR EJE",
               "CURVA C, BIPOLAR (F-ELEV / F-AZ) — VER D-005"),
        ([], [_arrow_down(520, 216)]),
        _block(400, 226, 640, 280, "CONTROLADOR DomBusTracker2 — CTRL-01",
               "4 RELÉS Q0.0–Q0.3 · ENTRADAS NPN — VER D-005…D-010"),
        ([], [_arrow_down(460, 284), _arrow_down(580, 284)]),
        _block(400, 294, 640, 348, "ACTUADORES SVH7 — M-ELEV / M-AZ",
               "MOTORREDUCTOR DOBLE EJE 24 VDC — VER D-006/D-007"),
        ([], [_arrow_down(580, 352)]),
        _block(400, 362, 640, 416, "SENSORES: FC ×4 NPN · AN-WIND · LUZ",
               "I0.0–I0.3 · AI0 · AI1/AI2 (0–10 V) — VER D-008/D-009"),
    ]:
        shapes.extend(b)
        texts.extend(t)

    # ---- Columna 3: comunicaciones (Doc1 §2.4, §2.5) ----
    texts.append(TextSpec(x=660, y=240, text="→", size=10))
    for (b, t) in [
        _block(720, 226, 960, 280, "RS485 (A/B) — TERMINACIÓN 120 Ω",
               "CABLE APANTALLADO, 115200 bps — VER D-013"),
        ([], [_arrow_down(840, 284)]),
        _block(720, 294, 960, 348, "USR-DR404 — CONCENTADOR",
               "RS485 → ETHERNET/WI-FI · 32 DISPOSITIVOS/RAMAL"),
        ([], [_arrow_down(840, 352)]),
        _block(720, 362, 960, 416, "ETHERNET / WI-FI"),
        ([], [_arrow_down(840, 420)]),
        _block(720, 430, 960, 484, "USR-W610 → DOMOTICZ / SISTEMA SUPERIOR",
               "MONITOREO REMOTO — VER D-013"),
    ]:
        shapes.extend(b)
        texts.extend(t)

    # ---- Notas de trazabilidad ----
    texts.extend([
        TextSpec(x=60, y=470, text="NOTAS:"),
        TextSpec(x=60, y=488,
                 text="1) PE: ESQUEMA TT, 8 JABALINAS — VER D-014"),
        TextSpec(x=60, y=506,
                 text="2) CANALIZACIÓN SEGREGADA: POTENCIA DC / CONTROL 24 VDC / RS485 "
                      "EN CAÑOS INDEPENDIENTES — VER D-015"),
        TextSpec(x=60, y=524,
                 text="3) PENDIENTE DE VERIFICACIÓN: NUMERACIÓN FÍSICA DE TERMINALES "
                      "DEL DISPOSITIVO (VER D-016)"),
        TextSpec(x=60, y=542,
                 text="4) RED DE PLANTA (COLECCIÓN DC/COM): FUERA DEL ALCANCE DE LOS "
                      "DOCUMENTOS FUENTE — VER D-017"),
    ])

    return FolioSpec(
        title="D-002 — DIAGRAMA GENERAL DEL MÓDULO TIPO",
        order=2,
        elements=[],
        connections=[],
        texts=texts,
        shapes=shapes,
    )


def build_d003() -> FolioSpec:
    """D-003 — STRING FOTOVOLTAICO DE 8 PANELES EN SERIE.

    Fuente: Doc1 §2.1.1 (panel JKM625-650N), §4.1.1 (string), §4.1.2 (Ib),
    §4.1.3 (cable H1Z2Z2-K 6 mm²), §4.2.4 (PE 6 mm²).
    Polaridad por terminal: PENDIENTE (símbolo genérico pvcell).
    """
    elements, connections = create_pv_string(count=8, x0=60, y=150, dx=120,
                                             label_base="PV-0")
    # create_pv_string genera ids PV-01..PV-08 con label_base "PV-0"
    # (labels finales: PV-01 … PV-08) — refinar designaciones BOM:
    for el in elements:
        el.label = el.id                      # PV-01 … PV-08
        el.info = {"designation": "Panel FV JKM625-650N 650 Wp (Doc. §2.1.1)",
                   "quantity": "1"}

    # Extremos del string → borneras de salida X1 / X2 (TB-DC)
    elements.append(ElementSpec(
        id="X1", type="dc_terminal", x=55, y=220, label="X1",
        info={"designation": "Borne salida string (TB-DC) — polaridad a verificar"}))
    elements.append(ElementSpec(
        id="X2", type="dc_terminal", x=905, y=220, label="X2",
        info={"designation": "Borne salida string (TB-DC) — polaridad a verificar"}))
    # PV-01.t1 (oeste, extremo 1) → X1.t0 ; PV-08.t3 (este, extremo 2) → X2.t0
    connections.append(ConnectionSpec(from_id="PV-01", from_terminal=1,
                                      to_id="X1", to_terminal=0))
    connections.append(ConnectionSpec(from_id="PV-08", from_terminal=3,
                                      to_id="X2", to_terminal=0))

    shapes = [ShapeSpec(x1=40, y1=80, x2=960, y2=200,
                        color="#7f7f7f", width=1.0, fill=None, dash=True)]
    texts = [
        TextSpec(x=60, y=36, size=13,
                 text="STRING FOTOVOLTAICO — 8 PANELES EN SERIE"),
        TextSpec(x=60, y=60,
                 text="PANELES: JKM625-650N-66HL4M-BDV-Z1 · 650 Wp · "
                      "VMP 41,6 V · IMP 15,64 A · VOC 50,28 V · ISC 16,44 A (Doc. §4.1.1)"),
        TextSpec(x=445, y=210, text="X1 — EXTREMO SALIDA 1"),
        TextSpec(x=760, y=210, text="X2 — EXTREMO SALIDA 2"),
        TextSpec(x=60, y=262,
                 text="VMP,STRING = 8 × 41,6 V = 332,8 V · "
                      "VOC,STRING = 8 × 50,28 V = 402,2 V (Doc. §4.1.1)"),
        TextSpec(x=60, y=284,
                 text="ISC,STRING = 16,44 A · CORRIENTE DE DISEÑO "
                      "IB = 1,25 × ISC = 20,55 A (Doc. §4.1.2, AEA 90364-7-712)"),
        TextSpec(x=60, y=306,
                 text="CABLE: H1Z2Z2-K 6 mm² (EN 50618) UNIPOLAR + PE 6 mm² · "
                      "CAÑO PVC Ø20 mm SEPARADO DE SEÑAL (Doc. §4.1.3/§4.2.4/§4.3)"),
        TextSpec(x=60, y=328,
                 text="CONTINUIDAD: PV-01 → PV-08 EN SERIE · SALIDA → PROTECCIÓN DC "
                      "(VER D-004)"),
        TextSpec(x=60, y=360,
                 text="PENDIENTE DE VERIFICACIÓN: ASIGNACIÓN DE POLARIDAD (+/−) POR "
                      "TERMINAL DEL PANEL (SÍMBOLO GENÉRICO DE BIBLIOTECA)"),
        TextSpec(x=60, y=382,
                 text="REQUISITO DEL CLIENTE: 588 MÓDULOS × ESTE STRING "
                      "(M-001…M-588) — VER D-018"),
    ]

    return FolioSpec(
        title="D-003 — STRING FOTOVOLTAICO 8 PANELES EN SERIE",
        order=3,
        elements=elements,
        connections=connections,
        texts=texts,
        shapes=shapes,
    )
