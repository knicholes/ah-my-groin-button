"""Generate the Ah My Groin v2 KiCad PCB.

This is a deterministic first-pass PCB layout from ../v2/README.md.  It
creates custom module footprints for the HiLetgo Pro Mini and DY-SV17F so the
board does not depend on external SnapEDA/EasyEDA libraries.

Run with KiCad's bundled Python:

    K:\Program Files\KiCad\10.0\bin\python.exe generate_v2_board.py
"""

from __future__ import annotations

import math
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parent
BOARD_PATH = ROOT / "ah_my_groin_v2.kicad_pcb"

BOARD_W = 84.0
BOARD_H = 56.0


NETS = [
    "GND",
    "VBATT",
    "VSYS",
    "VDFP",
    "PFET_GATE",
    "GATE_CTRL",
    "Q4_BASE",
    "BTN_IN",
    "TRIG_OUT",
    "BUSY_IN",
    "SPK+",
    "SPK-",
]


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def pt(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def layer_set(*layers: int) -> pcbnew.LSET:
    layerset = pcbnew.LSET()
    for layer in layers:
        layerset.AddLayer(layer)
    return layerset


TH_LAYERS = layer_set(pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_Mask, pcbnew.B_Mask)
SMD_F_LAYERS = layer_set(pcbnew.F_Cu, pcbnew.F_Paste, pcbnew.F_Mask)
NPTH_LAYERS = layer_set(pcbnew.F_Mask, pcbnew.B_Mask)


class BoardBuilder:
    def __init__(self) -> None:
        self.board = pcbnew.BOARD()
        self.nets: dict[str, pcbnew.NETINFO_ITEM] = {}
        for name in NETS:
            net = pcbnew.NETINFO_ITEM(self.board, name)
            self.board.Add(net)
            self.nets[name] = net

        settings = self.board.GetDesignSettings()
        settings.SetBoardThickness(mm(2.0))
        settings.SetCopperLayerCount(2)
        settings.m_TrackMinWidth = mm(0.20)
        settings.m_ViasMinSize = mm(0.60)
        settings.m_ViasMinDrill = mm(0.30)
        settings.SetCustomTrackWidth(mm(0.25))
        settings.SetCustomTrackWidth(mm(0.60))
        settings.SetCustomViaSize(mm(0.80))
        settings.SetCustomViaDrill(mm(0.40))

    def net(self, name: str | None) -> pcbnew.NETINFO_ITEM | None:
        if not name:
            return None
        return self.nets[name]

    def footprint(self, ref: str, value: str) -> pcbnew.FOOTPRINT:
        fp = pcbnew.FOOTPRINT(self.board)
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetPosition(pt(0, 0))
        fp.SetLayer(pcbnew.F_Cu)
        fp.SetAllowMissingCourtyard(True)
        for field in (fp.Reference(), fp.Value()):
            field.SetVisible(False)
            field.SetLayer(pcbnew.F_Fab)
        self.board.Add(fp)
        return fp

    def th_pad(
        self,
        fp: pcbnew.FOOTPRINT,
        number: str,
        x: float,
        y: float,
        net: str | None,
        size: float = 1.70,
        drill: float = 0.90,
        shape: int = pcbnew.PAD_SHAPE_CIRCLE,
    ) -> pcbnew.PAD:
        pad = pcbnew.PAD(fp)
        pad.SetNumber(str(number))
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetShape(shape)
        pad.SetSize(pt(size, size))
        pad.SetDrillSize(pt(drill, drill))
        pad.SetLayerSet(TH_LAYERS)
        pad.SetPosition(pt(x, y))
        if net:
            pad.SetNet(self.net(net))
        fp.Add(pad)
        return pad

    def smd_pad(
        self,
        fp: pcbnew.FOOTPRINT,
        number: str,
        x: float,
        y: float,
        w: float,
        h: float,
        net: str | None,
        shape: int = pcbnew.PAD_SHAPE_ROUNDRECT,
    ) -> pcbnew.PAD:
        pad = pcbnew.PAD(fp)
        pad.SetNumber(str(number))
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(shape)
        pad.SetSize(pt(w, h))
        if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
            pad.SetRoundRectRadiusRatio(0.20)
        pad.SetLayerSet(SMD_F_LAYERS)
        pad.SetPosition(pt(x, y))
        if net:
            pad.SetNet(self.net(net))
        fp.Add(pad)
        return pad

    def npth_pad(self, fp: pcbnew.FOOTPRINT, x: float, y: float, drill: float = 3.20) -> None:
        pad = pcbnew.PAD(fp)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(pt(drill, drill))
        pad.SetDrillSize(pt(drill, drill))
        pad.SetLayerSet(NPTH_LAYERS)
        pad.SetPosition(pt(x, y))
        fp.Add(pad)

    def text(
        self,
        text: str,
        x: float,
        y: float,
        layer: int = pcbnew.F_SilkS,
        size: float = 0.90,
        angle: float = 0,
    ) -> None:
        if layer == pcbnew.F_SilkS and size < 0.80:
            return
        item = pcbnew.PCB_TEXT(self.board)
        item.SetText(text)
        item.SetPosition(pt(x, y))
        item.SetLayer(layer)
        item.SetTextSize(pt(size, size))
        item.SetTextThickness(mm(max(size * 0.12, 0.10)))
        item.SetTextAngleDegrees(angle)
        self.board.Add(item)

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        layer: int = pcbnew.F_SilkS,
        width: float = 0.12,
    ) -> None:
        shape = pcbnew.PCB_SHAPE(self.board)
        shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
        shape.SetLayer(layer)
        shape.SetWidth(mm(width))
        shape.SetStart(pt(x1, y1))
        shape.SetEnd(pt(x2, y2))
        self.board.Add(shape)

    def track(
        self,
        net: str,
        points: list[tuple[float, float]],
        layer: int = pcbnew.F_Cu,
        width: float = 0.30,
    ) -> None:
        for start, end in zip(points, points[1:]):
            tr = pcbnew.PCB_TRACK(self.board)
            tr.SetStart(pt(*start))
            tr.SetEnd(pt(*end))
            tr.SetLayer(layer)
            tr.SetWidth(mm(width))
            tr.SetNet(self.net(net))
            self.board.Add(tr)

    def via(self, net: str, x: float, y: float, size: float = 0.80, drill: float = 0.40) -> None:
        via = pcbnew.PCB_VIA(self.board)
        via.SetPosition(pt(x, y))
        via.SetWidth(mm(size))
        via.SetDrill(mm(drill))
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        via.SetNet(self.net(net))
        self.board.Add(via)

    def rounded_outline(self, x: float, y: float, w: float, h: float, r: float) -> None:
        pts: list[tuple[float, float]] = []
        corner_specs = [
            ((x + w - r, y + r), -90, 0, (x + w, y + h - r)),
            ((x + w - r, y + h - r), 0, 90, (x + r, y + h)),
            ((x + r, y + h - r), 90, 180, (x, y + r)),
            ((x + r, y + r), 180, 270, (x + r, y)),
        ]
        pts.extend([(x + r, y), (x + w - r, y)])
        for (cx, cy), a0, a1, next_tangent in corner_specs:
            for step in range(0, 9):
                a = math.radians(a0 + (a1 - a0) * step / 8)
                point = (cx + r * math.cos(a), cy + r * math.sin(a))
                if point != pts[-1]:
                    pts.append(point)
            pts.append(next_tangent)
        for start, end in zip(pts, pts[1:]):
            if math.hypot(start[0] - end[0], start[1] - end[1]) < 0.001:
                continue
            self.line(*start, *end, layer=pcbnew.Edge_Cuts, width=0.10)

    def zone(self, net: str, layer: int, inset: float = 0.65) -> None:
        chain = pcbnew.SHAPE_LINE_CHAIN()
        for x, y in [
            (inset, inset),
            (BOARD_W - inset, inset),
            (BOARD_W - inset, BOARD_H - inset),
            (inset, BOARD_H - inset),
        ]:
            chain.Append(pt(x, y))
        chain.SetClosed(True)
        zone = pcbnew.ZONE(self.board)
        zone.SetLayer(layer)
        zone.SetNet(self.net(net))
        zone.SetLocalClearance(mm(0.25))
        zone.SetMinThickness(mm(0.25))
        zone.SetFillMode(pcbnew.ZONE_FILL_MODE_POLYGONS)
        zone.AddPolygon(chain)
        self.board.Add(zone)


