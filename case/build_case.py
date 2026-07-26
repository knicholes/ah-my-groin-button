"""Headless Blender model of the Ah! My Groin! v2 enclosure.

Run with:
    "K:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" \
        --background --python build_case.py

Outputs, all written to the VERSION sub-folder so each box shape keeps its
own model, STLs and renders side by side:
    case.blend      — the editable model
    body.stl        — main case body (top + sides, open at bottom)
    bottom.stl      — removable bottom tray (carries PCB, speaker, battery)
    foot.stl        — single foot puck; print 4× (one per corner)

To start a new box shape: change VERSION, change the dimensions below, and
run. The previous version's folder is left untouched.

ASSEMBLY:
  Bottom tray is a "shelf" inside the case with PCB standoffs, speaker
  mounting bosses and battery clips integrated. Slide everything (PCB,
  speaker, battery) onto the tray, connect the three JST cables, drop
  the tray UP into the case from below, stack a printed foot under each
  corner, and fasten with 4 M3 screws that pass foot → tray → heat-set
  insert in the corner block.

  The feet print as separate pucks (countersink facing UP on the build
  plate, flat side down) so no support material is needed under the
  tray's corners.

GEOMETRY:
    PCB                90 × 70 × 2.0 mm + ~20 mm component height
    Speaker (ADA1313)  77.8 × 77.8 × 25.5 mm
    Button             99 mm flange, 68.65 mm tall, 88 mm mounting hole
                       (microswitch detached and dangling on wires)
    Battery (3×AA)     48.22 × 68.95 × 17.8 mm, measured 2026-07-25.
                       LIES FLAT in its rib pocket on the tray, under the
                       PCB, switch face DOWN. A window cut through the tray
                       exposes the switch from underneath; the case stands
                       on 8 mm feet, so tipping it up reaches the switch.

CASE SHAPE:
    Outer 200 × 130 × 90 mm rectangular prism
    Wall thickness 3.5 mm, outer corner radius 5 mm
    Top integral with body; bottom is a separate removable tray
"""
from pathlib import Path
import math
import struct
import bpy
import bmesh

# ---------------------------------------------------------------------
# Output version. Every generated file lands in case/<VERSION>/.
# ---------------------------------------------------------------------
HERE    = Path(__file__).parent
VERSION = "v1-200x130x110"
OUT_DIR = HERE / VERSION

# ---------------------------------------------------------------------
# Dimensions (mm — internal Blender units)
# ---------------------------------------------------------------------
W, D, H        = 200.0, 130.0, 110.0   # outer case dimensions
# H raised from 90 → 110 to clear the microswitch hanging below the
# arcade button. Total button+microswitch length is 92 mm from dome tip
# to switch terminals; dome sits 26.7 mm above the top panel → 65.3 mm
# hangs below. Speaker stack (tray 3.5 + boss 6 + speaker 25.5) = 35 mm,
# so internal headroom needed is 65.3 + 35 ≈ 100 mm, plus 3.5 mm top
# panel and ~6 mm safety = 110 mm.
WALL           = 3.5                    # side wall thickness
CORNER_R       = 5.0                    # outer corner radius
TOP_TH         = 3.5                    # top panel thickness
BOT_TH         = 3.5                    # bottom tray thickness
PANEL_INSET    = 5.0                    # lip width (so tray rests on it)
TRAY_FIT_GAP   = 0.4                    # slip-fit gap on each side

# Tray footprint. Nothing mounted on the tray may extend past these edges:
# below z=BOT_TH the case opening is narrower than the main cavity, so a part
# hanging over the tray edge collides with the lip as the tray is pushed up
# into place. This is what forbids sliding the battery further forward.
TRAY_X     = W - 2*WALL - 2*PANEL_INSET - 2*TRAY_FIT_GAP
TRAY_Y     = D - 2*WALL - 2*PANEL_INSET - 2*TRAY_FIT_GAP
TRAY_MIN_Y = D/2 - TRAY_Y/2             # 8.9 mm — front edge of the tray

# Corner attachment blocks (where bottom-tray screws go)
CORNER_BLOCK   = 12.0                   # block width (square in plan)
CORNER_BLOCK_H = 12.0                   # block height above lip
INSERT_BORE_D  = 4.2                    # M3 heat-set insert hole
SCREW_CLEAR_D  = 3.4                    # M3 clearance through tray
COUNTERSINK_D  = 6.5                    # M3 countersink head diameter
COUNTERSINK_H  = 1.8                    # countersink depth

# Feet — lift the case off the resting surface so the downward-firing
# speaker isn't muffled. Printed as SEPARATE pucks (flat side on build
# plate, countersink facing up) so no support material is wasted under
# the tray. A single M3 passes through foot → tray → heat-set insert in
# the corner block above. With FOOT_H=8 the required screw length is
# FOOT_H + BOT_TH + CORNER_BLOCK_H = 23.5 mm → use M3×25.
FOOT_OD        = 14.0
FOOT_H         = 8.0

