"""Generate the 1:1 paper fit-check sheet for the Ah! My Groin! v3 board.

Run with KiCad's bundled Python (pcbnew is not importable from a system Python):

    "K:\\Program Files\\KiCad\\10.0\\bin\\python.exe" -u kicad\\fitcheck_v3.py

Output:
    kicad/fab/v3.2-fitcheck-USLetter-1to1.pdf

WHY THIS SCRIPT EXISTS
----------------------
The first fit-check sheet was exported ad-hoc with kicad-cli and inherited the
board's page setting, which is A4 (297 x 210 mm). Printed on US Letter
(279.4 x 215.9 mm) every consumer print driver silently rescales to fit the
paper. The board geometry is exact -- J4/J5 pads are at 2.5400 mm pitch and
J6/J7 at 2.5000 mm, with zero accumulated error -- but a rescaled printout
makes the pin spacing drift progressively, so a module laid on the paper
matches at the first pin and is a full pitch out by the last.

`kicad-cli pcb export pdf` has NO --page-size-mode option, so the only way to
control the page is to change it in the board file. This script therefore:

  1. copies the board to a scratch file and rewrites `(paper "A4")` to
     `(paper "USLetter")` -- landscape is KiCad's default for that token;
  2. draws calibration rulers and pitch ladders on User.Drawings so the sheet
     proves its own scale;
  3. exports at --scale 1.

THE POINT OF THE RULERS
-----------------------
A fit-check that can be silently rescaled is worse than no fit-check, because
it fails in the direction of false confidence. The 100 mm bars make a scaling
error measurable rather than merely suspected: if the horizontal bar does not
measure 100 mm, the sheet is void no matter how good the board is. Both axes
are drawn because "fit to page" can scale non-uniformly.
"""
import os
import shutil
import subprocess
import sys

import pcbnew

KICAD_BIN = r"K:\Program Files\KiCad\10.0\bin"
ROOT      = r"I:\code\ah-my-groin-button\kicad"
SRC       = os.path.join(ROOT, "ahmygroin.kicad_pcb")
SCRATCH   = os.path.join(ROOT, "_fitcheck.kicad_pcb")
OUT_DIR   = os.path.join(ROOT, "fab")
OUT_PDF   = os.path.join(OUT_DIR, "v3.2-fitcheck-USLetter-1to1.pdf")

LAYER   = pcbnew.Dwgs_User
LINE_W  = pcbnew.FromMM(0.15)
BOLD_W  = pcbnew.FromMM(0.30)

# US Letter landscape is 279.4 x 215.9 mm. The board sits at x 0..90, y 0..70,
# so everything below y=80 and right of x=100 is free space.
PITCH_PRO_MINI = 2.54   # J4 / J5  -- verified against live pad positions
PITCH_DY_SV17F = 2.50   # J6 / J7  -- verified against live pad positions


def vec(x_mm, y_mm):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def line(board, x1, y1, x2, y2, width=LINE_W):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(vec(x1, y1))
    s.SetEnd(vec(x2, y2))
    s.SetLayer(LAYER)
    s.SetWidth(width)
    board.Add(s)
    return s


def text(board, x, y, msg, size=2.5, thickness=0.3, align='left'):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(msg)
    t.SetPosition(vec(x, y))
    t.SetLayer(LAYER)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    t.SetTextThickness(pcbnew.FromMM(thickness))
    t.SetHorizJustify({'left':   pcbnew.GR_TEXT_H_ALIGN_LEFT,
                       'center': pcbnew.GR_TEXT_H_ALIGN_CENTER}[align])
    board.Add(t)
    return t


def h_ruler(board, x0, y0, length=100.0):
    """Horizontal calibration bar, ticks every 10 mm, drawn downward."""
    line(board, x0, y0, x0 + length, y0, BOLD_W)
    for i in range(0, int(length) + 1, 10):
        tall = (i % 50 == 0)
        line(board, x0 + i, y0, x0 + i, y0 + (5.0 if tall else 3.0))
        if tall:
            text(board, x0 + i, y0 + 9.5, str(i), size=2.5, align='center')
    for i in range(0, int(length)):
        line(board, x0 + i, y0, x0 + i, y0 + 1.5)   # 1 mm minor ticks
    text(board, x0, y0 - 3.0,
         "HORIZONTAL CHECK -- this bar MUST measure exactly 100.0 mm",
         size=3.0, thickness=0.4)