def add_pro_mini(board: BoardBuilder) -> dict[str, tuple[float, float]]:
    fp = board.footprint("U1", "HiLetgo Pro Mini 3.3V/8MHz")
    cx, y_top = 24.0, 14.0
    x_left, x_right = cx - 7.62, cx + 7.62
    left = [
        ("RAW", "VSYS"),
        ("GND", "GND"),
        ("RST", None),
        ("VCC", None),
        ("A3", None),
        ("A2", None),
        ("A1", None),
        ("A0", None),
        ("D13", None),
        ("D12", None),
        ("D11", None),
        ("D10", None),
    ]
    right = [
        ("TXO", None),
        ("RXI", None),
        ("RST", None),
        ("GND", "GND"),
        ("D2", "BTN_IN"),
        ("D3", None),
        ("D4", None),
        ("D5", "GATE_CTRL"),
        ("D6", "TRIG_OUT"),
        ("D7", "BUSY_IN"),
        ("D8", None),
        ("D9", None),
    ]
    coords: dict[str, tuple[float, float]] = {}
    for idx, (label, net) in enumerate(left):
        y = y_top + idx * 2.54
        coords[f"L.{label}"] = (x_left, y)
        shape = pcbnew.PAD_SHAPE_RECTANGLE if idx == 0 else pcbnew.PAD_SHAPE_CIRCLE
        board.th_pad(fp, f"L{idx + 1}", x_left, y, net, shape=shape)
    for idx, (label, net) in enumerate(right):
        y = y_top + idx * 2.54
        coords[f"R.{label}"] = (x_right, y)
        shape = pcbnew.PAD_SHAPE_RECTANGLE if idx == 0 else pcbnew.PAD_SHAPE_CIRCLE
        board.th_pad(fp, f"R{idx + 1}", x_right, y, net, shape=shape)

    # HiLetgo clones include an auxiliary top row and A4/A5 pads inside the
    # module outline. These are modeled for mechanical accuracy; only the extra
    # GND pads are tied into this board.
    aux_top = [
        ("GND", "GND"),
        ("A6", None),
        ("A7", None),
        ("DTR", None),
        ("TXO", None),
        ("RXI", None),
        ("VCC", None),
        ("GND", "GND"),
        ("GND", "GND"),
    ]
    x_aux0 = cx - 10.16
    y_aux = y_top - 5.08
    for idx, (label, net) in enumerate(aux_top):
        x = x_aux0 + idx * 2.54
        coords[f"T.{idx + 1}.{label}"] = (x, y_aux)
        board.th_pad(fp, f"T{idx + 1}", x, y_aux, net)
        board.text(label, x - 0.8, y_aux - 2.0, pcbnew.F_Fab, size=0.55)

    for idx, label in enumerate(["A4", "A5"]):
        x = cx - 1.27 + idx * 2.54
        y = y_top + 13.97
        coords[f"I.{label}"] = (x, y)
        board.th_pad(fp, f"I{idx + 1}", x, y, None)
        board.text(label, x - 0.8, y + 1.8, pcbnew.F_Fab, size=0.55)

    board.text("U1 PRO MINI", cx - 8.2, y_top - 3.2, size=0.85)
    board.line(cx - 11.6, y_top - 7.0, cx + 11.6, y_top - 7.0, pcbnew.F_Fab)
    board.line(cx + 11.6, y_top - 7.0, cx + 11.6, y_top + 29.4, pcbnew.F_Fab)
    board.line(cx + 11.6, y_top + 29.4, cx - 11.6, y_top + 29.4, pcbnew.F_Fab)
    board.line(cx - 11.6, y_top + 29.4, cx - 11.6, y_top - 7.0, pcbnew.F_Fab)
    return coords


