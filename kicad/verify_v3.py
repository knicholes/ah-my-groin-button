"""Pre-fabrication verification for the "Ah! My Groin!" v3.2 board.

Run this after build_v3.py and after any routing pass. It checks the two
classes of defect that KiCad's own DRC structurally cannot see:

  1. MODULE BODY COLLISIONS. J4/J5 and J6/J7 are plain pin headers. Their
     courtyards cover the header strips only -- not the Pro Mini PCB or the
     DY-SV17F package that plug into them and overhang in every direction.
     DRC therefore happily passes a board with a resistor pinned under a
     module. This was v2 bug #1 and it cost a whole fabrication round.

  2. ELECTRICAL INTENT. Netlist assertions for the rules that are correct-
     looking but wrong: the phantom-power rule (nothing always-on may touch
     the gated module) and the reverse-polarity FET orientation.

Exit code is 0 only when every check passes.

    "K:\\Program Files\\KiCad\\10.0\\bin\\python.exe" kicad\\verify_v3.py
"""
import os
import sys
from collections import defaultdict

import pcbnew

PCB = r"I:\code\ah-my-groin-button\kicad\ahmygroin.kicad_pcb"

# --- module body geometry -------------------------------------------------
# Bodies are derived from the pads they sit on, never hard-coded, so that
# moving a header in build_v3.py automatically moves its keep-out.
#
#   ref_a/ref_b  the two header rows the module straddles
#   across       body dimension measured across the two rows
#   along        body dimension measured along one row
BODIES = [
    # DY-SV17F DIP-18: datasheet body 26.3 x 23.08 mm, 2.5 mm pin pitch,
    # 20.5 mm row pitch. 23.08 is across the rows, 26.3 along them.
    dict(name="DY-SV17F", a="J6", b="J7", across=23.08, along=26.30),
    # Pro Mini: 0.7" x 1.3" = 17.78 x 33.02 mm, 0.6" row pitch.
    dict(name="Pro Mini", a="J4", b="J5", across=17.78, along=33.02),
]

# Footprints allowed to sit inside a body keep-out (the module's own headers).
BODY_EXEMPT = {"J4", "J5", "J6", "J7"}

BOARD_W, BOARD_H = 90.0, 70.0
EDGE_MARGIN = 0.3          # body must stay this far inside the outline


def iu(v):
    return pcbnew.ToMM(v)


def pad_positions(board, ref):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        raise SystemExit("missing footprint: %s" % ref)
    return [(iu(p.GetPosition().x), iu(p.GetPosition().y)) for p in fp.Pads()]


def body_rect(board, spec):
    """Return (x0, y0, x1, y1) of the module package outline in mm."""
    pts = pad_positions(board, spec["a"]) + pad_positions(board, spec["b"])
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0

    # "across" is measured on the axis that separates the two header rows,
    # "along" on the axis the pins march down. Compare header centroids --
    # comparing overall pad spread gets it wrong whenever a module happens
    # to be nearly square in pad extent, as the DY-SV17F is (20.5 vs 20.0).
    def centroid(ref):
        pts = pad_positions(board, ref)
        return (sum(p[0] for p in pts) / len(pts),
                sum(p[1] for p in pts) / len(pts))

    ax, ay = centroid(spec["a"])
    bx, by = centroid(spec["b"])
    if abs(bx - ax) >= abs(by - ay):
        w, h = spec["across"], spec["along"]     # rows separated in x
    else:
        w, h = spec["along"], spec["across"]     # rows separated in y
    return (cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0)


def fp_bbox(fp):
    bb = fp.GetBoundingBox(False, False)   # pads + graphics, no text
    return (iu(bb.GetLeft()), iu(bb.GetTop()),
            iu(bb.GetRight()), iu(bb.GetBottom()))


def overlap(r1, r2):
    return not (r1[2] <= r2[0] or r2[2] <= r1[0] or
                r1[3] <= r2[1] or r2[3] <= r1[1])


def check_bodies(board):
    problems = []
    for spec in BODIES:
        rect = body_rect(board, spec)
        print("  %-10s body  x[%6.2f %6.2f]  y[%6.2f %6.2f]"
              % (spec["name"], rect[0], rect[2], rect[1], rect[3]))

        if (rect[0] < EDGE_MARGIN or rect[1] < EDGE_MARGIN or
                rect[2] > BOARD_W - EDGE_MARGIN or
                rect[3] > BOARD_H - EDGE_MARGIN):
            problems.append("%s body overhangs the board outline" % spec["name"])

        for fp in board.GetFootprints():
            ref = fp.GetReference()
            if ref in BODY_EXEMPT:
                continue
            fb = fp_bbox(fp)
            if overlap(rect, fb):
                problems.append(
                    "%s (%s) sits under the %s body -- unreachable after "
                    "assembly  [part x%.2f..%.2f y%.2f..%.2f]"
                    % (ref, fp.GetValue(), spec["name"],
                       fb[0], fb[2], fb[1], fb[3]))

    # bodies must not overlap each other
    for i in range(len(BODIES)):
        for j in range(i + 1, len(BODIES)):
            if overlap(body_rect(board, BODIES[i]), body_rect(board, BODIES[j])):
                problems.append("%s and %s bodies overlap"
                                % (BODIES[i]["name"], BODIES[j]["name"]))
    return problems


def nets(board):
    d = defaultdict(set)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            nn = pad.GetNetname()
            if nn:
                d[nn].add("%s.%s" % (fp.GetReference(), pad.GetNumber()))
    return d


