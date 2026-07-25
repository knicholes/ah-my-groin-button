"""
v3 PCB re-spin — single-shot rebuild from the updated netlist.

Fixes the six Claude-introduced layout bugs (see PINOUTS.md):

  1-3. DY-SV17F footprint (J6/J7) → 1×9 pads each, 2.5 mm metric pin
       pitch, 20.5 mm row pitch; correct pin assignments per PINOUTS.md.
  4.   /CON1, /CON2, /CON3 routed from J8/J9/J10 to J6 pads 9/8/7.
  5.   Pro Mini J5 power pins → /VSYS on pad 1 (RAW),
       /V33 on pad 4 (VCC). Pads 11/12 (D10/D11) un-routed.
  6.   J1 (battery) and J3 (speaker) get '+' / '−' silkscreen markers.

Plus: V33 test point (TP1), C4 relocated out from under U2.

v3.1 fixes (2026-06-07, post-bring-up):

  7. /TRIG_OUT moved from J7 pad 2 (IO1) to J7 pad 1 (IO0). In
     I/O Independent Mode 0, IO0 plays 00001.mp3; IO1 plays 00002.mp3.
  8. /CON3 net folded into /BUSY_IN. The module's CON3/BUSY is one pin
     (J6 pad 7); v3 had J10 pad 2 on a separate /CON3 net that didn't
     reach the module. Now J10 pad 2 is on /BUSY_IN, same net as J6 p7.
  9. R3 added: 10 kΩ 0805 pull-down from /BUSY_IN to /GND, so the chip
     samples CON3=LOW during boot for Independent Mode 0, while the
     module's push-pull BUSY output can still drive HIGH afterward.

v3.2 — REQUIRED, NOT YET IMPLEMENTED (identified 2026-07-25):

 10. Split the /V33 net in two. Right now ("J5","4") and ("J6","5") are
     both on /V33, i.e. the Pro Mini's always-on VCC output is bonded to
     the DY-SV17F's V33 output *and* to the J8/J9/J10 pad-3 jumper rail.
     Two consequences, both bad:
       (a) two regulator outputs are tied together and back-drive;
       (b) CON2 (shunted to that rail on J9 pads 2-3) sits at 3.3 V even
           when Q1 has the module gated off, so current flows into the
           powered-down module through its input protection diodes and
           half-wakes it. Measured 8.7 mA of permanent idle draw on
           Kelly's built v2 board.
     Fix: ("J5","4") → new net "/V33_MCU" (or leave the pad un-routed —
     nothing on this board consumes the Pro Mini's VCC). Leave /V33 fed
     only by ("J6","5"), the module's own V33 output, which correctly
     collapses to 0 V when the gate closes. TP1 stays on /V33.
     Routing at lines ~577-591 must be re-derived accordingly.
     See PINOUTS.md -> "Phantom power".

Pipeline:
  1. Mutate kicad/ahmygroin.net (sexpdata: footprints, pad-nets, TP1).
  2. Build a fresh kicad/ahmygroin.kicad_pcb from the updated netlist
     (sync_netlist-style: load footprints from library, assign nets).
     This avoids SWIG Remove()-related segfaults completely.
  3. Place, route, add silkscreen, override DY pad pitch to 2.5 mm,
     re-draw board outline, drop GND pours. Save.

Run via:
  "K:\\Program Files\\KiCad\\10.0\\bin\\python.exe" -u kicad\\build_v3.py
Roll back with: `git reset --hard <pre-v3-commit>`
"""
import os, sys
from pathlib import Path
import sexpdata
import pcbnew

REPO    = Path(r"I:\code\ah-my-groin-button")
NETLIST = REPO / "kicad" / "ahmygroin.net"
PCB     = REPO / "kicad" / "ahmygroin.kicad_pcb"
FPLIB   = Path(r"K:\Program Files\KiCad\10.0\share\kicad\footprints")

W_PWR = 0.5
W_SIG = 0.25
F_CU  = "F.Cu"
B_CU  = "B.Cu"
EDGE  = "Edge.Cuts"
SILK  = "F.SilkS"

DY_PIN_PITCH_MM = 2.5
DY_ROW_PITCH_MM = 20.5

