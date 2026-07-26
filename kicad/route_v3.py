"""Autoroute the v3.2 board: KiCad -> Specctra DSN -> Freerouting -> SES -> KiCad.

build_v3.py deliberately produces an unrouted board (its own v2 routing logic
no longer matches the v3 placements). This script closes that gap without a
GUI, so the whole board is reproducible from source.

Freerouting 2.x is compiled for Java 25. The system JDK here is 21, so we use
the local JRE 25 unpacked under .kicad-mcp -- see JAVA below. Neither jar that
ships with KiCad will start under 21; the error is a bare
UnsupportedClassVersionError naming "class file version 69.0".

    "K:\\Program Files\\KiCad\\10.0\\bin\\python.exe" kicad\\route_v3.py
"""
import os
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(r"I:\code\ah-my-groin-button\kicad")
PCB  = HERE / "ahmygroin.kicad_pcb"
DSN  = HERE / "ahmygroin.dsn"
SES  = HERE / "ahmygroin.ses"

# Freerouting 2.x needs Java 25; a system JDK 21 cannot start it. Point these
# at your own JRE and jar, or set ROUTE_JAVA / ROUTE_JAR in the environment.
# See PINOUTS.md "Routing" for how this toolchain is set up.
JAVA = Path(os.environ.get(
    "ROUTE_JAVA",
    Path.home() / r".kicad-mcp\jre25\jdk-25.0.3+9-jre\bin\java.exe"))
JAR  = Path(os.environ.get(
    "ROUTE_JAR",
    Path.home() / (r"Documents\KiCad\10.0\3rdparty\plugins"
                   r"\app_freerouting_kicad-plugin\jar\freerouting-2.2.0.jar")))

PASSES = "100"


def _remove_all(board, items):
    """Delete board items via a materialised list.

    Mutating the container while iterating it segfaults in the SWIG
    bindings rather than raising, so build the list first.
    """
    doomed = list(items)
    for item in doomed:
        board.Remove(item)
    return len(doomed)


def export_dsn():
    """Strip old tracks from the real board, then export a zone-free copy.

    Freerouting treats pre-existing traces as fixed obstacles, so re-routing
    on top of an old attempt converges badly -- hence stripping tracks.

    The zones need to go too, but only from what Freerouting sees. If the
    GND pours are present in the .dsn, Freerouting reads GND as an
    already-poured plane and routes no copper for it at all, leaving every
    ground connection at the mercy of the fill. That fill fragments into
    islands around the dense Q1/Q4 band and silently orphaned C4's ground
    pad. Exporting without the pours forces GND to be routed as real
    tracks; the pours are still in the saved board, so ground ends up with
    both a guaranteed track path and a low-impedance plane over it.
    """
    board = pcbnew.LoadBoard(str(PCB))
    n = _remove_all(board, board.GetTracks())
    if n:
        print("  removed %d pre-existing track/via segments" % n)
    pcbnew.SaveBoard(str(PCB), board)

    tmp = PCB.with_name("_dsn_export.kicad_pcb")
    board = pcbnew.LoadBoard(str(PCB))
    z = _remove_all(board, board.Zones())
    print("  exporting without %d GND pour(s) so GND gets routed as copper" % z)
    pcbnew.SaveBoard(str(tmp), board)

    board = pcbnew.LoadBoard(str(tmp))
    ok = pcbnew.ExportSpecctraDSN(board, str(DSN))
    tmp.unlink(missing_ok=True)
    if not ok or not DSN.exists():
        raise SystemExit("DSN export failed")
    print("  wrote %s (%d KB)" % (DSN.name, DSN.stat().st_size // 1024))


def autoroute():
    if SES.exists():
        SES.unlink()
    cmd = [str(JAVA), "-Djava.awt.headless=true", "-jar", str(JAR),
           "-de", str(DSN), "-do", str(SES), "-mp", PASSES]
    print("  " + " ".join(cmd[3:]))
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    tail = [ln for ln in (p.stdout + p.stderr).splitlines() if ln.strip()]
    for ln in tail[-25:]:
        print("  | " + ln)
    if not SES.exists():
        raise SystemExit("freerouting produced no .ses (exit %d)" % p.returncode)
    print("  wrote %s (%d KB)" % (SES.name, SES.stat().st_size // 1024))


def import_ses():
    board = pcbnew.LoadBoard(str(PCB))
    ok = pcbnew.ImportSpecctraSES(board, str(SES))
    if not ok:
        raise SystemExit("SES import failed")
    pcbnew.SaveBoard(str(PCB), board)


def fill_zones():
    board = pcbnew.LoadBoard(str(PCB))
    zones = board.Zones()
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(zones)
    pcbnew.SaveBoard(str(PCB), board)


def report():
    board = pcbnew.LoadBoard(str(PCB))
    board.BuildConnectivity()
    print("  tracks/vias %d   zones %d (filled %d)   unconnected %d"
          % (len(list(board.GetTracks())),
             len(list(board.Zones())),
             sum(1 for z in board.Zones() if z.IsFilled()),
             board.GetConnectivity().GetUnconnectedCount(True)))


# Each pcbnew stage runs in its own interpreter. Chaining LoadBoard /
# SaveBoard / ExportSpecctraDSN / ImportSpecctraSES inside one process makes
# the SWIG wrapper hand back a bare SwigPyObject partway through -- the board
# handle silently loses its BOARD type and every method call after that dies
# with AttributeError. One stage per process sidesteps it entirely.
STAGES = {
    "export": export_dsn,
    "import": import_ses,
    "fill":   fill_zones,
    "report": report,
}


def run_stage(name):
    p = subprocess.run([sys.executable, "-u", str(Path(__file__).resolve()),
                        name], text=True)
    if p.returncode != 0:
        raise SystemExit("stage '%s' failed (exit %d)" % (name, p.returncode))


def main():
    if not JAVA.exists():
        raise SystemExit("JRE 25 not found at %s" % JAVA)
    print("--- 1/4: export Specctra DSN ---", flush=True)
    run_stage("export")
    print("--- 2/4: freerouting (%s passes) ---" % PASSES, flush=True)
    autoroute()
    print("--- 3/4: import SES ---", flush=True)
    run_stage("import")
    print("--- 4/4: fill GND pours ---", flush=True)
    run_stage("fill")
    run_stage("report")
    print("DONE")
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in STAGES:
        STAGES[sys.argv[1]]()
        sys.stdout.flush()
        os._exit(0)
    main()