def check_nets(board):
    n = nets(board)
    problems = []

    def require(net, pad, why):
        if pad not in n.get(net, ()):
            problems.append("%s must be on %s -- %s" % (pad, net, why))

    def forbid(net, pad, why):
        if pad in n.get(net, ()):
            problems.append("%s must NOT be on %s -- %s" % (pad, net, why))

    # --- phantom power: nothing always-on may reach the gated module ---
    forbid("/V33", "J5.4",
           "Pro Mini VCC is always on; bonding it to the jumper rail "
           "back-feeds CON2 into the gated module (14 mA idle drain)")
    require("/V33", "J6.5",
           "the jumper rail's 3.3 V must come from the module's own V33 "
           "output, which dies when Q1 gates the module off")
    for pad in ("J8.3", "J9.3", "J10.3"):
        require("/V33", pad, "mode-select jumper HIGH reference")

    # --- reverse-polarity P-FET: drain to the battery, source to the load ---
    require("/VBATT", "Q3.3", "drain faces the battery (counterintuitive but "
                              "correct: the body diode must reverse-bias on a "
                              "flipped cell)")
    require("/VSYS",  "Q3.2", "source faces the load")
    require("/GND",   "Q3.1", "gate to ground")
    forbid("/VBATT", "Q3.2", "source on the battery side = no protection")

    # --- load switch Q1 (high-side P-FET, gate pulled down by Q4) ---
    require("/VSYS",     "Q1.2", "Q1 source on the always-on rail")
    require("/VDFP",     "Q1.3", "Q1 drain feeds the module")
    require("/Q1_GATE",  "Q1.1", "Q1 gate")
    require("/VSYS",     "R2.1", "R2 holds the gate at the source")
    require("/Q1_GATE",  "R2.2", "R2 holds the gate at the source")

    # --- CON3 / BUSY pull-down (v3.1) ---
    require("/BUSY_IN", "R3.1", "CON3 must be held low, not floating")
    require("/GND",     "R3.2", "CON3 pull-down")

    # --- second Pro Mini ground ---
    require("/GND", "J5.2", "Pro Mini has a ground on each header row")

    # --- no net may be left with a single pad (a dangling connection) ---
    for name, pads in sorted(n.items()):
        refs = {p.split(".")[0] for p in pads}
        if len(refs) < 2:
            problems.append("net %s reaches only %s -- dangling"
                            % (name, ", ".join(sorted(pads))))
    return problems


def check_silkscreen(board):
    """Silk text must not land on a pad or run off the board.

    Silk over a pad gets squeegeed away by solder paste / wicks into the
    joint, so the label you most needed is the one that goes missing. KiCad
    DRC has a "silk over pad" rule but it only fires for footprint silk,
    not the free-standing gr_text this build injects.
    """
    problems = []
    pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            pads.append(("%s.%s" % (fp.GetReference(), p.GetNumber()),
                         (iu(bb.GetLeft()), iu(bb.GetTop()),
                          iu(bb.GetRight()), iu(bb.GetBottom()))))

    # The layer is written as "F.SilkS" but reads back under its display
    # name "F.Silkscreen"; accept either so this keeps working if that flips.
    texts = [d for d in board.GetDrawings()
             if d.GetClass() == "PCB_TEXT"
             and board.GetLayerName(d.GetLayer()) in ("F.SilkS", "F.Silkscreen")]
    print("  %d free silk texts" % len(texts))

    for t in texts:
        bb = t.GetBoundingBox()
        r = (iu(bb.GetLeft()), iu(bb.GetTop()),
             iu(bb.GetRight()), iu(bb.GetBottom()))
        label = t.GetText()
        if (r[0] < 0 or r[1] < 0 or r[2] > BOARD_W or r[3] > BOARD_H):
            problems.append('silk "%s" runs off the board edge '
                            "[x%.2f..%.2f y%.2f..%.2f]"
                            % (label, r[0], r[2], r[1], r[3]))
        for ref, pr in pads:
            if overlap(r, pr):
                problems.append('silk "%s" overlaps pad %s' % (label, ref))
                break
    return problems


def check_routing(board):
    """Informational: how much of the board is actually routed."""
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    unrouted = conn.GetUnconnectedCount(True)
    tracks = len([t for t in board.GetTracks()])
    zones = len(list(board.Zones()))
    filled = sum(1 for z in board.Zones() if z.IsFilled())
    print("  tracks/vias %d   zones %d (filled %d)   unconnected %d"
          % (tracks, zones, filled, unrouted))
    problems = []
    if unrouted:
        problems.append("%d unconnected item(s) -- board is not fully routed"
                        % unrouted)
    if zones and filled < zones:
        problems.append("%d of %d GND zones are unfilled" % (zones - filled, zones))
    return problems


def main():
    board = pcbnew.LoadBoard(PCB)
    all_problems = []

    print("=== module body keep-outs ===")
    p = check_bodies(board)
    all_problems += p
    print("  -> %d problem(s)" % len(p))

    print("\n=== electrical intent ===")
    p = check_nets(board)
    all_problems += p
    print("  -> %d problem(s)" % len(p))

    print("\n=== silkscreen ===")
    p = check_silkscreen(board)
    all_problems += p
    print("  -> %d problem(s)" % len(p))

    print("\n=== routing completeness ===")
    p = check_routing(board)
    all_problems += p

    print("\n" + "=" * 60)
    if all_problems:
        print("FAIL -- %d problem(s):" % len(all_problems))
        for i, msg in enumerate(all_problems, 1):
            print("  %2d. %s" % (i, msg))
    else:
        print("PASS -- board is ready for fabrication review")
    print("=" * 60)
    sys.stdout.flush()
    os._exit(1 if all_problems else 0)


if __name__ == "__main__":
    main()