PLACEMENTS = {
    "H1":  (5,    5,    0),
    "H2":  (85,   5,    0),
    "H3":  (5,    65,   0),
    "H4":  (85,   65,   0),
    "J4":  (15,    8,   0),
    "J5":  (30.24, 8,   0),
    "J6":  (55,    5,   0),
    "J7":  (55 + DY_ROW_PITCH_MM, 5, 0),
    "Q3":  (15,    55,  0),
    "C1":  (30,    50,  0),
    "Q1":  (50,    30,  0),
    "Q4":  (42,    30,  0),
    "R1":  (25,    29.59, 0),
    "R2":  (45,    33,  0),
    "R3":  (62,    46,  0),       # CON3/BUSY pull-down; north-east of J10
    "C2":  (35,    40,  0),
    "C3":  (39,    40,  0),
    "C4":  (50,    40,  0),
    "C5":  (60,    30,  0),       # south of J6 row, west of Q1
    "C6":  (64,    30,  0),
    "J1":  (14,    63,  270),
    "J2":  (28,    63,  270),
    "J3":  (74,    63,  270),
    "J8":  (45,    50,  90),
    "J9":  (55,    50,  90),
    "J10": (65,    50,  90),
    "TP1": (43,    40,  0),
}

FOOTPRINT_CHANGES = {
    "J6": "Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Vertical",
    "J7": "Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Vertical",
}

PAD_NETS = {
    ("J5", "11"): None,
    ("J5", "12"): None,
    ("J5", "1"):  "/VSYS",
    ("J5", "4"):  "/V33",
    ("J6", "1"):  "/SPK_P",
    ("J6", "2"):  "/SPK_N",
    ("J6", "3"):  None,
    ("J6", "4"):  None,
    ("J6", "5"):  "/V33",
    ("J6", "6"):  "/VDFP",
    ("J6", "7"):  "/BUSY_IN",
    ("J6", "8"):  "/CON2",
    ("J6", "9"):  "/CON1",
    ("J7", "1"):  "/TRIG_OUT",
    ("J7", "2"):  None,
    ("J7", "3"):  None,
    ("J7", "4"):  None,
    ("J7", "5"):  None,
    ("J7", "6"):  None,
    ("J7", "7"):  None,
    ("J7", "8"):  None,
    ("J7", "9"):  "/GND",
    ("J10", "2"): "/BUSY_IN",      # v3.1: fold /CON3 into /BUSY_IN
    ("R3", "1"):  "/BUSY_IN",      # v3.1: CON3 pull-down
    ("R3", "2"):  "/GND",
}


# =====================================================================
# Step 1 — netlist mutation (sexpdata)
# =====================================================================

def sym(x):
    return x.value() if isinstance(x, sexpdata.Symbol) else x

def find(node, key):
    for c in node[1:]:
        if isinstance(c, list) and c and sym(c[0]) == key:
            return c
    return None

def find_all(node, key):
    return [c for c in node[1:]
            if isinstance(c, list) and c and sym(c[0]) == key]

def set_str(node, key, value):
    n = find(node, key)
    if n is None:
        node.append([sexpdata.Symbol(key), value])
    elif len(n) == 1:
        n.append(value)
    else:
        n[1] = value


