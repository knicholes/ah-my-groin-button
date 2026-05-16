"""
Read the schematic netlist (kicadsexpr) and apply it to a fresh PCB:
  * load each footprint from the standard library
  * add it to the board with reference + value
  * assign nets to pads per the netlist's (nets ...) section
The MCP server's sync_schematic_to_board fails on this machine because its
Swig backend can't import pcbnew; this script does the same job using KiCad
10's bundled python (which can).
"""
import sys
from pathlib import Path
import sexpdata
import pcbnew

NETLIST = Path(r"I:\code\ah-my-groin-button\kicad\ahmygroin.net")
PCB     = Path(r"I:\code\ah-my-groin-button\kicad\ahmygroin.kicad_pcb")
FPLIB   = Path(r"K:\Program Files\KiCad\10.0\share\kicad\footprints")

def sym(x):
    return x.value() if isinstance(x, sexpdata.Symbol) else x

def find(node, key):
    """First child of `node` whose head is `key`."""
    for c in node[1:]:
        if isinstance(c, list) and c and sym(c[0]) == key:
            return c
    return None

def find_all(node, key):
    return [c for c in node[1:] if isinstance(c, list) and c and sym(c[0]) == key]

def get_str(node, key):
    n = find(node, key)
    if n is None:
        return None
    return n[1] if len(n) > 1 else ""

def main():
    raw = NETLIST.read_text(encoding="utf-8")
    tree = sexpdata.loads(raw)

    components = find(tree, "components")
    nets       = find(tree, "nets")
    if components is None or nets is None:
        print("ERR: malformed netlist", file=sys.stderr)
        sys.exit(1)

    board = pcbnew.LoadBoard(str(PCB))

    # 1) Walk components, load their footprints into the board.
    placed = {}
    grid_x = pcbnew.FromMM(50)
    grid_y = pcbnew.FromMM(50)
    step   = pcbnew.FromMM(15)
    col = 0
    row = 0
    for comp in find_all(components, "comp"):
        ref      = get_str(comp, "ref")
        value    = get_str(comp, "value") or ""
        fp_full  = get_str(comp, "footprint") or ""
        if not fp_full or ":" not in fp_full:
            print(f"SKIP {ref}: no footprint")
            continue
        lib_name, fp_name = fp_full.split(":", 1)
        lib_path = FPLIB / f"{lib_name}.pretty"
        if not lib_path.exists():
            print(f"FAIL {ref}: library {lib_path} missing")
            sys.exit(1)
        fp = pcbnew.FootprintLoad(str(lib_path), fp_name)
        if fp is None:
            print(f"FAIL {ref}: footprint {fp_full} not found")
            sys.exit(1)
        fp.SetReference(ref)
        fp.SetValue(value)
        # crude initial spread; we'll reposition deliberately later
        x = grid_x + col * step
        y = grid_y + row * step
        fp.SetPosition(pcbnew.VECTOR2I(x, y))
        board.Add(fp)
        placed[ref] = fp
        col += 1
        if col >= 8:
            col = 0
            row += 1
        print(f"  + {ref:<6} {fp_full}")

    # 2) Build NETINFO_ITEMs and assign pads.
    # First pass: collect all unique net names.
    pad_assignments = []  # list of (net_name, ref, pad_number)
    for net in find_all(nets, "net"):
        name = get_str(net, "name")
        if not name or name == "":
            continue
        for node in find_all(net, "node"):
            ref = get_str(node, "ref")
            pin = get_str(node, "pin")
            if ref and pin:
                pad_assignments.append((name, ref, str(pin)))

    # Add NETINFO_ITEMs and remember their codes.
    added_nets = {}
    for net_name, _, _ in pad_assignments:
        if net_name in added_nets:
            continue
        ni = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(ni)
        added_nets[net_name] = ni
    # Assign nets to pads.
    fail = 0
    for net_name, ref, pin in pad_assignments:
        fp = placed.get(ref)
        if fp is None:
            print(f"FAIL pad-assign: footprint {ref} not on board")
            fail += 1
            continue
        pad = fp.FindPadByNumber(pin)
        if pad is None:
            print(f"FAIL pad-assign: {ref} pad {pin} not found on its footprint")
            fail += 1
            continue
        pad.SetNet(added_nets[net_name])
    if fail:
        print(f"{fail} pad assignment(s) failed", file=sys.stderr)
        sys.exit(2)

    pcbnew.SaveBoard(str(PCB), board)
    print(f"OK: placed {len(placed)} footprints, {len(added_nets)} nets, "
          f"{len(pad_assignments)} pad assignments")

if __name__ == "__main__":
    main()
