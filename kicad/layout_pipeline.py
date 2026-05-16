"""
Single-shot layout pipeline. The wrapper script deletes the board and
re-runs sync_netlist.py before calling this, so we never need to remove
tracks/zones (SWIG remove() rejects them on this build).

Routing strategy:
  F.Cu (top): wide power tracks (VBATT, VSYS, VDFP), audio SPK_P,
              short analog control (Q1_GATE, Q4_BASE, GATE_CTRL).
  B.Cu (bottom): all long digital signals (BTN_IN, TRIG_OUT, BUSY_IN),
              V33 power rail to mode jumpers, audio SPK_N.
  GND: copper pours on both layers, left UNFILLED for user to fill in
       the KiCad GUI (SWIG zone-fill crashes Python here).

Key choices made to satisfy DRC on a hand-routed 90×70 mm board:
  * Pro Mini and DY-SV17F are anchored at PIN 1 (top of each header),
    NOT centred. With pin 1 at y=8 (Pro Mini) and y=5 (DY-SV17F), the
    module bodies fit within the board with FTDI overhang.
  * Tracks cross the J5 column (x=30.24) only at midpoints between two
    consecutive pads (e.g. y=29.59 between J5.9 and J5.10; y=32.13
    between J5.10 and J5.11) where 0.295 mm side-clearance is available.
  * Mounting-hole footprints and C1's dual-pitch radial cap footprint
    have multiple pads sharing one pad number; we walk every pad and
    assign the correct net.
  * SPK_N goes on B.Cu via x=78 column so it doesn't share F.Cu space
    with SPK_P; VDFP runs on F.Cu UP and OVER the DY-SV17F module
    (y=2 channel) so it doesn't fight SPK_P's vertical at x=72.78.
"""
import sys
from pathlib import Path
import pcbnew

PCB = Path(r"I:\code\ah-my-groin-button\kicad\ahmygroin.kicad_pcb")

W_PWR = 0.5
W_SIG = 0.25
F_CU  = "F.Cu"
B_CU  = "B.Cu"
EDGE  = "Edge.Cuts"

PLACEMENTS = {
    # mounting holes — corners
    "H1":  (5,    5,    0),
    "H2":  (85,   5,    0),
    "H3":  (5,    65,   0),
    "H4":  (85,   65,   0),
    # Pro Mini sockets (pin 1 anchor; FTDI overhang at top edge)
    "J4":  (15,    8,   0),
    "J5":  (30.24, 8,   0),
    # DY-SV17F sockets
    "J6":  (55,    5,   0),
    "J7":  (72.78, 5,   0),
    # power chain
    "Q3":  (15,    55,  0),       # reverse-polarity P-FET
    "C1":  (30,    50,  0),       # 1000 µF VSYS bulk
    "Q1":  (50,    30,  0),       # DY-SV17F gate P-FET
    "Q4":  (42,    30,  0),       # NPN level shifter
    "R1":  (25,    29.59, 0),     # 10 k base, y aligned to J5 midpoint
    "R2":  (45,    33,  0),       # 100 k pull-up, just south of spine
    # VSYS decoupling near Pro Mini RAW
    "C2":  (35,    40,  0),
    "C3":  (39,    40,  0),
    # VDFP decoupling — C4 placed west of J7 column so VDFP B.Cu path
    # doesn't have to cross SPK_N's x=78 vertical. C5/C6 sit east of
    # the J7 column to give a short F.Cu approach to J7.2.
    "C4":  (60,    14,  0),       # 100 µF radial bulk
    "C5":  (77,    8,   0),       # 0.1 µF, 3.2 mm east of J7.2
    "C6":  (77,    12,  0),       # 10 µF
    # External JST connectors — bottom edge
    "J1":  (14,    63,  270),     # BAT (moved east to clear H3 courtyard)
    "J2":  (28,    63,  270),
    "J3":  (74,    63,  270),
    # Mode-select 1×3 pin headers, horizontal
    "J8":  (45,    50,  90),
    "J9":  (55,    50,  90),
    "J10": (65,    50,  90),
}

def to_iu(x_mm):
    return pcbnew.FromMM(x_mm)