def update_netlist():
    print("--- 1/3: updating netlist ---", flush=True)
    raw  = NETLIST.read_text(encoding="utf-8")
    tree = sexpdata.loads(raw)

    components = find(tree, "components")
    nets       = find(tree, "nets")

    # 1a. Footprint updates on J6, J7
    for comp in find_all(components, "comp"):
        ref_n = find(comp, "ref")
        if not ref_n or len(ref_n) < 2:
            continue
        ref = ref_n[1]
        if ref in FOOTPRINT_CHANGES:
            new_fp = FOOTPRINT_CHANGES[ref]
            set_str(comp, "footprint", new_fp)
            fields = find(comp, "fields")
            if fields:
                for f in find_all(fields, "field"):
                    name_node = find(f, "name")
                    if (name_node and len(name_node) > 1
                            and name_node[1] == "Footprint"
                            and len(f) >= 3):
                        f[2] = new_fp

    # 1b. Add TP1 V33 test point
    has_tp1 = any(
        (find(c, "ref") and len(find(c, "ref")) > 1
         and find(c, "ref")[1] == "TP1")
        for c in find_all(components, "comp")
    )
    if not has_tp1:
        components.append(sexpdata.loads(
            '(comp (ref "TP1") (value "V33") '
            '(footprint "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm") '
            '(fields '
            '(field (name "Footprint") "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm") '
            '(field (name "Datasheet")) '
            '(field (name "Description"))) '
            '(libsource (lib "Connector") (part "TestPoint") '
            '(description "Test point")) '
            '(property (name "Sheetname") (value "")) '
            '(property (name "Sheetfile") (value "ahmygroin.kicad_sch")) '
            '(sheetpath (names "/") (tstamps "/")) '
            '(tstamps "tp1-v33-test-point"))'
        ))

    # 1b-bis (v3.1). Add R3 10 kΩ CON3 pull-down.
    has_r3 = any(
        (find(c, "ref") and len(find(c, "ref")) > 1
         and find(c, "ref")[1] == "R3")
        for c in find_all(components, "comp")
    )
    if not has_r3:
        components.append(sexpdata.loads(
            '(comp (ref "R3") (value "10k") '
            '(footprint "Resistor_SMD:R_0805_2012Metric") '
            '(fields '
            '(field (name "Footprint") "Resistor_SMD:R_0805_2012Metric") '
            '(field (name "Datasheet")) '
            '(field (name "Description") "CON3/BUSY pull-down to GND")) '
            '(libsource (lib "Device") (part "R") (description "Resistor")) '
            '(property (name "Sheetname") (value "")) '
            '(property (name "Sheetfile") (value "ahmygroin.kicad_sch")) '
            '(sheetpath (names "/") (tstamps "/")) '
            '(tstamps "r3-con3-pulldown"))'
        ))

    # 1c. Pad-net updates
    existing = {}
    for net_node in find_all(nets, "net"):
        for node_node in find_all(net_node, "node"):
            r = find(node_node, "ref")
            p = find(node_node, "pin")
            if r and p and len(r) > 1 and len(p) > 1:
                existing[(r[1], str(p[1]))] = (net_node, node_node)

    for (ref, pin), want_net in PAD_NETS.items():
        cur = existing.get((ref, pin))
        if cur is not None:
            net_node, node_node = cur
            cur_name = find(net_node, "name")[1] if find(net_node, "name") else None
            if want_net == cur_name:
                continue
            net_node.remove(node_node)
        if want_net is None:
            continue
        target = None
        for net_node in find_all(nets, "net"):
            nn = find(net_node, "name")
            if nn and len(nn) > 1 and nn[1] == want_net:
                target = net_node
                break
        if target is None:
            continue
        target.append(sexpdata.loads(
            f'(node (ref "{ref}") (pin "{pin}") '
            f'(pinfunction "Pin_{pin}_{pin}") (pintype "passive"))'
        ))

    # TP1 → /V33
    for net_node in find_all(nets, "net"):
        nn = find(net_node, "name")
        if nn and len(nn) > 1 and nn[1] == "/V33":
            already = any(
                (find(nd, "ref") and find(nd, "ref")[1] == "TP1")
                for nd in find_all(net_node, "node")
            )
            if not already:
                net_node.append(sexpdata.loads(
                    '(node (ref "TP1") (pin "1") (pintype "passive"))'
                ))
            break

    NETLIST.write_text(sexpdata.dumps(tree), encoding="utf-8")
    print(f"  netlist written: {NETLIST}")


# =====================================================================
# Step 2 — build fresh PCB from netlist (sync_netlist-style)
# =====================================================================

