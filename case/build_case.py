"""Headless Blender model of the Ah! My Groin! v2 enclosure.

Run with:
    "K:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" \
        --background --python build_case.py

Outputs:
    case.blend      — the editable model
    body.stl        — main case body (top + sides, open at bottom)
    bottom.stl      — removable bottom tray (carries PCB, speaker, battery)
    foot.stl        — single foot puck; print 4× (one per corner)

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
    Button             88 mm mounting hole, 50 mm body below panel
                       (microswitch detached and dangling on wires)
    Battery (3×AA)     48.22 × 68.95 × 17.8 mm, measured 2026-07-25.
                       STANDS ON EDGE against the front wall so its switch
                       face is vertical and reachable through a window in
                       the body. Lying flat (the old arrangement) pointed
                       that face at the ceiling, where no wall window can
                       reach it.

CASE SHAPE:
    Outer 200 × 130 × 90 mm rectangular prism
    Wall thickness 3.5 mm, outer corner radius 5 mm
    Top integral with body; bottom is a separate removable tray
"""
from pathlib import Path
import math
import bpy
import bmesh

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
BTN_BODY_D     = 78.0                   # body diameter below panel
BTN_BODY_LEN   = 50.0                   # how far the body hangs below
BTN_REINF_R    = 50.0                   # reinforcement ring outer radius
BTN_REINF_TH   = 6.0                    # reinforced zone thickness
# Anti-rotation nubs on the button body: two half-circle bumps directly
# opposite each other across the button's diameter. Each is 5.73 mm wide
# (chord, against the button surface) and protrudes 2.7 mm radially.
# Cut matching slots into the mounting hole so the button can't spin and
# tangle the wires below.
BTN_NUB_W      = 5.73                   # chord width of nub at button surface
BTN_NUB_PROT   = 2.7                    # how far nub sticks out radially

# PCB — right half, on standoffs from the tray.
# PCB_CY moved 65 → 74 when the battery stood up: the battery pocket's back
# wall lands at y=32.3, and at PCB_CY=65 the PCB's front edge was at y=30, so
# the pocket walls (40 mm tall) ran straight through the board. At 74 the
# board starts at y=39 with 6.7 mm to spare. Still clear of the speaker
# (x ≤ 93.9 vs PCB x ≥ 100) and the rear corner blocks (y ≥ 114.5).
PCB_CX, PCB_CY = 145.0, 74.0
PCB_W, PCB_D, PCB_T = 90.0, 70.0, 2.0
PCB_MOUNT_DX   = 40.0                   # ±40 mm from PCB centre (80 mm apart in X)
PCB_MOUNT_DY   = 30.0                   # ±30 mm from PCB centre (60 mm apart in Y)
STANDOFF_OD    = 6.0
STANDOFF_ID    = 2.7                    # M3 self-tapping (or use M3 heat-set)
STANDOFF_H     = 25.0                   # PCB sits this far above the tray inner face

# Speaker — fires DOWN through tray grille, under the button area
SPK_CX, SPK_CY = 55.0, 65.0
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
SPK_MOUNT_BOSS_ID = 2.7
SPK_MOUNT_BOSS_H  = 6.0

# ---------------------------------------------------------------------
# Battery holder — 3×AA, stands ON EDGE in the front-right corner
# ---------------------------------------------------------------------
# Measured on the physical holder 2026-07-25. BAT_W/BAT_H are the two sides
# of the face the switch is on; BAT_D is the thickness.
BAT_W, BAT_H, BAT_D = 48.22, 68.95, 17.8
BAT_FIT        = 0.6                    # printed-pocket clearance per axis
BAT_CX         = 145.0                  # same X centre as the PCB above it
BAT_WALL_TH    = 2.5                    # pocket wall / rib thickness
BAT_WALL_H     = 40.0                   # side + back wall height (box is 68.95)
BAT_FRONT_RIB_H = 10.0                  # front stop; deliberately short
BAT_WIRE_GAP   = 14.0                   # gap in the back wall for the leads