def add_dy_sv17f(board: BoardBuilder) -> dict[str, tuple[float, float]]:
    fp = board.footprint("U2", "DY-SV17F audio module")
    cx, y_top = 60.0, 13.0
    x_left, x_right = cx - 8.89, cx + 8.89
    left = [
        ("IO0", None),
        ("IO1", "TRIG_OUT"),
        ("IO2", None),
        ("IO3", None),
        ("IO4", None),
        ("IO5", None),
        ("IO6", None),
        ("IO7", None),
    ]
    right = [
        ("V33", None),
        ("V5", "VDFP"),
        ("GND", "GND"),
        ("DACL", None),
        ("BUSY", "BUSY_IN"),
        ("DACR", None),
        ("SPK-", "SPK-"),
        ("SPK+", "SPK+"),
    ]
    coords: dict[str, tuple[float, float]] = {}
    for idx, (label, net) in enumerate(left):
        pin = idx + 1
        y = y_top + idx * 2.54
        coords[f"{pin}.{label}"] = (x_left, y)
        board.th_pad(fp, str(pin), x_left, y, net, shape=pcbnew.PAD_SHAPE_RECTANGLE if pin == 1 else pcbnew.PAD_SHAPE_CIRCLE)
    for idx, (label, net) in enumerate(right):
        pin = 16 - idx
        y = y_top + idx * 2.54
        coords[f"{pin}.{label}"] = (x_right, y)
        board.th_pad(fp, str(pin), x_right, y, net)

    board.text("U2 DY-SV17F", cx - 7.0, y_top - 3.1, size=0.85)
    board.line(cx - 11.0, y_top - 2.0, cx + 11.0, y_top - 2.0, pcbnew.F_Fab)
    board.line(cx + 11.0, y_top - 2.0, cx + 11.0, y_top + 19.8, pcbnew.F_Fab)
    board.line(cx + 11.0, y_top + 19.8, cx - 11.0, y_top + 19.8, pcbnew.F_Fab)
    board.line(cx - 11.0, y_top + 19.8, cx - 11.0, y_top - 2.0, pcbnew.F_Fab)
    return coords