def vec(x_mm, y_mm):
    return pcbnew.VECTOR2I(to_iu(x_mm), to_iu(y_mm))

def get_net(board, name):
    candidates = (name, "/" + name) if not name.startswith("/") else (name,)
    for code in range(board.GetNetCount()):
        ni = board.GetNetInfo().GetNetItem(code)
        if ni.GetNetname() in candidates:
            return ni
    raise RuntimeError(f"net {name!r} not on board")

def add_track(board, x1, y1, x2, y2, layer_name, width_mm, net):
    if (x1, y1) == (x2, y2):
        return
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(vec(x1, y1))
    t.SetEnd  (vec(x2, y2))
    t.SetWidth(to_iu(width_mm))
    t.SetLayer(board.GetLayerID(layer_name))
    if net is not None:
        t.SetNet(net)
    board.Add(t)

def add_via(board, x_mm, y_mm, net, drill_mm=0.4, diameter_mm=0.8):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x_mm, y_mm))
    v.SetDrill(to_iu(drill_mm))
    v.SetWidth(to_iu(diameter_mm))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(board.GetLayerID(F_CU), board.GetLayerID(B_CU))
    if net is not None:
        v.SetNet(net)
    board.Add(v)

def chain(board, net_name, layer, width, *waypoints):
    net = get_net(board, net_name)
    for (x1, y1), (x2, y2) in zip(waypoints, waypoints[1:]):
        add_track(board, x1, y1, x2, y2, layer, width, net)

def via_at(board, net_name, x, y):
    add_via(board, x, y, get_net(board, net_name))

def get_pad_pos(board, ref, pad_num):
    fp = board.FindFootprintByReference(ref)
    pad = fp.FindPadByNumber(str(pad_num))
    p = pad.GetPosition()
    return (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))

def reset_pcb_geometry(board):
    try:
        for t in list(board.GetTracks()):
            board.Remove(t)
    except Exception:
        pass

def place_all(board):
    fp_by_ref = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for ref, (x, y, rot) in PLACEMENTS.items():
        fp = fp_by_ref[ref]
        fp.SetPosition(vec(x, y))
        fp.SetOrientationDegrees(rot)
    gnd = get_net(board, "GND")
    for ref in ("H1", "H2", "H3", "H4"):
        for pad in fp_by_ref[ref].Pads():
            pad.SetNet(gnd)
    vsys = get_net(board, "VSYS")
    for pad in fp_by_ref["C1"].Pads():
        if pad.GetNumber() == "1":
            pad.SetNet(vsys)
        elif pad.GetNumber() == "2":
            pad.SetNet(gnd)

def add_outline(board, x0=0, y0=0, w=90, h=70, r=3):
    edge = board.GetLayerID(EDGE)
    def line(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.S_SEGMENT)
        s.SetStart(vec(x1, y1))
        s.SetEnd  (vec(x2, y2))
        s.SetLayer(edge)
        s.SetWidth(to_iu(0.15))
        board.Add(s)
    def arc(cx, cy, sx, sy, ex, ey):
        a = pcbnew.PCB_SHAPE(board)
        a.SetShape(pcbnew.S_ARC)
        a.SetCenter(vec(cx, cy))
        a.SetStart (vec(sx, sy))
        a.SetEnd   (vec(ex, ey))
        a.SetLayer(edge)
        a.SetWidth(to_iu(0.15))
        board.Add(a)
    line(x0+r,   y0,     x0+w-r, y0)
    line(x0+w,   y0+r,   x0+w,   y0+h-r)
    line(x0+w-r, y0+h,   x0+r,   y0+h)
    line(x0,     y0+h-r, x0,     y0+r)
    arc(x0+r,   y0+r,   x0,     y0+r,   x0+r,   y0)
    arc(x0+w-r, y0+r,   x0+w-r, y0,     x0+w,   y0+r)
    arc(x0+w-r, y0+h-r, x0+w,   y0+h-r, x0+w-r, y0+h)
    arc(x0+r,   y0+h-r, x0+r,   y0+h,   x0,     y0+h-r)