def v_ruler(board, x0, y0, length=100.0):
    """Vertical calibration bar -- catches non-uniform 'fit to page' scaling."""
    line(board, x0, y0, x0, y0 + length, BOLD_W)
    for i in range(0, int(length) + 1, 10):
        tall = (i % 50 == 0)
        line(board, x0, y0 + i, x0 + (5.0 if tall else 3.0), y0 + i)
        if tall:
            text(board, x0 + 7.0, y0 + i + 1.0, str(i), size=2.5)
    for i in range(0, int(length)):
        line(board, x0, y0 + i, x0 + 1.5, y0 + i)
    text(board, x0, y0 - 3.0, "VERTICAL CHECK -- 100.0 mm", size=3.0, thickness=0.4)


def pitch_ladder(board, x0, y0, pitch, count, label):
    """A bare row of ticks at exactly `pitch`. Lay the module's pin row on it.

    This is deliberately independent of the board footprints: if the ladder
    matches the module but the board does not, the footprint is wrong; if the
    ladder does not match the module either, the printout is rescaled.
    """
    span = pitch * (count - 1)
    line(board, x0, y0, x0 + span, y0, BOLD_W)
    for i in range(count):
        line(board, x0 + i * pitch, y0 - 2.5, x0 + i * pitch, y0 + 2.5)
    text(board, x0, y0 - 5.0,
         "%s -- %d pins @ %.2f mm = %.2f mm end to end"
         % (label, count, pitch, span),
         size=2.5, thickness=0.3)


def build_scratch_board():
    board = pcbnew.LoadBoard(SRC)

    text(board, 105.0, 8.0, "PRINT AT 100% / ACTUAL SIZE.", size=5.0, thickness=0.7)
    text(board, 105.0, 16.0, "Turn OFF 'Fit to page' / 'Shrink oversized pages'.",
         size=3.2, thickness=0.4)
    text(board, 105.0, 22.0, "Paper: US LETTER. Verify the rulers before trusting",
         size=3.2, thickness=0.4)
    text(board, 105.0, 27.0, "anything else on this sheet.",
         size=3.2, thickness=0.4)

    text(board, 105.0, 38.0, "Board outline must measure 90.0 x 70.0 mm.",
         size=3.2, thickness=0.4)

    h_ruler(board, 5.0, 90.0, 100.0)
    v_ruler(board, 150.0, 90.0, 100.0)

    pitch_ladder(board, 5.0, 120.0, PITCH_PRO_MINI, 12, "Pro Mini J4/J5")
    pitch_ladder(board, 5.0, 138.0, PITCH_DY_SV17F,  9, "DY-SV17F J6/J7")

    text(board, 5.0, 155.0, "Row spacing: Pro Mini 15.24 mm (0.6 in), "
         "DY-SV17F 20.50 mm.", size=2.8, thickness=0.35)
    text(board, 5.0, 161.0, "Lay each module's pin row on its ladder. It must "
         "match at BOTH ends,", size=2.8, thickness=0.35)
    text(board, 5.0, 167.0, "not just the first pin.", size=2.8, thickness=0.35)

    pcbnew.SaveBoard(SCRATCH, board)


def set_letter_page():
    """Rewrite the page token. kicad-cli has no --page-size-mode for PDF."""
    with open(SCRATCH, "r", encoding="utf-8") as fh:
        src = fh.read()
    if '(paper "A4")' not in src:
        raise SystemExit("FAILED: '(paper \"A4\")' not found in scratch board")
    with open(SCRATCH, "w", encoding="utf-8") as fh:
        fh.write(src.replace('(paper "A4")', '(paper "USLetter")', 1))


def export_pdf():
    os.makedirs(OUT_DIR, exist_ok=True)
    cmd = [
        os.path.join(KICAD_BIN, "kicad-cli.exe"), "pcb", "export", "pdf",
        "--mode-single", "--output", OUT_PDF,
        "--layers", "F.Cu,F.Silkscreen,Edge.Cuts,User.Drawings",
        "--scale", "1",
        "--drill-shape-opt", "2",
        "--black-and-white",
        SCRATCH,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(res.stdout)
    sys.stderr.write(res.stderr)
    if res.returncode != 0:
        raise SystemExit("kicad-cli failed with %d" % res.returncode)


def main():
    build_scratch_board()
    set_letter_page()
    export_pdf()
    try:
        os.remove(SCRATCH)
    except OSError:
        pass
    print("\nwrote %s" % OUT_PDF)
    print("Print at 100%%, then measure the two 100 mm bars before using the sheet.")
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