# Button — left half of the case
BTN_CX, BTN_CY = 55.0, 65.0
BTN_HOLE_D     = 88.0                   # mounting hole through top panel
BTN_FLANGE_D   = 99.0                   # outer flange, measured — this is what
                                        # hides the notches, so it bounds them
BTN_TOTAL_H    = 68.65                  # dome tip to the end of the barrel
BTN_BODY_D     = 78.0                   # body diameter below panel
BTN_BODY_LEN   = 50.0                   # how far the body hangs below. Kept
                                        # conservative: the whole button is
                                        # only 68.65 mm, so 50 mm below the
                                        # panel over-reserves whatever the
                                        # above/below split actually is.
BTN_REINF_R    = 50.0                   # reinforcement ring outer radius
BTN_REINF_TH   = 6.0                    # reinforced zone thickness
# Anti-rotation nubs on the button barrel: two bumps directly opposite each
# other across the button's diameter. They hold the flange up off the panel
# unless the hole is notched for them, so this is a fit problem, not just an
# anti-spin nicety.
#
# Cut a semicircle of BTN_NUB_R centred ON the hole rim: it protrudes
# BTN_NUB_R past the rim and is 2*BTN_NUB_R wide. The earlier values (5.73 mm
# chord, 2.7 mm protrusion) were too small against the physical button.
#
# Angular position is free — the nubs are diametrically opposed, the button is
# round, and the flange overhangs far enough to cover the notches. They sit on
# ±Y rather than ±X because the hole edge is only 7.5 mm from the left inner
# wall in X, which a 4 mm notch would cut to 3.5 mm; on Y there is 13.5 mm.
BTN_NUB_D      = 5.88                   # measured nub diameter
BTN_NUB_R      = 4.0                    # semicircular notch radius — 1.06 mm
                                        # of slop around the nub, and it stays
                                        # 1.5 mm inside the flange rim

# PCB — right half, on standoffs from the tray. The battery lies flat
# underneath it (21.3 mm tall including the tray) with the board at 28.5 mm,
# so they share plan area and only the standoffs need dodging.
PCB_CX, PCB_CY = 145.0, 65.0
PCB_W, PCB_D, PCB_T = 90.0, 70.0, 2.0
PCB_MOUNT_DX   = 40.0                   # ±40 mm from PCB centre (80 mm apart in X)
PCB_MOUNT_DY   = 30.0                   # ±30 mm from PCB centre (60 mm apart in Y)
STANDOFF_OD    = 6.0
STANDOFF_ID    = 2.7                    # M3 self-tapping (or use M3 heat-set)
STANDOFF_H     = 25.0                   # PCB sits this far above the tray inner face

# Speaker (Adafruit ADA1313) — fires DOWN through tray grille, under the
# button area.
SPK_CX, SPK_CY = 55.0, 65.0
SPK_BODY_X, SPK_BODY_Y, SPK_BODY_H = 77.8, 77.8, 25.5
# Grille pattern: concentric rings of round holes (speaker-mesh style).
# Each tuple = (ring_radius_mm, hole_count, hole_dia_mm).
SPK_GRILLE_RINGS = [
    (0,    1,  6.0),
    (10,   6,  5.5),
    (20,  12,  5.5),
    (30,  18,  5.0),
]
# Measured on physical speaker: adjacent hole centres are 58.9 mm apart
# (outer-edge to outer-edge 63.66 mm, inner-edge to inner-edge 54.13–54.2 mm,
# so c-to-c = (63.66 + 54.17) / 2 ≈ 58.9 mm, hole dia ≈ 4.75 mm).
# Bolt-circle radius = 58.9 / √2 ≈ 41.65 mm.
SPK_MOUNT_R    = 41.65                  # bolt circle radius (58.9 mm side)
SPK_MOUNT_BOSS_OD = 6.0
SPK_MOUNT_BOSS_ID = 2.7                 # M3 self-tapping
SPK_MOUNT_BOSS_H  = 6.0

# ---------------------------------------------------------------------
# Battery holder — 3×AA, LIES FLAT on the tray with the switch face DOWN
# ---------------------------------------------------------------------
# Measured on the physical holder 2026-07-25: the switch face is
# 48.22 × 68.95 mm and the box is 17.8 mm thick.
#
# It lies down in the front-right of the tray, under the PCB — where it
# already sat securely. Standing it on edge to reach the switch through a
# side wall was built and then abandoned: it worked, but it traded away a
# pocket that was already good for a problem that a hole in the tray solves.
BAT_LEN, BAT_WIDTH, BAT_HEIGHT = 68.95, 48.22, 17.8   # X, Y, Z as it lies
BAT_FIT        = 0.6                    # printed-pocket clearance per axis
BAT_CX, BAT_CY = 145.0, 40.0            # holder centre on the tray
BAT_RIB_TH     = 2.5                    # rib / end-stop thickness
BAT_RIB_H      = BAT_HEIGHT + 2.0       # ribs stand just proud of the holder
# Central gap in each end stop. It lets the leads out, and — the reason it is
# 20 mm and not 10 — it straddles y=35, where the two front PCB standoffs sit.
# The end stops reach x=182.275 and the standoff at (185, 35) starts at
# x=182.0, so without the gap they would merge into each other.
BAT_END_GAP    = 20.0