def add_sot23(board: BoardBuilder, ref: str, value: str, cx: float, cy: float, nets: dict[int, str]) -> dict[int, tuple[float, float]]:
    fp = board.footprint(ref, value)
    coords = {1: (cx - 0.95, cy - 0.95), 2: (cx - 0.95, cy + 0.95), 3: (cx + 0.95, cy)}
    for pin, (x, y) in coords.items():
        board.smd_pad(fp, str(pin), x, y, 0.80, 0.95, nets.get(pin))
    board.text(ref, cx - 2.0, cy - 2.4, size=0.65)
    board.line(cx - 1.6, cy - 1.6, cx + 1.6, cy - 1.6, pcbnew.F_Fab)
    board.line(cx + 1.6, cy - 1.6, cx + 1.6, cy + 1.6, pcbnew.F_Fab)
    board.line(cx + 1.6, cy + 1.6, cx - 1.6, cy + 1.6, pcbnew.F_Fab)
    board.line(cx - 1.6, cy + 1.6, cx - 1.6, cy - 1.6, pcbnew.F_Fab)
    return coords


def add_smd2(board: BoardBuilder, ref: str, value: str, cx: float, cy: float, net1: str, net2: str, vertical: bool = False) -> dict[int, tuple[float, float]]:
    fp = board.footprint(ref, value)
    if vertical:
        coords = {1: (cx, cy - 0.90), 2: (cx, cy + 0.90)}
        size = (1.10, 0.85)
    else:
        coords = {1: (cx - 0.90, cy), 2: (cx + 0.90, cy)}
        size = (0.85, 1.10)
    board.smd_pad(fp, "1", *coords[1], *size, net1)
    board.smd_pad(fp, "2", *coords[2], *size, net2)
    board.text(ref, cx - 1.1, cy - 1.7, size=0.60)
    return coords