def build_fresh_pcb():
    print("--- 2/3: building fresh PCB from netlist ---", flush=True)
    raw  = NETLIST.read_text(encoding="utf-8")
    tree = sexpdata.loads(raw)
    components = find(tree, "components")
    nets       = find(tree, "nets")

    # Start with an empty board
    if PCB.exists():
        PCB.unlink()
    board = pcbnew.BOARD()

    # Walk components, load footprints, place stub
    placed = {}
    for comp in find_all(components, "comp"):
        ref     = find(comp, "ref")[1] if find(comp, "ref") else None
        value   = find(comp, "value")[1] if find(comp, "value") else ""
        fp_full = find(comp, "footprint")[1] if find(comp, "footprint") else ""
        if not fp_full or ":" not in fp_full:
            print(f"  SKIP {ref}: no footprint")
            continue
        lib_name, fp_name = fp_full.split(":", 1)
        lib_path = FPLIB / f"{lib_name}.pretty"
        if not lib_path.exists():
            print(f"  FAIL {ref}: library {lib_path} missing")
            sys.exit(1)
        fp = pcbnew.FootprintLoad(str(lib_path), fp_name)
        if fp is None:
            print(f"  FAIL {ref}: footprint {fp_full} not found")
            sys.exit(1)
        fp.SetReference(ref)
        fp.SetValue(value)
        board.Add(fp)
        placed[ref] = fp
    print(f"  loaded {len(placed)} footprints")

    # Pad assignments
    pad_assignments = []
    for net in find_all(nets, "net"):
        name = find(net, "name")[1] if find(net, "name") else None
        if not name:
            continue
        for node in find_all(net, "node"):
            r = find(node, "ref")
            p = find(node, "pin")
            if r and p:
                pad_assignments.append((name, r[1], str(p[1])))

    added_nets = {}
    for net_name, _, _ in pad_assignments:
        if net_name in added_nets:
            continue
        ni = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(ni)
        added_nets[net_name] = ni
    for net_name, ref, pin in pad_assignments:
        fp = placed.get(ref)
        if fp is None:
            continue
        pad = fp.FindPadByNumber(pin)
        if pad is None:
            continue
        pad.SetNet(added_nets[net_name])

    return board, placed


# =====================================================================
# Step 3 — place + route + silkscreen
# =====================================================================

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

def add_via(board, x, y, net):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(vec(x, y))
    v.SetDrill(to_iu(0.4))
    v.SetWidth(to_iu(0.8))
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

def get_pad_pos_cache(fp_cache, ref, pad_num):
    fp = fp_cache.get(ref)
    if fp is None:
        raise RuntimeError(f"no footprint {ref}")
    pad = fp.FindPadByNumber(str(pad_num))
    if pad is None:
        raise RuntimeError(f"{ref} pad {pad_num} not found")
    p = pad.GetPosition()
    return (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))

def place_all(board, placed):
    for ref, (x, y, rot) in PLACEMENTS.items():
        fp = placed.get(ref)
        if fp is None:
            print(f"  WARN: footprint {ref} not on board")
            continue
        fp.SetPosition(vec(x, y))
        fp.SetOrientationDegrees(rot)
    gnd = get_net(board, "GND")
    for ref in ("H1", "H2", "H3", "H4"):
        fp = placed.get(ref)
        if fp:
            for pad in fp.Pads():
                pad.SetNet(gnd)
    vsys = get_net(board, "VSYS")
    c1 = placed.get("C1")
    if c1:
        for pad in c1.Pads():
            if pad.GetNumber() == "1":
                pad.SetNet(vsys)
            elif pad.GetNumber() == "2":
                pad.SetNet(gnd)


def override_dy_pad_pitch(board, placed):
    """Standard PinHeader_1x09_P2.54mm has 2.54 mm pitch; the DY-SV17F
    module is metric 2.5 mm. Shift each pad to its true metric position."""
    for ref in ("J6", "J7"):
        fp = placed.get(ref)
        if fp is None:
            continue
        origin = fp.GetPosition()
        for i in range(1, 10):
            pad = fp.FindPadByNumber(str(i))
            if pad is None:
                continue
            pad.SetPosition(pcbnew.VECTOR2I(
                origin.x,
                origin.y + to_iu((i - 1) * DY_PIN_PITCH_MM),
            ))


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