BAT_POCKET_L = BAT_LEN + BAT_FIT
BAT_POCKET_W = BAT_WIDTH + BAT_FIT
BAT_X0, BAT_X1 = BAT_CX - BAT_LEN/2,   BAT_CX + BAT_LEN/2     # 110.525 .. 179.475
BAT_Y0, BAT_Y1 = BAT_CY - BAT_WIDTH/2, BAT_CY + BAT_WIDTH/2   #  15.890 ..  64.110

# Switch opening, measured on the holder's switch face from its own top-right
# corner (face held upright, viewed from the front):
#   from the right edge  6.43 .. 17.2 mm    → a 10.77 mm span
#   from the top edge    2.30 .. 12.0 mm    → a  9.70 mm span
#
# Laid down switch-face-DOWN, that face's "top" edge points -X and its "right"
# edge points -Y. Both distances therefore measure inward from BAT_X0 / BAT_Y0.
# The pocket is a plain rectangle, so the holder also drops in rotated 180° —
# in which case the switch lands in the far corner and misses the hole. The
# fix is to spin it; the soldering guide says so.
BAT_SW_FROM_RIGHT = (6.43, 17.2)
BAT_SW_FROM_TOP   = (2.3, 12.0)
BAT_SW_X0 = BAT_X0 + min(BAT_SW_FROM_TOP)      # 112.825
BAT_SW_X1 = BAT_X0 + max(BAT_SW_FROM_TOP)      # 122.525
BAT_SW_Y0 = BAT_Y0 + min(BAT_SW_FROM_RIGHT)    #  22.320
BAT_SW_Y1 = BAT_Y0 + max(BAT_SW_FROM_RIGHT)    #  33.090

# The tray window is oversized around that opening so a fingertip reaches the
# lever through 3.5 mm of tray, and a shallow scallop on the underside gives
# the finger a lead-in.
BAT_WIN_MARGIN    = 2.0
BAT_WIN_X0, BAT_WIN_X1 = BAT_SW_X0 - BAT_WIN_MARGIN, BAT_SW_X1 + BAT_WIN_MARGIN
BAT_WIN_Y0, BAT_WIN_Y1 = BAT_SW_Y0 - BAT_WIN_MARGIN, BAT_SW_Y1 + BAT_WIN_MARGIN
BAT_WIN_SCALLOP   = 3.0                 # how far the lead-in oversizes it
BAT_WIN_SCALLOP_D = 1.5                 # depth of the lead-in

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)

def add_cube(name, sx, sy, sz, cx, cy, cz):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

def add_cyl(name, r, depth, cx, cy, cz, axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=r, depth=depth, location=(cx, cy, cz), vertices=64)
    obj = bpy.context.active_object
    obj.name = name
    if axis == 'X':
        obj.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
    elif axis == 'Y':
        obj.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
    return obj

def add_cone(name, r1, r2, depth, cx, cy, cz):
    """Truncated cone: r1 at bottom, r2 at top."""
    bpy.ops.mesh.primitive_cone_add(
        radius1=r1, radius2=r2, depth=depth, location=(cx, cy, cz), vertices=32)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def boolean(target, tool, op='DIFFERENCE'):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new(name="Bool", type='BOOLEAN')
    mod.operation = op
    mod.object = tool
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool, do_unlink=True)