# Derived pocket geometry. The pocket starts one wall thickness behind the
# tray's front edge, because the front rib has to sit ON the tray.
BAT_POCKET_W = BAT_W + BAT_FIT
BAT_POCKET_D = BAT_D + BAT_FIT
BAT_FRONT_Y  = TRAY_MIN_Y + BAT_WALL_TH         # 11.4 — holder's front face
BAT_BACK_Y   = BAT_FRONT_Y + BAT_POCKET_D       # 29.8 — holder's back face

# Switch opening, measured from the holder's own top-right corner as it is
# seen from the front of the case (+X is to the viewer's right):
#   horizontal   6.43 mm (right edge of opening) .. 17.2 mm (left edge)
#   vertical     2.30 mm (top edge)              .. 12.0 mm (bottom edge)
# → a 10.77 × 9.70 mm opening. Only the centre is needed here.
BAT_SW_FROM_RIGHT = (6.43, 17.2)
BAT_SW_FROM_TOP   = (2.3, 12.0)
BAT_SW_CX = (BAT_CX + BAT_W/2) - sum(BAT_SW_FROM_RIGHT)/2   # 157.295
BAT_SW_CZ = (BOT_TH + BAT_H)  - sum(BAT_SW_FROM_TOP)/2      # 65.300

# The body window is much larger than the 10.77 × 9.70 switch opening on
# purpose. The holder's switch face sits at y=11.4 while the outer wall face
# is at y=0, so the switch is recessed 11.4 mm — the hole has to admit a
# fingertip, not merely clear the lever. A shallow scallop around the outside
# gives the finger a lead-in.
BAT_WIN_W, BAT_WIN_H = 20.0, 14.0
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

    # Button hole through the top.
    btn_hole = add_cyl("btn_hole", BTN_HOLE_D/2, TOP_TH * 4,
                       BTN_CX, BTN_CY, H - TOP_TH/2)
    boolean(outer, btn_hole)

    # Anti-rotation slots — two half-circle cutouts on opposite sides of
    # the button hole (along ±X) that the button's plastic nubs slot into.
    # Offset the cutter circle so its near edge sits flush with the hole
    # edge and its far edge protrudes BTN_NUB_PROT outward.
    nub_r      = BTN_NUB_W / 2
    nub_offset = BTN_HOLE_D/2 + BTN_NUB_PROT - nub_r
    # Cut deep enough to clear top panel + reinforcement ring (with margin).
    nub_depth  = TOP_TH + BTN_REINF_TH + 4.0
    nub_cz     = H - nub_depth/2 + 0.05
    for sign in (-1, 1):
        nub = add_cyl(f"btn_nub_slot_{sign}", nub_r, nub_depth,
                      BTN_CX + sign * nub_offset, BTN_CY, nub_cz)
        boolean(outer, nub)

    # Reinforcement ring around the button hole (extra thickness downward).
    ring = add_cyl("btn_reinf", BTN_REINF_R, BTN_REINF_TH,
                   BTN_CX, BTN_CY, H - BTN_REINF_TH/2)
    ring_hole = add_cyl("ring_hole", BTN_HOLE_D/2, BTN_REINF_TH * 2,
                        BTN_CX, BTN_CY, H - BTN_REINF_TH/2)
    boolean(ring, ring_hole)
    boolean(outer, ring, op='UNION')

    # Battery switch window through the FRONT wall (y=0 face). The holder
    # stands on edge behind it with its switch face toward -Y. Sized for a
    # fingertip rather than for the lever — see BAT_WIN_W notes above.
    win = add_cube(
        "bat_switch_win",
        BAT_WIN_W, WALL * 4, BAT_WIN_H,
        BAT_SW_CX, WALL/2, BAT_SW_CZ,
    )
    boolean(outer, win)
    # Shallow finger lead-in on the outside face only.
    scallop = add_cube(
        "bat_switch_scallop",
        BAT_WIN_W + 2*BAT_WIN_SCALLOP,
        BAT_WIN_SCALLOP_D * 2,
        BAT_WIN_H + 2*BAT_WIN_SCALLOP,
        BAT_SW_CX, 0.0, BAT_SW_CZ,
    )
    boolean(outer, scallop)

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
    for i in range(4):
        angle = 2 * math.pi * i / 4 + math.pi/4
        bx = SPK_CX + SPK_MOUNT_R * math.cos(angle)
        by = SPK_CY + SPK_MOUNT_R * math.sin(angle)
        bz = BOT_TH + SPK_MOUNT_BOSS_H/2
        boss = add_cyl(f"spk_boss_{i}", SPK_MOUNT_BOSS_OD/2,
                       SPK_MOUNT_BOSS_H, bx, by, bz)
        hole = add_cyl(f"spk_boss_hole_{i}", SPK_MOUNT_BOSS_ID/2,
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

    # Battery pocket — the holder stands on edge, switch face toward -Y.
    # Two full-depth side walls, a low front rib and a split back wall.
    px0 = BAT_CX - BAT_POCKET_W/2
    px1 = BAT_CX + BAT_POCKET_W/2
    mid_y = (BAT_FRONT_Y + BAT_BACK_Y) / 2

    for label, wx in (("bat_wall_left",  px0 - BAT_WALL_TH/2),
                      ("bat_wall_right", px1 + BAT_WALL_TH/2)):
        wall = add_cube(
            label,
            BAT_WALL_TH, BAT_POCKET_D + 2*BAT_WALL_TH, BAT_WALL_H,
            wx, mid_y, BOT_TH + BAT_WALL_H/2,
        )
        boolean(tray, wall, op='UNION')

    # Front rib. Kept to BAT_FRONT_RIB_H so it stops the holder sliding
    # forward off the tray without rising anywhere near the switch, which is
    # 65.3 mm up. Without it the holder could creep forward onto the case lip
    # and then foul the tray when the tray is pulled back out.
    front_rib = add_cube(
        "bat_front_rib",
        BAT_POCKET_W + 2*BAT_WALL_TH, BAT_WALL_TH, BAT_FRONT_RIB_H,
        BAT_CX, BAT_FRONT_Y - BAT_WALL_TH/2, BOT_TH + BAT_FRONT_RIB_H/2,
    )
    boolean(tray, front_rib, op='UNION')

    # Back wall, split around a central gap the battery leads pass through
    # on their way to the JST connector at the back of the PCB.
    back_seg = (BAT_POCKET_W + 2*BAT_WALL_TH - BAT_WIRE_GAP) / 2
    for sign in (-1, 1):
        seg = add_cube(
            f"bat_back_wall_{sign}",
            back_seg, BAT_WALL_TH, BAT_WALL_H,
            BAT_CX + sign * (BAT_WIRE_GAP + back_seg) / 2,
            BAT_BACK_Y + BAT_WALL_TH/2,
            BOT_TH + BAT_WALL_H/2,
        )
        boolean(tray, seg, op='UNION')

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
def check_clearances():
    """Assert the placements that are easy to break by nudging a constant.

    Every one of these fired at least once while the battery was being stood
    up. They are cheap and they encode *why* the numbers are what they are,
    which a bare constant cannot.
    """
    errs = []

    # The pocket must sit entirely on the tray.
    if BAT_FRONT_Y - BAT_WALL_TH < TRAY_MIN_Y - 1e-9:
        errs.append("battery front rib overhangs the tray front edge "
                    f"({BAT_FRONT_Y - BAT_WALL_TH:.2f} < {TRAY_MIN_Y:.2f}); "
                    "it would foul the case lip during assembly")

    # The pocket must stay clear of the PCB and its standoffs.
    pcb_front = PCB_CY - PCB_D/2
    pocket_back = BAT_BACK_Y + BAT_WALL_TH
    if pocket_back > pcb_front:
        errs.append(f"battery pocket back wall (y={pocket_back:.2f}) runs into "
                    f"the PCB front edge (y={pcb_front:.2f})")

    # Pocket must clear the four PCB standoffs in X, or in Y if it overlaps.
    pocket_x0 = BAT_CX - BAT_POCKET_W/2 - BAT_WALL_TH
    pocket_x1 = BAT_CX + BAT_POCKET_W/2 + BAT_WALL_TH
    for ix in (-1, 1):
        for iy in (-1, 1):
            sx = PCB_CX + ix * PCB_MOUNT_DX
            sy = PCB_CY + iy * PCB_MOUNT_DY
            x_hit = pocket_x0 < sx + STANDOFF_OD/2 and pocket_x1 > sx - STANDOFF_OD/2
            y_hit = (BAT_FRONT_Y - BAT_WALL_TH < sy + STANDOFF_OD/2
                     and pocket_back > sy - STANDOFF_OD/2)
            if x_hit and y_hit:
                errs.append(f"battery pocket collides with PCB standoff "
                            f"at ({sx:.1f}, {sy:.1f})")

    # Pocket must clear the front corner blocks.
    for cx in CORNER_CX:
        bx0, bx1 = cx - CORNER_BLOCK/2, cx + CORNER_BLOCK/2
        if pocket_x0 < bx1 and pocket_x1 > bx0:
            errs.append(f"battery pocket overlaps the corner block at x={cx:.1f}")

    # The switch window must land on the holder's switch face, not past it.
    sw_x0, sw_x1 = BAT_SW_CX - BAT_WIN_W/2, BAT_SW_CX + BAT_WIN_W/2
    sw_z0, sw_z1 = BAT_SW_CZ - BAT_WIN_H/2, BAT_SW_CZ + BAT_WIN_H/2
    box_x0, box_x1 = BAT_CX - BAT_W/2, BAT_CX + BAT_W/2
    box_z0, box_z1 = BOT_TH, BOT_TH + BAT_H
    if sw_x0 < box_x0 or sw_x1 > box_x1 or sw_z0 < box_z0 or sw_z1 > box_z1:
        errs.append("switch window runs off the edge of the holder's face: "
                    f"window x[{sw_x0:.2f} {sw_x1:.2f}] z[{sw_z0:.2f} {sw_z1:.2f}] "
                    f"vs holder x[{box_x0:.2f} {box_x1:.2f}] z[{box_z0:.2f} {box_z1:.2f}]")

    # ...and must fully expose the 10.77 × 9.70 opening itself.
    op_x0 = box_x1 - max(BAT_SW_FROM_RIGHT)
    op_x1 = box_x1 - min(BAT_SW_FROM_RIGHT)
    op_z0 = box_z1 - max(BAT_SW_FROM_TOP)
    op_z1 = box_z1 - min(BAT_SW_FROM_TOP)
    if op_x0 < sw_x0 or op_x1 > sw_x1 or op_z0 < sw_z0 or op_z1 > sw_z1:
        errs.append("switch window does not fully expose the switch opening")

    # The holder must not foul the button body hanging down from the top.
    btn_x0, btn_x1 = BTN_CX - BTN_BODY_D/2, BTN_CX + BTN_BODY_D/2
    if pocket_x0 < btn_x1 and pocket_x1 > btn_x0 \
            and BOT_TH + BAT_H > H - TOP_TH - BTN_BODY_LEN:
        errs.append("battery holder runs into the button body")

    if errs:
        for e in errs:
            print("CLEARANCE FAIL:", e)
        raise SystemExit("clearance checks failed")

    print("clearance checks PASS")
    print(f"  holder      x[{box_x0:.2f} {box_x1:.2f}] "
          f"y[{BAT_FRONT_Y:.2f} {BAT_BACK_Y:.2f}] z[{box_z0:.2f} {box_z1:.2f}]")
    print(f"  switch win  x[{sw_x0:.2f} {sw_x1:.2f}] z[{sw_z0:.2f} {sw_z1:.2f}]"
          f"   centre ({BAT_SW_CX:.3f}, {BAT_SW_CZ:.3f})")
    print(f"  switch recessed {BAT_FRONT_Y:.2f} mm behind the outer wall face")
    print(f"  PCB         y[{pcb_front:.2f} {PCB_CY + PCB_D/2:.2f}]")


def main():
    check_clearances()
    clear_scene()
    body = build_body()
    tray = build_tray()
    foot = build_foot()

    out_dir = Path(r"I:\code\ah-my-groin-button\case")
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out_dir / "case.blend"))

    for obj, fname in [(body, "body.stl"), (tray, "bottom.stl"), (foot, "foot.stl")]:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.wm.stl_export(
            filepath=str(out_dir / fname),
            export_selected_objects=True,
            global_scale=0.001,
            forward_axis='Y',
            up_axis='Z',
            apply_modifiers=True,
        )
        print(f"exported {fname}")

    print(f"BUILT: body {len(body.data.vertices)} verts, "
          f"tray {len(tray.data.vertices)} verts, "
          f"foot {len(foot.data.vertices)} verts")

if __name__ == "__main__":
    main()