def add_silk_text(board, text, x_mm, y_mm, size_mm=1.2, rotation=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(vec(x_mm, y_mm))
    t.SetLayer(board.GetLayerID(SILK))
    t.SetTextSize(pcbnew.VECTOR2I(to_iu(size_mm), to_iu(size_mm)))
    t.SetTextThickness(to_iu(0.2))
    t.SetTextAngle(pcbnew.EDA_ANGLE(rotation, pcbnew.DEGREES_T))
    board.Add(t)


def add_polarity_silkscreen(board, placed):
    # J1, J3 are 270°-rotated JST-XH 2-pin; the silk body of the footprint
    # extends to the +x side of the pin column, so polarity text goes to
    # the -x side to clear the silk rectangle.
    j1_p1 = get_pad_pos_cache(placed, "J1", 1)
    j1_p2 = get_pad_pos_cache(placed, "J1", 2)
    add_silk_text(board, "+", j1_p1[0] - 5.0, j1_p1[1])
    add_silk_text(board, "-", j1_p2[0] - 5.0, j1_p2[1])

    j3_p1 = get_pad_pos_cache(placed, "J3", 1)
    j3_p2 = get_pad_pos_cache(placed, "J3", 2)
    add_silk_text(board, "+", j3_p1[0] - 5.0, j3_p1[1])
    add_silk_text(board, "-", j3_p2[0] - 5.0, j3_p2[1])

    tp1 = PLACEMENTS["TP1"]
    add_silk_text(board, "V33", tp1[0] + 1.8, tp1[1])


def route(board, placed):
    P = lambda r, p: get_pad_pos_cache(placed, r, p)

    j1_1 = P("J1", 1)
    q3_S = P("Q3", 2)
    chain(board, "VBATT", F_CU, W_PWR,
          j1_1, (q3_S[0], j1_1[1]), q3_S)

    q3_D = P("Q3", 3)
    c1_p = P("C1", 1)
    j5_1 = P("J5", 1)
    q1_S = P("Q1", 2)
    c2_1 = P("C2", 1)
    c3_1 = P("C3", 1)
    r2_1 = P("R2", 1)
    chain(board, "VSYS", F_CU, W_PWR, q3_D, (q3_D[0], c1_p[1]), c1_p)
    chain(board, "VSYS", F_CU, W_PWR, c1_p, (30.0, 50.0))
    chain(board, "VSYS", F_CU, W_PWR, c1_p,
          (j5_1[0] - 2, c1_p[1]),
          (j5_1[0] - 2, j5_1[1]),
          j5_1)
    spine_y = j5_1[1]
    chain(board, "VSYS", F_CU, W_PWR, j5_1, (q1_S[0], spine_y), q1_S)
    chain(board, "VSYS", F_CU, W_PWR,
          (c2_1[0], spine_y), (c2_1[0], c2_1[1]))
    chain(board, "VSYS", F_CU, W_PWR,
          (c3_1[0], spine_y), (c3_1[0], c3_1[1]))
    chain(board, "VSYS", F_CU, W_PWR,
          (r2_1[0], spine_y), (r2_1[0], r2_1[1]))

    q1_D = P("Q1", 3)
    c4_p = P("C4", 1)
    c5_p = P("C5", 1)
    c6_p = P("C6", 1)
    j6_6 = P("J6", 6)
    chain(board, "VDFP", F_CU, W_PWR, q1_D, (q1_D[0], c4_p[1]), c4_p)
    chain(board, "VDFP", F_CU, W_PWR,
          c4_p, (c5_p[0], c4_p[1]), c5_p)
    chain(board, "VDFP", F_CU, W_PWR, c5_p, c6_p)
    chain(board, "VDFP", F_CU, W_PWR,
          c5_p, (c5_p[0], 4),
          (j6_6[0] + 1.5, 4))
    via_at(board, "VDFP", j6_6[0] + 1.5, 4)
    chain(board, "VDFP", B_CU, W_PWR,
          (j6_6[0] + 1.5, 4),
          (j6_6[0] + 1.5, j6_6[1]),
          j6_6)

    j6_1 = P("J6", 1)
    j3_1 = P("J3", 1)
    chain(board, "SPK_P", F_CU, W_PWR,
          j6_1, (j6_1[0] - 3, j6_1[1]),
          (j6_1[0] - 3, 60),
          (j3_1[0], 60), j3_1)

    q1_G = P("Q1", 1)
    r2_2 = P("R2", 2)
    q4_C = P("Q4", 3)
    chain(board, "Q1_GATE", F_CU, W_SIG,
          r2_2, (r2_2[0], q1_G[1]), q1_G)
    chain(board, "Q1_GATE", F_CU, W_SIG,
          q1_G, (q4_C[0], q1_G[1]), q4_C)

    r1_2 = P("R1", 2)
    q4_B = P("Q4", 1)
    chain(board, "Q4_BASE", F_CU, W_SIG,
          r1_2, (q4_B[0], r1_2[1]), q4_B)

    j4_8 = P("J4", 8)
    r1_1 = P("R1", 1)
    chain(board, "GATE_CTRL", F_CU, W_SIG,
          j4_8, (17, j4_8[1]), (17, r1_1[1]), r1_1)

    j5_4  = P("J5", 4)
    tp1_p = P("TP1", 1)
    j8_3  = P("J8", 3)
    j9_3  = P("J9", 3)
    j10_3 = P("J10", 3)
    j6_5  = P("J6", 5)
    chain(board, "V33", F_CU, 0.4,
          j5_4, (j5_4[0] + 4, j5_4[1]),
          (j5_4[0] + 4, 19))
    via_at(board, "V33", j5_4[0] + 4, 19)
    chain(board, "V33", B_CU, 0.4,
          (j5_4[0] + 4, 19), (j5_4[0] + 4, tp1_p[1]),
          tp1_p)
    chain(board, "V33", B_CU, 0.4,
          tp1_p, (tp1_p[0], 53), (j8_3[0], 53))
    chain(board, "V33", B_CU, 0.4, (j8_3[0], 53), j8_3)
    chain(board, "V33", B_CU, 0.4, (j8_3[0], 53), (j9_3[0], 53))
    chain(board, "V33", B_CU, 0.4, (j9_3[0], 53), j9_3)
    chain(board, "V33", B_CU, 0.4, (j9_3[0], 53), (j10_3[0], 53))
    chain(board, "V33", B_CU, 0.4, (j10_3[0], 53), j10_3)
    chain(board, "V33", B_CU, 0.4,
          (j10_3[0], 53),
          (j6_5[0] - 2, 53),
          (j6_5[0] - 2, j6_5[1]),
          j6_5)

    j6_9 = P("J6", 9)
    j6_8 = P("J6", 8)
    j6_7 = P("J6", 7)
    j8_2 = P("J8", 2)
    j9_2 = P("J9", 2)
    j10_2 = P("J10", 2)
    chain(board, "CON1", F_CU, W_SIG,
          j8_2, (j8_2[0], j6_9[1]), j6_9)
    chain(board, "CON2", F_CU, W_SIG,
          j9_2, (j9_2[0], j6_8[1]), j6_8)

    j4_5 = P("J4", 5)
    j2_1 = P("J2", 1)
    chain(board, "BTN_IN", B_CU, W_SIG,
          j4_5, (12, j4_5[1]), (12, 60),
          (j2_1[0], 60), j2_1)

    j4_9 = P("J4", 9)
    j7_1 = P("J7", 1)
    chain(board, "TRIG_OUT", B_CU, W_SIG,
          j4_9, (17, j4_9[1]), (17, 27),
          (j7_1[0] - 2, 27), (j7_1[0] - 2, j7_1[1]), j7_1)

    j4_10 = P("J4", 10)
    chain(board, "BUSY_IN", B_CU, W_SIG,
          j4_10, (17, j4_10[1]), (17, 32.13),
          (j6_7[0] - 2, 32.13),
          (j6_7[0] - 2, j6_7[1]), j6_7)
    chain(board, "BUSY_IN", B_CU, W_SIG,
          (j6_7[0] - 2, j6_7[1]),
          (j6_7[0] - 2, 42),
          (j10_2[0], 42), j10_2)

    # v3.1: R3 (10k) pulls /BUSY_IN to /GND via the J10 jumper rail
    r3_1 = P("R3", 1)
    r3_2 = P("R3", 2)
    chain(board, "BUSY_IN", B_CU, W_SIG,
          (j10_2[0], 42), (j10_2[0], r3_1[1]), r3_1)
    j10_1 = P("J10", 1)
    chain(board, "GND", B_CU, W_SIG,
          r3_2, (r3_2[0], j10_1[1]), j10_1)

    j6_2 = P("J6", 2)
    j3_2 = P("J3", 2)
    chain(board, "SPK_N", B_CU, W_PWR,
          j6_2, (j6_2[0] - 4, j6_2[1]),
          (j6_2[0] - 4, 60), (j3_2[0], 60), j3_2)


def add_gnd_zones(board):
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
        outline = z.Outline()
        outline.RemoveAllContours()
        outline.NewOutline()
        for x, y in [(0.2, 0.2), (89.8, 0.2), (89.8, 69.8), (0.2, 69.8)]:
            outline.Append(to_iu(x), to_iu(y))
        board.Add(z)


def main():
    update_netlist()

    board, placed = build_fresh_pcb()

    bds = board.GetDesignSettings()
    bds.m_MinClearance       = to_iu(0.15)
    bds.m_MinTrackWidth      = to_iu(0.2)
    bds.m_MinThroughDrill    = to_iu(0.3)
    bds.m_HoleClearance      = to_iu(0.2)
    bds.m_TrackMinWidth      = to_iu(0.2)
    bds.m_ViasMinSize        = to_iu(0.5)
    try:
        ncs = board.GetAllNetClasses()
        for name in ncs.keys():
            try:
                ncs[name].SetClearance(to_iu(0.15))
            except Exception:
                pass
    except Exception:
        pass

    print("--- 3/3: place + outline + GND zones (no routing) ---", flush=True)
    place_all(board, placed)
    override_dy_pad_pitch(board, placed)
    add_outline(board)
    # Skip route() — the v2 routing logic doesn't fit v3 placements
    # (C4/C5/C6/J7 moved, J6 pad map changed). Leave the board as a
    # ratsnest; the user runs the autorouter or hand-routes in the GUI.
    # See PINOUTS.md §v3 routing notes.
    add_gnd_zones(board)

    # Capture polarity-text positions BEFORE save (need pad positions).
    # J1/J3 are 270°-rotated JST-XH whose silk body sits on the +x side
    # of the pin column; polarity text goes to the -x side to clear it.
    silk_text = [
        ("+", get_pad_pos_cache(placed, "J1", 1)[0] - 5.0,
              get_pad_pos_cache(placed, "J1", 1)[1]),
        ("-", get_pad_pos_cache(placed, "J1", 2)[0] - 5.0,
              get_pad_pos_cache(placed, "J1", 2)[1]),
        ("+", get_pad_pos_cache(placed, "J3", 1)[0] - 5.0,
              get_pad_pos_cache(placed, "J3", 1)[1]),
        ("-", get_pad_pos_cache(placed, "J3", 2)[0] - 5.0,
              get_pad_pos_cache(placed, "J3", 2)[1]),
        ("V33", PLACEMENTS["TP1"][0] + 2.5, PLACEMENTS["TP1"][1]),
    ]

    pcbnew.SaveBoard(str(PCB), board)
    n_fp = len(list(board.GetFootprints()))
    n_tk = len(list(board.GetTracks()))
    n_zn = len(list(board.Zones()))
    print(f"saved: {n_fp} footprints, {n_tk} tracks/vias, {n_zn} zones")

    # --- post-save: inject silkscreen text via sexpdata ---
    print("--- 4/4: silkscreen via sexpdata ---", flush=True)
    raw = PCB.read_text(encoding="utf-8")
    tree = sexpdata.loads(raw)
    import uuid as uuid_mod
    for txt, x, y in silk_text:
        block = sexpdata.loads(
            f'(gr_text "{txt}" (at {x} {y}) (layer "F.SilkS") '
            f'(uuid "{uuid_mod.uuid4()}") '
            f'(effects (font (size 1.2 1.2) (thickness 0.2))))'
        )
        tree.append(block)
    PCB.write_text(sexpdata.dumps(tree), encoding="utf-8")

    b2 = pcbnew.LoadBoard(str(PCB))
    print(f"SANITY: re-load ok={b2 is not None}", flush=True)
    print("DONE")
    os._exit(0)


if __name__ == "__main__":
    main()