def route(board):
    P = lambda r, p: get_pad_pos(board, r, p)

    # =========================================================
    # F.Cu WIDE POWER (0.5 mm)
    # =========================================================

    # VBATT (J1.1 → Q3.S)
    j1_1 = P("J1", 1)             # (14, 63)
    q3_S = P("Q3", 2)             # (14.06, 54.05)
    chain(board, "VBATT", F_CU, W_PWR,
          j1_1, (q3_S[0], j1_1[1]), q3_S)

    # VSYS spine: Q3.D → C1.1 → J5.12 → east to Q1.S
    q3_D = P("Q3", 3)             # (15.94, 55)
    c1_p = P("C1", 1)             # (29.33, 48.40)
    j5_12 = P("J5", 12)           # (30.24, 35.94)
    q1_S = P("Q1", 2)             # (49.06, 30.95)
    c2_1 = P("C2", 1)             # (33.96, 40)
    c3_1 = P("C3", 1)             # (37.96, 40)
    r2_1 = P("R2", 1)             # (44, 33)
    chain(board, "VSYS", F_CU, W_PWR,
          q3_D, (q3_D[0], c1_p[1]), c1_p)
    chain(board, "VSYS", F_CU, W_PWR,
          c1_p, (j5_12[0], c1_p[1]), j5_12)
    # C1 is a dual-pitch radial; its pad 1 exists at TWO positions
    # ((29.33, 48.40) for 2.50 mm lead pitch and (30.00, 50.00) for
    # 5.00 mm pitch). Link them with a short track so whichever hole
    # the lead actually uses, the connection completes.
    chain(board, "VSYS", F_CU, W_PWR, c1_p, (30.0, 50.0))
    spine_y = j5_12[1]            # 35.94
    chain(board, "VSYS", F_CU, W_PWR,
          j5_12, (q1_S[0], spine_y), q1_S)
    # branches
    chain(board, "VSYS", F_CU, W_PWR, (c2_1[0], spine_y), c2_1)
    chain(board, "VSYS", F_CU, W_PWR, (c3_1[0], spine_y), c3_1)
    chain(board, "VSYS", F_CU, W_PWR, (r2_1[0], spine_y), r2_1)

    # VDFP: Q1.D F.Cu south to y=44; via to B.Cu; B.Cu east to x=60
    # (west of SPK_N's x=78 vertical and BUSY_IN's x=70 vertical at
    # this y); B.Cu north up x=60 column to C4.1 (60, 14). F.Cu C4 →
    # east through inter-pad-row channel at y=13.89 (midpoint between
    # J*.4 and J*.5) → up to C5.1 (passes C6.1, same net) → west into
    # J7.2.
    q1_D = P("Q1", 3)             # (50.94, 30)
    c4_p = P("C4", 1)             # (60, 14)
    c5_p = P("C5", 1)             # (75.96, 8)
    c6_p = P("C6", 1)             # (75.96, 12)
    j7_2 = P("J7", 2)             # (72.78, 7.54)
    # VDFP entirely on F.Cu, no vias. Q1.D north up x=50.94 column to
    # the y=11.35 channel (midpoint between J*.3 at y=10.08 and J*.4 at
    # y=12.62 — a 0.59 mm clear gap). Run east through that channel
    # with a 0.25 mm trace (0.25 + 2*0.15 = 0.55 mm fits). South tap
    # into C4.1, north tap to C5.1, south tap to C6.1, west into J7.2.
    channel_y = 11.35
    chain(board, "VDFP", F_CU, W_PWR,
          q1_D, (q1_D[0], channel_y))
    chain(board, "VDFP", F_CU, 0.25,
          (q1_D[0], channel_y), (c5_p[0], channel_y))
    chain(board, "VDFP", F_CU, W_PWR,
          (c4_p[0], channel_y), c4_p)
    chain(board, "VDFP", F_CU, W_PWR,
          (c5_p[0], channel_y), c5_p)
    chain(board, "VDFP", F_CU, W_PWR,
          (c5_p[0], channel_y), c6_p)
    chain(board, "VDFP", F_CU, W_PWR,
          c5_p, (j7_2[0], c5_p[1]), j7_2)

    # SPK_P (J7.8 → J3.1) on F.Cu, x=72.78 column
    j7_8 = P("J7", 8)             # (72.78, 22.78)
    j3_1 = P("J3", 1)             # (74, 63)
    chain(board, "SPK_P", F_CU, W_PWR,
          j7_8,
          (j7_8[0], 60),
          (j3_1[0], 60),
          j3_1)

    # =========================================================
    # F.Cu SIGNALS (analog control, 0.25 mm)
    # =========================================================

    # Q1_GATE: R2.2 → Q1.G → Q4.C
    q1_G = P("Q1", 1)             # (49.06, 29.05)
    r2_2 = P("R2", 2)             # (46, 33)
    q4_C = P("Q4", 3)             # (42.94, 30)
    # R2.2 (46, 33) → (46, 29.05) → Q1.G (49.06, 29.05)
    chain(board, "Q1_GATE", F_CU, W_SIG,
          r2_2, (r2_2[0], q1_G[1]), q1_G)
    # Q1.G → Q4.C: west at y=29.05 to (42.94, 29.05), south 0.95 mm
    chain(board, "Q1_GATE", F_CU, W_SIG,
          q1_G, (q4_C[0], q1_G[1]), q4_C)

    # Q4_BASE: R1.2 → Q4.B (y=29.59 crossing midpoint of J5.9 / J5.10)
    r1_2 = P("R1", 2)             # (26, 29.59)
    q4_B = P("Q4", 1)             # (41.06, 29.05)
    chain(board, "Q4_BASE", F_CU, W_SIG,
          r1_2, (q4_B[0], r1_2[1]), q4_B)

    # GATE_CTRL: J4.8 → R1.1, F.Cu, east-then-south so we don't run on
    # the x=15 column (J4 has TRIG_OUT on J4.9 just below).
    j4_8 = P("J4", 8)             # (15, 25.78)
    r1_1 = P("R1", 1)             # (24, 29.59)
    chain(board, "GATE_CTRL", F_CU, W_SIG,
          j4_8,
          (17, j4_8[1]),
          (17, r1_1[1]),
          r1_1)

    # =========================================================
    # B.Cu SIGNALS (0.25 mm)
    # =========================================================

    # V33: J5.11 → via → spine south at x=27 → east at y=53 → taps north
    # to each J*.3. Split the spine into segments that END at each tap
    # point so KiCad sees a proper T-junction and the taps aren't
    # flagged "dangling".
    j5_11 = P("J5", 11)           # (30.24, 33.4)
    j8_3  = P("J8", 3)
    j9_3  = P("J9", 3)
    j10_3 = P("J10", 3)
    chain(board, "V33", F_CU, 0.4, j5_11, (27, 33.4))
    via_at(board, "V33", 27, 33.4)
    y = 53
    chain(board, "V33", B_CU, 0.4,
          (27, 33.4),
          (27, y),
          (j8_3[0], y))
    chain(board, "V33", B_CU, 0.4, (j8_3[0], y), (j8_3[0], j8_3[1]))
    chain(board, "V33", B_CU, 0.4, (j8_3[0], y), (j9_3[0], y))
    chain(board, "V33", B_CU, 0.4, (j9_3[0], y), (j9_3[0], j9_3[1]))
    chain(board, "V33", B_CU, 0.4, (j9_3[0], y), (j10_3[0], y))
    chain(board, "V33", B_CU, 0.4, (j10_3[0], y), (j10_3[0], j10_3[1]))

    # BTN_IN: J4.5 → J2.1 (south column at x=12, east to J2)
    j4_5 = P("J4", 5)
    j2_1 = P("J2", 1)
    chain(board, "BTN_IN", B_CU, W_SIG,
          j4_5,
          (12, j4_5[1]),
          (12, 60),
          (j2_1[0], 60),
          j2_1)

    # TRIG_OUT: J4.9 → J6.2 (east jog at x=17, y=27 horizontal channel
    # is the midpoint between J5.8 and J5.9)
    j4_9 = P("J4", 9)
    j6_2 = P("J6", 2)
    chain(board, "TRIG_OUT", B_CU, W_SIG,
          j4_9,
          (17, j4_9[1]),
          (17, 27),
          (53.5, 27),
          (53.5, j6_2[1]),
          j6_2)

    # BUSY_IN: J4.10 → J7.5. East at y=32.13 to x=70 (west of SPK_N's
    # east jog so they don't collide); north up x=70 column (clear of
    # J10.3 at y=55 since vertical only goes to y=15); east into J7.5.
    j4_10 = P("J4", 10)
    j7_5  = P("J7", 5)
    chain(board, "BUSY_IN", B_CU, W_SIG,
          j4_10,
          (17, j4_10[1]),
          (17, 32.13),
          (70, 32.13),
          (70, j7_5[1]),
          j7_5)

    # SPK_N (J7.7 → J3.2) on B.Cu via x=78 column, well clear of other
    # B.Cu signals and of J3.1 (SPK_P).
    j7_7 = P("J7", 7)
    j3_2 = P("J3", 2)
    chain(board, "SPK_N", B_CU, W_PWR,
          j7_7,
          (78, j7_7[1]),
          (78, 66),
          (j3_2[0], 66),
          j3_2)