def add_cap_th(board: BoardBuilder, ref: str, value: str, x: float, y: float, pitch: float, net1: str, net2: str) -> dict[int, tuple[float, float]]:
    fp = board.footprint(ref, value)
    coords = {1: (x, y), 2: (x + pitch, y)}
    board.th_pad(fp, "1", *coords[1], net1, size=1.80, drill=0.80, shape=pcbnew.PAD_SHAPE_RECTANGLE)
    board.th_pad(fp, "2", *coords[2], net2, size=1.80, drill=0.80)
    board.text(ref, x - 1.2, y - 2.3, size=0.65)
    return coords


def add_jst2(board: BoardBuilder, ref: str, label: str, cx: float, y: float, net1: str, net2: str) -> dict[int, tuple[float, float]]:
    fp = board.footprint(ref, label)
    coords = {1: (cx - 1.25, y), 2: (cx + 1.25, y)}
    board.th_pad(fp, "1", *coords[1], net1, size=1.85, drill=1.00, shape=pcbnew.PAD_SHAPE_RECTANGLE)
    board.th_pad(fp, "2", *coords[2], net2, size=1.85, drill=1.00)
    board.text(ref, cx - 2.0, y - 4.0, size=0.70)
    board.text(label, cx - 4.2, y + 3.2, size=0.65)
    board.line(cx - 4.0, y - 2.3, cx + 4.0, y - 2.3)
    board.line(cx + 4.0, y - 2.3, cx + 4.0, y + 2.3)
    board.line(cx + 4.0, y + 2.3, cx - 4.0, y + 2.3)
    board.line(cx - 4.0, y + 2.3, cx - 4.0, y - 2.3)
    return coords


def add_mounting_hole(board: BoardBuilder, ref: str, x: float, y: float) -> None:
    fp = board.footprint(ref, "M3 mount")
    board.npth_pad(fp, x, y, drill=3.20)
    board.text(ref, x - 1.5, y - 4.1, size=0.60)
    # Copper keepout/ring reference on both layers, connected by nearby GND stitch via.
    board.line(x - 3.0, y, x + 3.0, y, pcbnew.F_Fab, 0.10)
    board.line(x, y - 3.0, x, y + 3.0, pcbnew.F_Fab, 0.10)


def add_test_pad(board: BoardBuilder, ref: str, net: str, x: float, y: float) -> tuple[float, float]:
    fp = board.footprint(ref, f"TP {net}")
    board.th_pad(fp, "1", x, y, net, size=1.50, drill=0.70, shape=pcbnew.PAD_SHAPE_CIRCLE)
    board.text(ref, x - 1.0, y - 2.0, size=0.55)
    board.text(net, x - 1.5, y + 1.7, size=0.50)
    return (x, y)


def add_mode_solder_bridges(board: BoardBuilder) -> None:
    # Documentation only. DY-SV17F modules expose CON pads with inconsistent
    # placement, so clone-specific solder jumpers should be added after the
    # exact module is verified.
    return