def bevel_corners(obj, segments=4, width=CORNER_R):
    """Bevel only the vertical edges of a box (rounds the four corners)."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(obj.data)
    for edge in bm.edges:
        v0, v1 = edge.verts
        if abs(v0.co.x - v1.co.x) < 1e-3 and abs(v0.co.y - v1.co.y) < 1e-3:
            edge.select = True
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.bevel(offset=width, segments=segments, profile=0.5, affect='EDGES')
    bpy.ops.object.mode_set(mode='OBJECT')

# Corner positions (block centres) — bosses sit 8 mm in from each side
CORNER_CX = [WALL + CORNER_BLOCK/2, W - WALL - CORNER_BLOCK/2]
CORNER_CY = [WALL + CORNER_BLOCK/2, D - WALL - CORNER_BLOCK/2]
def corner_positions():
    for x in CORNER_CX:
        for y in CORNER_CY:
            yield x, y

def spk_boss_positions():
    for i in range(4):
        angle = 2 * math.pi * i / 4 + math.pi/4
        yield (SPK_CX + SPK_MOUNT_R * math.cos(angle),
               SPK_CY + SPK_MOUNT_R * math.sin(angle))

# ---------------------------------------------------------------------
# BODY
# ---------------------------------------------------------------------
def build_body():
    outer = add_cube("outer", W, D, H, W/2, D/2, H/2)
    bevel_corners(outer)

    # Main cavity from z=BOT_TH up to top panel inside face.
    cavity_h = H - BOT_TH - TOP_TH
    main_cavity = add_cube(
        "main_cavity",
        W - 2*WALL, D - 2*WALL, cavity_h,
        W/2, D/2, BOT_TH + cavity_h/2,
    )
    boolean(outer, main_cavity)

    # Bottom opening leaves a lip PANEL_INSET wide for the tray to rest on.
    bot_open_h = BOT_TH + 0.1
    bot_open = add_cube(
        "bot_open",
        W - 2*WALL - 2*PANEL_INSET, D - 2*WALL - 2*PANEL_INSET, bot_open_h,
        W/2, D/2, bot_open_h/2,
    )
    boolean(outer, bot_open)

    # Reinforcement ring around the button hole (extra thickness downward).
    #
    # ORDER MATTERS: the ring is added BEFORE the hole and notches are cut.
    # Unioning it afterwards silently filled the notches back in — they sit at
    # r=44..48, the ring is solid out to r=50, and it spans the notches' whole
    # depth, so the union restored exactly the material the notches removed.
    # The build still reported them because check_clearances() only validates
    # the constants, and the STL still had the arc verts from the hole rim.
    ring = add_cyl("btn_reinf", BTN_REINF_R, BTN_REINF_TH,
                   BTN_CX, BTN_CY, H - BTN_REINF_TH/2)
    boolean(outer, ring, op='UNION')

    # Button hole, cut through the top panel and the ring together.
    cut_depth = TOP_TH + BTN_REINF_TH + 4.0
    cut_cz    = H - cut_depth/2 + 0.05
    btn_hole = add_cyl("btn_hole", BTN_HOLE_D/2, cut_depth,
                       BTN_CX, BTN_CY, cut_cz)
    boolean(outer, btn_hole)

    # Anti-rotation notches — a semicircle on each side of the hole for the
    # button's two nubs, centred on the rim so the cut is exactly a half
    # circle of BTN_NUB_R. Full depth, so the nub's length doesn't matter.
    for sign in (-1, 1):
        nub = add_cyl(f"btn_nub_slot_{sign}", BTN_NUB_R, cut_depth,
                      BTN_CX, BTN_CY + sign * BTN_HOLE_D/2, cut_cz)
        boolean(outer, nub)

    # Four corner attachment blocks. Each block sits on top of the lip
    # and merges into the side walls; tray screws thread into a heat-set
    # insert in each block from below.
    for cx, cy in corner_positions():
        block = add_cube(
            f"corner_block_{cx:.0f}_{cy:.0f}",
            CORNER_BLOCK, CORNER_BLOCK, CORNER_BLOCK_H,
            cx, cy, BOT_TH + CORNER_BLOCK_H/2,
        )
        boolean(outer, block, op='UNION')
        # Heat-set insert pocket — bore from z=BOT_TH up through block.
        bore_h = CORNER_BLOCK_H + 0.2
        bore = add_cyl(
            f"corner_bore_{cx:.0f}_{cy:.0f}",
            INSERT_BORE_D/2, bore_h,
            cx, cy, BOT_TH + bore_h/2,
        )
        boolean(outer, bore)

    outer.name = "case_body"
    return outer

# ---------------------------------------------------------------------
# BOTTOM TRAY (removable; carries PCB, speaker, battery)
# ---------------------------------------------------------------------
def build_tray():
    # Tray plate sits in the bot_open hole at z=0..BOT_TH (flush with case
    # bottom). Inner dimensions are bot_open minus a slip-fit gap.
    tray = add_cube("tray_plate", TRAY_X, TRAY_Y, BOT_TH,
                    W/2, D/2, BOT_TH/2)

    # Plain screw clearance holes through each corner of the tray. The
    # feet print separately and the countersink lives in the foot, so the
    # tray's underside stays flat (no support material needed).
    clr_depth = BOT_TH + 2.0
    for cx, cy in corner_positions():
        clr = add_cyl(f"clr_{cx:.0f}_{cy:.0f}",
                      SCREW_CLEAR_D/2, clr_depth,
                      cx, cy, BOT_TH/2)
        boolean(tray, clr)

    # Speaker grille — concentric rings of round holes (speaker-mesh look).
    # Each hole is a separate cylindrical cut through the tray; the
    # surrounding tray material stays continuous, so no island is left
    # disconnected.
    hole_idx = 0
    for ring_r, count, hole_d in SPK_GRILLE_RINGS:
        for i in range(count):
            angle = 2 * math.pi * i / count
            gx = SPK_CX + ring_r * math.cos(angle)
            gy = SPK_CY + ring_r * math.sin(angle)
            hole = add_cyl(f"spk_hole_{hole_idx}", hole_d/2, BOT_TH * 3,
                           gx, gy, BOT_TH/2)
            boolean(tray, hole)
            hole_idx += 1

    # Speaker mounting bosses (project UP from tray top surface)
    for bx, by in spk_boss_positions():
        bz = BOT_TH + SPK_MOUNT_BOSS_H/2
        boss = add_cyl(f"spk_boss_{bx:.0f}_{by:.0f}", SPK_MOUNT_BOSS_OD/2,
                       SPK_MOUNT_BOSS_H, bx, by, bz)
        hole = add_cyl(f"spk_boss_hole_{bx:.0f}_{by:.0f}", SPK_MOUNT_BOSS_ID/2,
                       SPK_MOUNT_BOSS_H * 2, bx, by, bz)
        boolean(boss, hole)
        boolean(tray, boss, op='UNION')

    # PCB standoffs (4× M3 posts that the PCB rests on with components UP)
    for ix in (-1, 1):
        for iy in (-1, 1):
            sx = PCB_CX + ix * PCB_MOUNT_DX
            sy = PCB_CY + iy * PCB_MOUNT_DY
            sz = BOT_TH + STANDOFF_H/2
            post = add_cyl(f"pcb_post_{ix}_{iy}", STANDOFF_OD/2,
                           STANDOFF_H, sx, sy, sz)
            hole = add_cyl(f"pcb_hole_{ix}_{iy}", STANDOFF_ID/2,
                           STANDOFF_H * 2, sx, sy, sz)
            boolean(post, hole)
            boolean(tray, post, op='UNION')

    # Battery pocket — the holder lies flat, switch face down. Two long ribs
    # take the fore/aft load; short end stops at both ends stop it sliding
    # along X. The stops are split rather than solid so the leads can escape
    # at either end and so they miss the front PCB standoffs (see BAT_END_GAP).
    for sign in (-1, 1):
        rib = add_cube(
            f"bat_rib_{sign}",
            BAT_POCKET_L + 2*BAT_RIB_TH, BAT_RIB_TH, BAT_RIB_H,
            BAT_CX, BAT_CY + sign * (BAT_POCKET_W + BAT_RIB_TH)/2,
            BOT_TH + BAT_RIB_H/2,
        )
        boolean(tray, rib, op='UNION')

    tab_len = (BAT_POCKET_W + 2*BAT_RIB_TH - BAT_END_GAP) / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            stop = add_cube(
                f"bat_end_{sx}_{sy}",
                BAT_RIB_TH, tab_len, BAT_RIB_H,
                BAT_CX + sx * (BAT_POCKET_L + BAT_RIB_TH)/2,
                BAT_CY + sy * (BAT_END_GAP + tab_len)/2,
                BOT_TH + BAT_RIB_H/2,
            )
            boolean(tray, stop, op='UNION')

    # Switch window straight through the tray, under the holder's switch.
    win = add_cube(
        "bat_switch_win",
        BAT_WIN_X1 - BAT_WIN_X0, BAT_WIN_Y1 - BAT_WIN_Y0, BOT_TH * 3,
        (BAT_WIN_X0 + BAT_WIN_X1)/2, (BAT_WIN_Y0 + BAT_WIN_Y1)/2, BOT_TH/2,
    )
    boolean(tray, win)
    # Finger lead-in, cut into the underside only.
    scallop = add_cube(
        "bat_switch_scallop",
        BAT_WIN_X1 - BAT_WIN_X0 + 2*BAT_WIN_SCALLOP,
        BAT_WIN_Y1 - BAT_WIN_Y0 + 2*BAT_WIN_SCALLOP,
        BAT_WIN_SCALLOP_D * 2,
        (BAT_WIN_X0 + BAT_WIN_X1)/2, (BAT_WIN_Y0 + BAT_WIN_Y1)/2, 0.0,
    )
    boolean(tray, scallop)

    tray.name = "case_tray"
    return tray

# ---------------------------------------------------------------------
# FOOT (single puck; print 4×)
# ---------------------------------------------------------------------
def build_foot():
    """One foot puck. Printed flat-side-down with the countersink facing
    UP on the build plate, so no support is needed. At assembly, flip it
    over: countersink ends up on the floor, screw head sits flush, screw
    passes up through foot → tray → corner block heat-set insert.
    """
    # Position the foot off to the side of the body/tray so the export
    # selection picks up only the foot. Coordinates are arbitrary.
    fx, fy, fz = -50.0, 0.0, FOOT_H/2
    foot = add_cyl("foot_puck", FOOT_OD/2, FOOT_H, fx, fy, fz)

    # Clearance hole all the way through.
    clr = add_cyl("foot_clr", SCREW_CLEAR_D/2, FOOT_H + 2.0, fx, fy, fz)
    boolean(foot, clr)

    # Countersink at the BOTTOM face (so the screw head finishes flush
    # with the floor once the foot is flipped during assembly). Cone has
    # the big end at z=0 (floor) tapering up.
    csk = add_cone("foot_csk",
                   COUNTERSINK_D/2, SCREW_CLEAR_D/2,
                   COUNTERSINK_H, fx, fy, COUNTERSINK_H/2)
    boolean(foot, csk)

    foot.name = "case_foot"
    return foot

# ---------------------------------------------------------------------
def _rect(cx, cy, sx, sy):
    return (cx - sx/2, cy - sy/2, cx + sx/2, cy + sy/2)

def _hits(a, b):
    """True if two plan rects overlap (touching exactly does not count)."""
    return (a[0] < b[2] - 1e-9 and a[2] > b[0] + 1e-9
            and a[1] < b[3] - 1e-9 and a[3] > b[1] + 1e-9)

def _inside(inner, outer):
    return (inner[0] >= outer[0] - 1e-9 and inner[1] >= outer[1] - 1e-9
            and inner[2] <= outer[2] + 1e-9 and inner[3] <= outer[3] + 1e-9)


def check_clearances():
    """Assert the placements that are easy to break by nudging a constant.

    Every one of these fired at least once while the battery pocket was being
    reworked. They are cheap, and they encode *why* the numbers are what they
    are, which a bare constant cannot.
    """
    errs = []

    tray_rect = _rect(W/2, D/2, TRAY_X, TRAY_Y)
    posts = [(f"PCB standoff ({PCB_CX + ix*PCB_MOUNT_DX:.0f},"
              f" {PCB_CY + iy*PCB_MOUNT_DY:.0f})",
              _rect(PCB_CX + ix*PCB_MOUNT_DX, PCB_CY + iy*PCB_MOUNT_DY,
                    STANDOFF_OD, STANDOFF_OD))
             for ix in (-1, 1) for iy in (-1, 1)]
    blocks = [(f"corner block ({cx:.0f}, {cy:.0f})",
               _rect(cx, cy, CORNER_BLOCK, CORNER_BLOCK))
              for cx, cy in corner_positions()]

    # --- battery pocket -------------------------------------------------
    tab_len = (BAT_POCKET_W + 2*BAT_RIB_TH - BAT_END_GAP) / 2
    if tab_len <= 0:
        errs.append("BAT_END_GAP is wider than the pocket; no end stops left")

    pocket = []
    for sign in (-1, 1):
        pocket.append((f"battery rib {sign:+d}",
                       _rect(BAT_CX, BAT_CY + sign*(BAT_POCKET_W + BAT_RIB_TH)/2,
                             BAT_POCKET_L + 2*BAT_RIB_TH, BAT_RIB_TH)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            pocket.append((f"battery end stop {sx:+d}{sy:+d}",
                           _rect(BAT_CX + sx*(BAT_POCKET_L + BAT_RIB_TH)/2,
                                 BAT_CY + sy*(BAT_END_GAP + tab_len)/2,
                                 BAT_RIB_TH, tab_len)))
    holder = (BAT_X0, BAT_Y0, BAT_X1, BAT_Y1)

    # Nothing on the tray may hang over its edge: below z=BOT_TH the case
    # opening is narrower than the cavity, so an overhang fouls the lip as the
    # tray is pushed up.
    for name, r in pocket:
        if not _inside(r, tray_rect):
            errs.append(f"{name} x[{r[0]:.2f} {r[2]:.2f}] y[{r[1]:.2f} {r[3]:.2f}] "
                        f"overhangs the tray edge")

    # The ribs stand BAT_RIB_H tall and the standoffs STANDOFF_H, so any plan
    # overlap is a real collision. Same for the corner blocks, which reach down
    # to z=BOT_TH.
    for name, r in pocket + [("battery holder", holder)]:
        for other, o in posts + blocks:
            if _hits(r, o):
                errs.append(f"{name} collides with {other}")

    # The holder has to fit under the PCB, not push it up.
    if BOT_TH + BAT_RIB_H > BOT_TH + STANDOFF_H:
        errs.append(f"battery ribs (top z={BOT_TH + BAT_RIB_H:.2f}) reach above "
                    f"the PCB underside (z={BOT_TH + STANDOFF_H:.2f})")

    # ...and must not foul the button body hanging down from the top panel.
    btn_body = _rect(BTN_CX, BTN_CY, BTN_BODY_D, BTN_BODY_D)
    if _hits(holder, btn_body) and BOT_TH + BAT_HEIGHT > H - TOP_TH - BTN_BODY_LEN:
        errs.append("battery holder runs into the button body")

    # --- speaker --------------------------------------------------------
    spk = _rect(SPK_CX, SPK_CY, SPK_BODY_X, SPK_BODY_Y)
    bosses = [(f"speaker boss ({bx:.1f}, {by:.1f})",
               _rect(bx, by, SPK_MOUNT_BOSS_OD, SPK_MOUNT_BOSS_OD))
              for bx, by in spk_boss_positions()]

    if not _inside(spk, tray_rect):
        errs.append(f"speaker body x[{spk[0]:.2f} {spk[2]:.2f}] "
                    f"y[{spk[1]:.2f} {spk[3]:.2f}] overhangs the tray edge")
    for name, r in bosses:
        if not _inside(r, tray_rect):
            errs.append(f"{name} overhangs the tray edge")
        # A boss outside the speaker's own frame has nothing to bolt to.
        if not _inside(r, spk):
            errs.append(f"{name} lands off the speaker frame")
    for name, r in bosses + [("speaker body", spk)]:
        for other, o in posts + blocks + pocket:
            if _hits(r, o):
                errs.append(f"{name} collides with {other}")

    # Grille holes must not undercut a boss.
    for ring_r, count, hole_d in SPK_GRILLE_RINGS:
        for i in range(count):
            angle = 2 * math.pi * i / count
            g = _rect(SPK_CX + ring_r * math.cos(angle),
                      SPK_CY + ring_r * math.sin(angle), hole_d, hole_d)
            for name, r in bosses:
                if _hits(g, r):
                    errs.append(f"grille hole at ring r={ring_r} cuts into {name}")

    # The speaker stack has to clear the button body hanging above it.
    spk_top = BOT_TH + SPK_MOUNT_BOSS_H + SPK_BODY_H
    btn_bottom = H - TOP_TH - BTN_BODY_LEN
    if _hits(spk, btn_body) and spk_top > btn_bottom:
        errs.append(f"speaker stack (top z={spk_top:.2f}) runs into the button "
                    f"body (bottom z={btn_bottom:.2f})")

    # --- switch window --------------------------------------------------
    win = (BAT_WIN_X0, BAT_WIN_Y0, BAT_WIN_X1, BAT_WIN_Y1)
    opening = (BAT_SW_X0, BAT_SW_Y0, BAT_SW_X1, BAT_SW_Y1)
    if not _inside(opening, win):
        errs.append("tray window does not fully expose the switch opening")
    if not _inside(win, holder):
        errs.append(f"tray window x[{win[0]:.2f} {win[2]:.2f}] "
                    f"y[{win[1]:.2f} {win[3]:.2f}] runs off the holder's "
                    f"footprint x[{holder[0]:.2f} {holder[2]:.2f}] "
                    f"y[{holder[1]:.2f} {holder[3]:.2f}]")
    for name, r in pocket:
        if _hits(win, r):
            errs.append(f"tray window cuts through {name}")
    for name, r in posts:
        if _hits(win, r):
            errs.append(f"tray window cuts through {name}")

    # The lead-in scallop is wider than the window and only 1.5 mm deep, so it
    # may pass under a rib — but it must not run off the tray.
    scallop = (BAT_WIN_X0 - BAT_WIN_SCALLOP, BAT_WIN_Y0 - BAT_WIN_SCALLOP,
               BAT_WIN_X1 + BAT_WIN_SCALLOP, BAT_WIN_Y1 + BAT_WIN_SCALLOP)
    if not _inside(scallop, tray_rect):
        errs.append("switch-window scallop runs off the tray edge")

    # --- button ---------------------------------------------------------
    # The notches must stay buried in the reinforcement ring (otherwise they
    # open into thin top panel), clear the side walls, actually clear the nubs,
    # and stay hidden under the button's flange.
    notch_r = BTN_HOLE_D/2 + BTN_NUB_R
    if notch_r > BTN_REINF_R:
        errs.append(f"button nub notch (r={notch_r:.2f}) breaks out of the "
                    f"reinforcement ring (r={BTN_REINF_R:.2f})")
    if BTN_CY - notch_r < WALL or BTN_CY + notch_r > D - WALL:
        errs.append(f"button nub notch (r={notch_r:.2f} on ±Y) reaches a side wall")
    if BTN_NUB_R < BTN_NUB_D/2:
        errs.append(f"button nub notch (r={BTN_NUB_R:.2f}) is smaller than the "
                    f"nub itself (r={BTN_NUB_D/2:.2f})")
    if notch_r > BTN_FLANGE_D/2:
        errs.append(f"button nub notch (r={notch_r:.2f}) sticks out past the "
                    f"flange (r={BTN_FLANGE_D/2:.2f}) and would be visible")

    if errs:
        for e in errs:
            print("CLEARANCE FAIL:", e)
        raise SystemExit("clearance checks failed")

    print("clearance checks PASS")
    print(f"  speaker     x[{spk[0]:.2f} {spk[2]:.2f}] y[{spk[1]:.2f} {spk[3]:.2f}]"
          f"   stack top z={spk_top:.2f} vs button bottom z={btn_bottom:.2f}")
    print(f"  spk bosses  bolt circle r={SPK_MOUNT_R:.2f}"
          f"   ({SPK_MOUNT_R * math.sqrt(2):.2f} mm square pattern)")
    print(f"  holder      x[{BAT_X0:.2f} {BAT_X1:.2f}] y[{BAT_Y0:.2f} {BAT_Y1:.2f}] "
          f"z[{BOT_TH:.2f} {BOT_TH + BAT_HEIGHT:.2f}]"
          f"   PCB underside z={BOT_TH + STANDOFF_H:.2f}")
    print(f"  switch      x[{BAT_SW_X0:.2f} {BAT_SW_X1:.2f}] "
          f"y[{BAT_SW_Y0:.2f} {BAT_SW_Y1:.2f}]"
          f"   window x[{BAT_WIN_X0:.2f} {BAT_WIN_X1:.2f}] "
          f"y[{BAT_WIN_Y0:.2f} {BAT_WIN_Y1:.2f}]")
    print(f"  end stops   {tab_len:.2f} mm tabs either side of a "
          f"{BAT_END_GAP:.1f} mm lead gap")
    print(f"  nub notches r={BTN_NUB_R:.2f} on ±Y at y="
          f"{BTN_CY - BTN_HOLE_D/2:.2f} / {BTN_CY + BTN_HOLE_D/2:.2f}"
          f"   ring margin {BTN_REINF_R - notch_r:.2f} mm,"
          f" wall margin {BTN_CY - notch_r - WALL:.2f} mm,"
          f" flange cover {BTN_FLANGE_D/2 - notch_r:.2f} mm")


def verify_button_notches(body):
    """Prove the notches survived into the mesh, not just into the constants.

    check_clearances() validates numbers; it cannot see a later boolean
    undoing an earlier one. The reinforcement ring did exactly that for a
    while, and every numeric check still passed. So look for real vertices on
    the protruding half of each notch arc — material that exists only if the
    notch is genuinely open.
    """
    m = body.matrix_world
    counts = []
    for sign in (-1, 1):
        nx, ny = BTN_CX, BTN_CY + sign * BTN_HOLE_D/2
        n = 0
        for v in body.data.vertices:
            p = m @ v.co
            if p.z < H - TOP_TH - 1e-6:
                continue                       # top panel only
            if abs(math.hypot(p.x - nx, p.y - ny) - BTN_NUB_R) > 0.15:
                continue                       # on the notch arc
            if math.hypot(p.x - BTN_CX, p.y - BTN_CY) < BTN_HOLE_D/2 + 0.5:
                continue                       # protruding half, not the rim
            n += 1
        if n == 0:
            raise SystemExit(
                f"BUILD FAIL: nothing on the notch arc at ({nx:.1f}, {ny:.1f}) "
                f"— the notch was cut and then filled back in")
        counts.append(n)
    print(f"  notch arcs verified: {counts[0]} / {counts[1]} verts on the "
          f"protruding half, z >= {H - TOP_TH:.1f}")


def verify_stl_scale(path, obj):
    """Read the exported STL back and confirm it is in millimetres.

    Slicers treat STL units as mm and will happily load a 0.2 mm case without
    complaint, so a wrong global_scale is invisible until the print starts.
    Parse the binary file (80-byte header, uint32 count, 50 bytes per triangle:
    12-byte normal then three 12-byte vertices) and compare against the object.
    """
    b = path.read_bytes()
    n = struct.unpack("<I", b[80:84])[0]
    lo, hi, off = [1e30]*3, [-1e30]*3, 84
    for _ in range(n):
        for v in range(3):
            xyz = struct.unpack("<3f", b[off + 12 + v*12: off + 24 + v*12])
            for i in range(3):
                lo[i] = min(lo[i], xyz[i])
                hi[i] = max(hi[i], xyz[i])
        off += 50
    size = [hi[i] - lo[i] for i in range(3)]
    want = list(obj.dimensions)
    if any(abs(g - e) > 0.05 for g, e in zip(size, want)):
        raise SystemExit(
            f"BUILD FAIL: {path.name} exported at the wrong scale — "
            f"{size[0]:.3f} x {size[1]:.3f} x {size[2]:.3f}, expected "
            f"{want[0]:.3f} x {want[1]:.3f} x {want[2]:.3f} mm")
    print(f"  {path.name:11s} {n:6d} tris   "
          f"{size[0]:.2f} × {size[1]:.2f} × {size[2]:.2f} mm")


def main():
    check_clearances()
    clear_scene()
    body = build_body()
    verify_button_notches(body)
    tray = build_tray()
    foot = build_foot()

    out_dir = OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_dir / "case.blend"))

    for obj, fname in [(body, "body.stl"), (tray, "bottom.stl"), (foot, "foot.stl")]:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.wm.stl_export(
            filepath=str(out_dir / fname),
            export_selected_objects=True,
            # 1 model unit == 1 mm in the file. global_scale is a plain
            # multiplier (use_scene_unit defaults off), so the 0.001 that used
            # to be here wrote metres — body.stl came out 0.2 x 0.13 x 0.11,
            # which a slicer loads as a speck rather than rejecting.
            global_scale=1.0,
            forward_axis='Y',
            up_axis='Z',
            apply_modifiers=True,
        )
        verify_stl_scale(out_dir / fname, obj)

    print(f"BUILT: body {len(body.data.vertices)} verts, "
          f"tray {len(tray.data.vertices)} verts, "
          f"foot {len(foot.data.vertices)} verts")

if __name__ == "__main__":
    main()