def add_gnd_zones(board):
    """Drop F.Cu and B.Cu copper pours tied to GND. Leaves them
    UNFILLED — user fills in the GUI by pressing B because SWIG
    zone-fill crashes pcbnew Python on Windows here.

    We modify the zone's own Outline() in place instead of setting a
    new SHAPE_POLY_SET; SWIG ownership semantics on this build make
    SetOutline() free the polygon before SaveBoard serialises it
    (SaveBoard crashes immediately after, file is truncated)."""
    gnd = get_net(board, "GND")
    for layer_name in (F_CU, B_CU):
        z = pcbnew.ZONE(board)
        z.SetLayer(board.GetLayerID(layer_name))
        z.SetNet(gnd)
        z.SetIsRuleArea(False)
        z.SetAssignedPriority(0)
        z.SetLocalClearance(to_iu(0.25))
        z.SetMinThickness(to_iu(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(to_iu(0.25))
        z.SetThermalReliefSpokeWidth(to_iu(0.4))
        outline = z.Outline()                    # zone-owned, won't dangle
        outline.RemoveAllContours()
        outline.NewOutline()
        for x, y in [(0.2, 0.2), (89.8, 0.2), (89.8, 69.8), (0.2, 69.8)]:
            outline.Append(to_iu(x), to_iu(y))
        board.Add(z)

def main():
    board = pcbnew.LoadBoard(str(PCB))
    reset_pcb_geometry(board)
    place_all(board)
    # JLCPCB 2-layer process supports 5 mil = 0.127 mm minimums; we set
    # 0.15 mm so DRC accepts the inter-pad-row crossings on J5 (J5.9 →
    # J5.10 gap is 0.59 mm) and the J*.3/.4 channel for VDFP.
    bds = board.GetDesignSettings()
    bds.m_MinClearance       = to_iu(0.15)
    bds.m_MinTrackWidth      = to_iu(0.2)
    bds.m_MinThroughDrill    = to_iu(0.3)
    bds.m_HoleClearance      = to_iu(0.2)
    bds.m_TrackMinWidth      = to_iu(0.2)
    bds.m_ViasMinSize        = to_iu(0.5)
    # Set the default-net-class clearance too — DRC uses the netclass
    # clearance for net-pair checks, not just m_MinClearance.
    ncs = board.GetAllNetClasses()
    for name in ncs.keys():
        nc = ncs[name]
        try:
            nc.SetClearance(to_iu(0.15))
        except Exception:
            pass
    add_outline(board)
    route(board)
    add_gnd_zones(board)
    n_fp = len(list(board.GetFootprints()))
    n_tk = len(list(board.GetTracks()))
    n_zn = len(list(board.Zones()))
    pcbnew.SaveBoard(str(PCB), board)
    print(f"OK: {n_fp} footprints, {n_tk} tracks/vias, {n_zn} zones")
    # pcbnew's SWIG wrappers leak BOARD/PCB_TRACK/etc during Python's
    # normal teardown and intermittently segfault — bypass cleanup.
    import os
    os._exit(0)

if __name__ == "__main__":
    main()