def add_assembly_labels(board: BoardBuilder) -> None:
    labels = [
        ("H1", 4.8, 2.9),
        ("H2", 76.8, 2.9),
        ("H3", 4.8, 54.0),
        ("H4", 76.8, 54.0),
        ("U1 Pro Mini", 16.0, 45.0),
        ("FTDI edge", 16.0, 46.4),
        ("U2 DY-SV17F", 56.0, 34.5),
        ("USB edge", 58.0, 36.0),
        ("Q3", 16.0, 35.0),
        ("Q1", 46.8, 10.6),
        ("Q4", 47.0, 27.2),
        ("R1", 38.6, 30.0),
        ("R2", 34.3, 20.0),
        ("C1", 4.2, 27.2),
        ("C2", 36.8, 7.2),
        ("C3", 41.8, 7.2),
        ("C4", 57.8, 11.9),
        ("C5", 62.5, 11.9),
        ("C6", 68.5, 11.9),
        ("J1 BAT", 10.6, 45.0),
        ("J2 BTN", 32.0, 45.0),
        ("J3 SPK", 66.0, 45.0),
        ("TP1 VSYS", 45.0, 8.4),
        ("TP2 VDFP", 52.4, 3.6),
        ("TP5 GND", 61.0, 3.6),
        ("TP3 PFET", 50.2, 26.2),
        ("TP4 BUSY", 72.3, 25.5),
    ]
    for label, x, y in labels:
        board.text(label, x, y, pcbnew.F_Fab, size=0.65)

    board.text("DY mode pads: CON1=GND, CON2=V33, CON3 per module", 8.0, 58.0, pcbnew.Cmts_User, size=0.75)
    board.text("Verify DY-SV17F pin 1/orientation before fab", 8.0, 59.8, pcbnew.Cmts_User, size=0.75)


def build() -> None:
    board = BoardBuilder()
    board.rounded_outline(0, 0, BOARD_W, BOARD_H, 3.0)
    board.zone("GND", pcbnew.F_Cu, inset=3.5)
    board.zone("GND", pcbnew.B_Cu, inset=3.5)
    board.text("AH MY GROIN V2", 31.0, 3.0, size=1.0)
    board.text("BAT", 11.0, 53.1, size=0.80)
    board.text("BTN", 33.0, 53.1, size=0.80)
    board.text("SPK", 67.0, 53.1, size=0.80)

    for ref, x, y in [("H1", 6, 6), ("H2", 78, 6), ("H3", 6, 50), ("H4", 78, 50)]:
        add_mounting_hole(board, ref, x, y)

    u1 = add_pro_mini(board)
    u2 = add_dy_sv17f(board)

    q3 = add_sot23(board, "Q3", "AO3401A reverse polarity", 13.0, 37.0, {1: "GND", 2: "VSYS", 3: "VBATT"})
    q1 = add_sot23(board, "Q1", "AO3401A audio high-side", 45.0, 14.0, {1: "PFET_GATE", 2: "VDFP", 3: "VSYS"})
    q4 = add_sot23(board, "Q4", "MMBT3904 gate pull-down", 45.0, 24.0, {1: "Q4_BASE", 2: "GND", 3: "PFET_GATE"})

    r1 = add_smd2(board, "R1", "10k", 40.0, 27.0, "GATE_CTRL", "Q4_BASE")
    r2 = add_smd2(board, "R2", "100k", 38.0, 20.0, "VSYS", "PFET_GATE", vertical=True)

    c1 = add_cap_th(board, "C1", "1000uF", 6.5, 30.0, 5.0, "VSYS", "GND")
    c2 = add_smd2(board, "C2", "10uF", 38.0, 9.5, "VSYS", "GND")
    c3 = add_smd2(board, "C3", "0.1uF", 43.0, 9.5, "VSYS", "GND")
    c4 = add_cap_th(board, "C4", "100uF", 54.5, 8.0, 2.5, "VDFP", "GND")
    c5 = add_smd2(board, "C5", "0.1uF", 64.0, 8.0, "VDFP", "GND")
    c6 = add_smd2(board, "C6", "10uF", 70.0, 8.0, "VDFP", "GND")

    j1 = add_jst2(board, "J1", "BAT + -", 14.0, 49.0, "VBATT", "GND")
    j2 = add_jst2(board, "J2", "BUTTON", 36.0, 49.0, "BTN_IN", "GND")
    j3 = add_jst2(board, "J3", "SPEAKER", 70.0, 49.0, "SPK+", "SPK-")

    add_test_pad(board, "TP1", "VSYS", 46.0, 5.5)
    add_test_pad(board, "TP2", "VDFP", 54.5, 5.5)
    add_test_pad(board, "TP3", "PFET_GATE", 49.0, 24.0)
    add_test_pad(board, "TP4", "BUSY_IN", 76.0, 23.0)
    add_test_pad(board, "TP5", "GND", 63.0, 5.5)
    add_mode_solder_bridges(board)
    add_assembly_labels(board)

    # Battery and system power.
    board.track("VBATT", [j1[1], (12.75, 43.0), q3[3]], pcbnew.F_Cu, 1.00)
    board.track("VSYS", [q3[2], (10.0, 37.95), c1[1]], pcbnew.F_Cu, 0.85)
    board.track("VSYS", [c1[1], (9.0, 22.0), (13.4, 22.0), (13.4, 14.0), u1["L.RAW"]], pcbnew.F_Cu, 0.70)
    board.track("VSYS", [u1["L.RAW"], (16.38, 11.5), (37.1, 11.5), c2[1]], pcbnew.F_Cu, 0.60)
    board.track("VSYS", [(37.1, 11.5), (42.1, 11.5), c3[1]], pcbnew.F_Cu, 0.60)
    board.track("VSYS", [u1["L.RAW"], (16.38, 11.5), (45.95, 11.5), q1[3]], pcbnew.F_Cu, 0.85)
    board.track("VSYS", [q1[3], (45.95, 12.0), (38.0, 12.0), r2[1]], pcbnew.F_Cu, 0.45)
    board.track("VSYS", [(46.0, 11.5), (46.0, 5.5)], pcbnew.F_Cu, 0.35)

    # DY-SV17F gated rail.
    board.track("VDFP", [q1[2], (44.05, 20.5), (48.5, 20.5), (48.5, 10.5), (72.0, 10.5), (72.0, 15.54), u2["15.V5"]], pcbnew.F_Cu, 0.85)
    board.track("VDFP", [(72.0, 10.5), c6[1]], pcbnew.F_Cu, 0.70)
    board.track("VDFP", [(72.0, 10.5), (64.0, 10.5), c5[1]], pcbnew.F_Cu, 0.60)
    board.track("VDFP", [(72.0, 10.5), (54.5, 10.5), c4[1]], pcbnew.F_Cu, 0.70)
    board.track("VDFP", [c4[1], (54.5, 5.5)], pcbnew.F_Cu, 0.35)

    # Gate drive.
    board.track("PFET_GATE", [q1[1], (40.0, 13.05), (40.0, 21.6), (49.0, 21.6), (49.0, 24.0), q4[3]], pcbnew.F_Cu, 0.30)
    board.track("PFET_GATE", [r2[2], (40.0, 20.9), (40.0, 21.6)], pcbnew.F_Cu, 0.30)
    board.track("GATE_CTRL", [u1["R.D5"], (36.0, u1["R.D5"][1]), (36.0, 27.0), r1[1]], pcbnew.F_Cu, 0.25)
    board.track("Q4_BASE", [r1[2], q4[1]], pcbnew.F_Cu, 0.25)

    # Digital control.
    board.track("TRIG_OUT", [u1["R.D6"], (34.0, u1["R.D6"][1]), (34.0, 17.0), u2["2.IO1"]], pcbnew.B_Cu, 0.25)
    board.track("BUSY_IN", [u1["R.D7"], (73.0, u1["R.D7"][1]), (73.0, 23.16), u2["12.BUSY"]], pcbnew.B_Cu, 0.25)
    board.track("BUSY_IN", [(73.0, 23.16), (76.0, 23.0)], pcbnew.B_Cu, 0.25)
    board.track("BTN_IN", [u1["R.D2"], (30.0, 24.16), (30.0, 45.0), (34.75, 45.0), j2[1]], pcbnew.B_Cu, 0.25)

    # Speaker output: keep short and wide.
    board.track("SPK+", [u2["9.SPK+"], (68.75, 30.78), j3[1]], pcbnew.F_Cu, 0.60)
    board.track("SPK-", [u2["10.SPK-"], (71.25, 28.24), j3[2]], pcbnew.F_Cu, 0.60)

    # Explicit ground backbone, backed up by zones once the board is opened and
    # refilled in KiCad.
    board.track("GND", [q3[1], (12.05, 34.5), (15.0, 34.5), (15.0, 30.0), c1[2]], pcbnew.F_Cu, 0.60)
    board.via("GND", 11.0, 34.5)
    board.track("GND", [q3[1], (11.0, 34.5)], pcbnew.F_Cu, 0.35)
    board.track("GND", [(11.0, 34.5), (11.0, 52.0), (15.25, 52.0), j1[2]], pcbnew.B_Cu, 0.50)
    board.track("GND", [j1[2], (15.25, 52.0), (37.25, 52.0), j2[2]], pcbnew.F_Cu, 0.60)
    board.track("GND", [u1["L.GND"], (11.5, 16.54), c1[2]], pcbnew.B_Cu, 0.50)
    board.via("GND", 38.9, 7.4)
    board.track("GND", [c2[2], (38.9, 7.4)], pcbnew.F_Cu, 0.35)
    board.track("GND", [(38.9, 7.4), (12.2, 7.4), (12.2, 16.54), u1["L.GND"]], pcbnew.B_Cu, 0.35)
    board.track("GND", [c2[2], (38.9, 7.4), (43.9, 7.4), c3[2]], pcbnew.F_Cu, 0.35)
    board.track("GND", [u1["T.1.GND"], (10.0, 8.92), (10.0, 16.54), u1["L.GND"]], pcbnew.B_Cu, 0.35)
    board.track("GND", [u1["T.8.GND"], u1["T.9.GND"], (38.9, 6.2), (38.9, 7.4)], pcbnew.B_Cu, 0.35)
    board.track("GND", [u1["R.GND"], (27.0, 21.62), (27.0, 16.54), u1["L.GND"]], pcbnew.B_Cu, 0.35)
    board.track("GND", [q4[2], (44.05, 45.0), (37.25, 45.0), j2[2]], pcbnew.F_Cu, 0.35)
    board.track("GND", [c4[2], (57.0, 4.0), (12.2, 4.0), (12.2, 16.54), u1["L.GND"]], pcbnew.B_Cu, 0.50)
    board.track("GND", [c4[2], (60.0, 5.5), (63.0, 5.5)], pcbnew.F_Cu, 0.35)
    board.track("GND", [(63.0, 5.5), (64.9, 6.5), c5[2]], pcbnew.F_Cu, 0.35)
    board.track("GND", [c5[2], (64.9, 6.5), (70.9, 6.5), c6[2]], pcbnew.F_Cu, 0.35)
    board.track("GND", [c6[2], (74.0, 8.0), (74.0, 18.08), u2["14.GND"]], pcbnew.F_Cu, 0.35)

    # Do not fill zones from SWIG Python on Windows/KiCad 10; ZONE_FILLER can
    # crash the interpreter. Open the board in KiCad and press B before final
    # DRC/Gerber export.
    pcbnew.SaveBoard(str(BOARD_PATH), board.board)
    print(f"Wrote {BOARD_PATH}")


if __name__ == "__main__":
    build()
