"""Headless Blender model of the Ah! My Groin! v2 enclosure — tall and narrow.

Run with:
    "K:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" \
        --background --python build_v2.py

v1 (case/v1-200x130x110) laid everything out side by side on one tray, which
made it wide. This one stacks: speaker on the bottom firing down through the
grille, PCB and battery in a middle layer, button on top. 120 x 120 x 140.

WHY THE PCB IS NOT ON TRAY STANDOFFS
    Its mount holes span 80 mm and the speaker is 77.8 mm wide, so 6 mm posts
    need 86 mm to straddle it. Short by 3.8 mm — and that is independent of
    box size, so no amount of widening fixes it. Instead four posts rise from
    the tray OUTSIDE the speaker's footprint (in the y < 21.1 and y > 98.9
    bands) and reach inward with short arms above the speaker's top face.

ASSEMBLY
    Speaker onto the tray bosses. PCB onto the four mid-layer bosses. Battery
    holder stands on edge in the cradle against the -X wall, switch facing out
    through the window in that wall. Connect the three JST cables, lift the
    tray up into the body, stack a foot under each corner, four M3 x 25.

GEOMETRY (all measured on the physical parts unless noted)
    PCB                90 x 70 x 2.0 mm + ~20 mm component height,
                       mounted rotated 90 deg vs v1 so it fits beside the
                       battery: 70 mm across X, 90 mm across Y
    Speaker (ADA1313)  77.8 x 77.8 x 25.5 mm, 58.9 mm square bolt pattern
    Button             99 mm flange, 88 mm mounting hole, 42.07 mm of barrel
                       below the flange, plus 24.62 mm of microswitch BOLTED
                       ON (v1 left it dangling; this one keeps it captive)
    Battery (3xAA)     48.22 x 68.95 x 17.8 mm, standing on edge

CHILD-SAFE ROUNDING
    Vertical corners 12 mm, top rim 6 mm, bottom rim 2 mm. The top rim is
    what limits the button: at 6 mm the flat top is 108 mm across, leaving
    the 99 mm flange 4.5 mm of seating. Going bigger starts to undercut it.
"""
from pathlib import Path
import math
import struct
import bpy
import bmesh

# ---------------------------------------------------------------------
HERE    = Path(__file__).parent
VERSION = "v2-120x120x140"
OUT_DIR = HERE / VERSION

# ---------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------
W, D, H        = 120.0, 120.0, 140.0
WALL           = 3.5
TOP_TH         = 3.5
BOT_TH         = 3.5
PANEL_INSET    = 5.0
TRAY_FIT_GAP   = 0.4

CORNER_R       = 12.0                   # vertical edges — generous, kid-safe
TOP_R          = 6.0                    # top rim
BOT_R          = 2.0                    # bottom rim; kept small so the feet
                                        # still land on flat material

TRAY_X    = W - 2*WALL - 2*PANEL_INSET - 2*TRAY_FIT_GAP     # 102.2
TRAY_Y    = D - 2*WALL - 2*PANEL_INSET - 2*TRAY_FIT_GAP
TRAY_MIN  = W/2 - TRAY_X/2              # 8.9 — tray edge, and the limit on
                                        # anything mounted to the tray

CORNER_BLOCK   = 12.0
CORNER_BLOCK_H = 12.0
INSERT_BORE_D  = 4.2
SCREW_CLEAR_D  = 3.4
COUNTERSINK_D  = 6.5
COUNTERSINK_H  = 1.8
FOOT_OD        = 14.0
FOOT_H         = 8.0

# ---------------------------------------------------------------------
# Button — top centre
# ---------------------------------------------------------------------
BTN_CX, BTN_CY = W/2, D/2
BTN_HOLE_D     = 88.0
BTN_FLANGE_D   = 99.0                   # measured; bounds the notches
BTN_BODY_D     = 78.0
BTN_BODY_LEN   = 42.07                  # measured, flange underside to the
                                        # end of the barrel
BTN_SWITCH_LEN = 24.62                  # measured, microswitch below that
# ASSUMED, NOT MEASURED: the microswitch's width. 40 mm is a deliberate
# over-estimate of a part that is realistically ~27 mm. It only has to clear
# the PCB below it, and at H=140 there is 5.8 mm to spare, so a smaller real
# value only adds margin. Worth a caliper check before printing.
BTN_SWITCH_D   = 40.0
BTN_REINF_R    = 50.0
BTN_REINF_TH   = 6.0
BTN_NUB_D      = 5.88
BTN_NUB_R      = 4.0

# ---------------------------------------------------------------------
# Speaker — bottom, on the tray, firing down
# ---------------------------------------------------------------------
SPK_CX, SPK_CY = W/2, D/2
SPK_BODY_X, SPK_BODY_Y, SPK_BODY_H = 77.8, 77.8, 25.5
SPK_MOUNT_R    = 41.65                  # 58.9 mm square pattern
SPK_MOUNT_BOSS_OD = 6.0
SPK_MOUNT_BOSS_ID = 2.7
SPK_MOUNT_BOSS_H  = 6.0
SPK_TOP = BOT_TH + SPK_MOUNT_BOSS_H + SPK_BODY_H        # 35.0

SPK_GRILLE_RINGS = [
    (0,    1,  6.0),
    (10,   6,  5.5),
    (20,  12,  5.5),
    (30,  18,  5.0),
]

# ---------------------------------------------------------------------
# Mid layer — PCB and battery share one level above the speaker
# ---------------------------------------------------------------------
MID_Z      = 42.0                       # PCB underside / battery cradle floor
ARM_Z      = SPK_TOP + 2.0              # 37.0 — arms and bosses start here,
                                        # clear of the speaker's top face

PCB_CX, PCB_CY = 67.0, D/2
PCB_W, PCB_D, PCB_T = 70.0, 90.0, 2.0   # rotated 90 deg vs v1
PCB_MOUNT_DX = 30.0
PCB_MOUNT_DY = 40.0
PCB_COMP_H   = 20.0
STANDOFF_OD  = 6.0
STANDOFF_ID  = 2.7
POST_DY      = 45.0                     # posts sit this far out in Y from the
                                        # PCB centre, which puts them clear of
                                        # the speaker; the arm covers the rest
POST_X, POST_Y = 6.0, 12.0              # post cross-section


def pcb_mounts():
    for ix in (-1, 1):
        for iy in (-1, 1):
            yield PCB_CX + ix*PCB_MOUNT_DX, PCB_CY + iy*PCB_MOUNT_DY


def pcb_posts():
    for ix in (-1, 1):
        for iy in (-1, 1):
            yield PCB_CX + ix*PCB_MOUNT_DX, PCB_CY + iy*POST_DY


# ---------------------------------------------------------------------
# Battery — 3xAA on edge against the -X wall, switch facing out
# ---------------------------------------------------------------------
BAT_TH, BAT_LEN, BAT_TALL = 17.8, 68.95, 48.22      # X, Y, Z as it stands
BAT_FIT       = 0.6
BAT_WALL_TH   = 2.5
BAT_X0        = 11.5                    # switch face; 11.5 mm behind the
                                        # outer wall, same recess as v1
BAT_X1        = BAT_X0 + BAT_TH
BAT_CY        = D/2
BAT_Y0        = BAT_CY - BAT_LEN/2
BAT_Y1        = BAT_CY + BAT_LEN/2
BAT_Z0        = MID_Z
BAT_Z1        = BAT_Z0 + BAT_TALL
BAT_FLOOR_TH  = 3.0                     # cradle floor, MID_Z-3 .. MID_Z
BAT_RET_H     = 15.0                    # retaining walls above the floor

# Switch opening, from the face's own top-right corner. Standing on edge with
# the face pointing -X, "top" is +Z and "right" is -Y. The cradle is a plain
# channel, so the holder also drops in rotated 180 deg with the switch in the
# far corner — the guide says to spin it if the window shows blank plastic.
BAT_SW_FROM_RIGHT = (6.43, 17.2)
BAT_SW_FROM_TOP   = (2.3, 12.0)
BAT_SW_Y0 = BAT_Y0 + min(BAT_SW_FROM_RIGHT)
BAT_SW_Y1 = BAT_Y0 + max(BAT_SW_FROM_RIGHT)
BAT_SW_Z0 = BAT_Z1 - max(BAT_SW_FROM_TOP)
BAT_SW_Z1 = BAT_Z1 - min(BAT_SW_FROM_TOP)

# The window is generous because the switch is recessed 11.5 mm — it has to
# admit a fingertip, not merely clear the lever. It is allowed to overrun the
# top of the holder; unlike v1's tray window there is nothing above it.
BAT_WIN_MARGIN    = 4.0
BAT_WIN_Y0 = BAT_SW_Y0 - BAT_WIN_MARGIN
BAT_WIN_Y1 = BAT_SW_Y1 + BAT_WIN_MARGIN
BAT_WIN_Z0 = BAT_SW_Z0 - BAT_WIN_MARGIN
BAT_WIN_Z1 = BAT_SW_Z1 + BAT_WIN_MARGIN
BAT_WIN_SCALLOP   = 3.0
BAT_WIN_SCALLOP_D = 1.5

CORNER_CX = [WALL + CORNER_BLOCK/2, W - WALL - CORNER_BLOCK/2]
CORNER_CY = [WALL + CORNER_BLOCK/2, D - WALL - CORNER_BLOCK/2]


def corner_positions():
    for x in CORNER_CX:
        for y in CORNER_CY:
            yield x, y


def spk_boss_positions():
    for i in range(4):
        a = 2*math.pi*i/4 + math.pi/4
        yield SPK_CX + SPK_MOUNT_R*math.cos(a), SPK_CY + SPK_MOUNT_R*math.sin(a)


# ---------------------------------------------------------------------
# Mesh helpers
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


def add_box(name, x0, y0, z0, x1, y1, z1):
    """Same as add_cube but from opposite corners, which is how most of the
    geometry below is actually specified."""
    return add_cube(name, x1-x0, y1-y0, z1-z0,
                    (x0+x1)/2, (y0+y1)/2, (z0+z1)/2)


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


def bevel_edges(obj, width, segments, predicate):
    """Bevel just the edges the predicate picks out.

    Run in passes rather than one angle-limited modifier, because the vertical
    corners and the horizontal rims want different radii.
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(obj.data)
    n = 0
    for e in bm.edges:
        a, b = e.verts
        if predicate(a.co, b.co):
            e.select = True
            n += 1
    bmesh.update_edit_mesh(obj.data)
    if n:
        bpy.ops.mesh.bevel(offset=width, segments=segments, profile=0.5,
                           affect='EDGES')
    bpy.ops.object.mode_set(mode='OBJECT')
    return n


def _vertical(a, b):
    return abs(a.x - b.x) < 1e-3 and abs(a.y - b.y) < 1e-3


def _rim_at(z):
    def pred(a, b):
        return (abs(a.z - b.z) < 1e-3 and abs(a.z - z) < 1e-3)
    return pred


def round_shell(obj):
    """Vertical corners, then the top rim, then the bottom rim."""
    bevel_edges(obj, CORNER_R, 8, _vertical)
    bevel_edges(obj, TOP_R, 6, _rim_at(H))
    bevel_edges(obj, BOT_R, 3, _rim_at(0.0))


# ---------------------------------------------------------------------
# BODY
# ---------------------------------------------------------------------
def build_body():
    outer = add_cube("outer", W, D, H, W/2, D/2, H/2)
    round_shell(outer)

    cavity_h = H - BOT_TH - TOP_TH
    boolean(outer, add_cube("main_cavity", W - 2*WALL, D - 2*WALL, cavity_h,
                            W/2, D/2, BOT_TH + cavity_h/2))

    bot_open_h = BOT_TH + 0.1
    boolean(outer, add_cube("bot_open",
                            W - 2*WALL - 2*PANEL_INSET,
                            D - 2*WALL - 2*PANEL_INSET, bot_open_h,
                            W/2, D/2, bot_open_h/2))

    # Reinforcement ring FIRST, then cut the hole and notches through it.
    # Unioning it afterwards fills the notches straight back in — that bug
    # shipped in v1 and survived every numeric check.
    boolean(outer, add_cyl("btn_reinf", BTN_REINF_R, BTN_REINF_TH,
                           BTN_CX, BTN_CY, H - BTN_REINF_TH/2), op='UNION')

    cut_depth = TOP_TH + BTN_REINF_TH + 4.0
    cut_cz    = H - cut_depth/2 + 0.05
    boolean(outer, add_cyl("btn_hole", BTN_HOLE_D/2, cut_depth,
                           BTN_CX, BTN_CY, cut_cz))
    for sign in (-1, 1):
        boolean(outer, add_cyl(f"btn_nub_slot_{sign}", BTN_NUB_R, cut_depth,
                               BTN_CX, BTN_CY + sign*BTN_HOLE_D/2, cut_cz))

    # Battery switch window through the -X wall, with a finger scallop on the
    # outside face only.
    boolean(outer, add_cube("bat_switch_win",
                            WALL*4, BAT_WIN_Y1 - BAT_WIN_Y0,
                            BAT_WIN_Z1 - BAT_WIN_Z0,
                            WALL/2, (BAT_WIN_Y0 + BAT_WIN_Y1)/2,
                            (BAT_WIN_Z0 + BAT_WIN_Z1)/2))
    boolean(outer, add_cube("bat_switch_scallop",
                            BAT_WIN_SCALLOP_D*2,
                            BAT_WIN_Y1 - BAT_WIN_Y0 + 2*BAT_WIN_SCALLOP,
                            BAT_WIN_Z1 - BAT_WIN_Z0 + 2*BAT_WIN_SCALLOP,
                            0.0, (BAT_WIN_Y0 + BAT_WIN_Y1)/2,
                            (BAT_WIN_Z0 + BAT_WIN_Z1)/2))

    for cx, cy in corner_positions():
        boolean(outer, add_cube(f"corner_block_{cx:.0f}_{cy:.0f}",
                                CORNER_BLOCK, CORNER_BLOCK, CORNER_BLOCK_H,
                                cx, cy, BOT_TH + CORNER_BLOCK_H/2), op='UNION')
        bore_h = CORNER_BLOCK_H + 0.2
        boolean(outer, add_cyl(f"corner_bore_{cx:.0f}_{cy:.0f}",
                               INSERT_BORE_D/2, bore_h, cx, cy,
                               BOT_TH + bore_h/2))

    outer.name = "case_body"
    return outer


# ---------------------------------------------------------------------
# TRAY — speaker, PCB posts, battery cradle
# ---------------------------------------------------------------------
def build_tray():
    tray = add_cube("tray_plate", TRAY_X, TRAY_Y, BOT_TH, W/2, D/2, BOT_TH/2)

    for cx, cy in corner_positions():
        boolean(tray, add_cyl(f"clr_{cx:.0f}_{cy:.0f}", SCREW_CLEAR_D/2,
                              BOT_TH + 2.0, cx, cy, BOT_TH/2))

    # Speaker grille
    i = 0
    for ring_r, count, hole_d in SPK_GRILLE_RINGS:
        for k in range(count):
            a = 2*math.pi*k/count
            boolean(tray, add_cyl(f"spk_hole_{i}", hole_d/2, BOT_TH*3,
                                  SPK_CX + ring_r*math.cos(a),
                                  SPK_CY + ring_r*math.sin(a), BOT_TH/2))
            i += 1

    # Speaker mounting bosses
    for bx, by in spk_boss_positions():
        bz = BOT_TH + SPK_MOUNT_BOSS_H/2
        boss = add_cyl(f"spk_boss_{bx:.0f}_{by:.0f}", SPK_MOUNT_BOSS_OD/2,
                       SPK_MOUNT_BOSS_H, bx, by, bz)
        boolean(boss, add_cyl(f"spk_bh_{bx:.0f}_{by:.0f}", SPK_MOUNT_BOSS_ID/2,
                              SPK_MOUNT_BOSS_H*2, bx, by, bz))
        boolean(tray, boss, op='UNION')

    # PCB support. Post rises in the clear band beside the speaker; a stub
    # bridges inward at ARM_Z, above the speaker's top face; the boss sits on
    # the end of it. Splitting it this way is what lets an 80 mm mount span
    # live over a 77.8 mm speaker.
    for (mx, my), (px, py) in zip(pcb_mounts(), pcb_posts()):
        boolean(tray, add_cube(f"pcb_post_{mx:.0f}_{py:.0f}",
                               POST_X, POST_Y, MID_Z - BOT_TH,
                               px, py, BOT_TH + (MID_Z - BOT_TH)/2), op='UNION')
        a0 = min(py - POST_Y/2, my - STANDOFF_OD/2)
        a1 = max(py + POST_Y/2, my + STANDOFF_OD/2)
        boolean(tray, add_box(f"pcb_arm_{mx:.0f}_{my:.0f}",
                              px - POST_X/2, a0, ARM_Z,
                              px + POST_X/2, a1, MID_Z), op='UNION')
        boss = add_cyl(f"pcb_boss_{mx:.0f}_{my:.0f}", STANDOFF_OD/2,
                       MID_Z - ARM_Z, mx, my, (ARM_Z + MID_Z)/2)
        boolean(boss, add_cyl(f"pcb_bh_{mx:.0f}_{my:.0f}", STANDOFF_ID/2,
                              (MID_Z - ARM_Z)*2 + 2, mx, my, (ARM_Z + MID_Z)/2))
        boolean(tray, boss, op='UNION')

    # Battery cradle. One full-height wall outboard (it clears the speaker in
    # X), a floor cantilevered off it at MID_Z, and low retaining walls above.
    boolean(tray, add_box("bat_support",
                          BAT_X0 - BAT_WALL_TH, BAT_Y0 - BAT_WALL_TH, BOT_TH,
                          BAT_X0, BAT_Y1 + BAT_WALL_TH, MID_Z), op='UNION')
    boolean(tray, add_box("bat_floor",
                          BAT_X0 - BAT_WALL_TH, BAT_Y0 - BAT_WALL_TH,
                          MID_Z - BAT_FLOOR_TH,
                          BAT_X1 + BAT_WALL_TH, BAT_Y1 + BAT_WALL_TH, MID_Z),
            op='UNION')
    # Inboard wall and two end stops, all above the speaker.
    boolean(tray, add_box("bat_wall_in",
                          BAT_X1 + BAT_FIT/2, BAT_Y0 - BAT_WALL_TH, MID_Z,
                          BAT_X1 + BAT_FIT/2 + BAT_WALL_TH,
                          BAT_Y1 + BAT_WALL_TH, MID_Z + BAT_RET_H), op='UNION')
    boolean(tray, add_box("bat_wall_out",
                          BAT_X0 - BAT_WALL_TH, BAT_Y0 - BAT_WALL_TH, MID_Z,
                          BAT_X0 - BAT_FIT/2, BAT_Y1 + BAT_WALL_TH,
                          MID_Z + BAT_RET_H), op='UNION')
    for y0, y1 in ((BAT_Y0 - BAT_WALL_TH, BAT_Y0 - BAT_FIT/2),
                   (BAT_Y1 + BAT_FIT/2, BAT_Y1 + BAT_WALL_TH)):
        boolean(tray, add_box(f"bat_end_{y0:.0f}",
                              BAT_X0 - BAT_WALL_TH, y0, MID_Z,
                              BAT_X1 + BAT_WALL_TH, y1, MID_Z + BAT_RET_H),
                op='UNION')

    tray.name = "case_tray"
    return tray


def _b(x0, y0, z0, x1, y1, z1):
    return (x0, y0, z0, x1, y1, z1)


def _at(cx, cy, z0, z1, sx, sy):
    return (cx - sx/2, cy - sy/2, z0, cx + sx/2, cy + sy/2, z1)


def _hit(a, b):
    """3D AABB overlap. Touching exactly does not count."""
    return all(a[i] < b[i+3] - 1e-9 and a[i+3] > b[i] + 1e-9 for i in range(3))


def _within(inner, outer):
    return all(inner[i] >= outer[i] - 1e-9 and inner[i+3] <= outer[i+3] + 1e-9
               for i in range(3))


def check_clearances():
    errs = []

    tray_vol = _b(TRAY_MIN, TRAY_MIN, 0.0, W - TRAY_MIN, D - TRAY_MIN, H)
    speaker  = _at(SPK_CX, SPK_CY, BOT_TH + SPK_MOUNT_BOSS_H, SPK_TOP,
                   SPK_BODY_X, SPK_BODY_Y)
    pcb      = _at(PCB_CX, PCB_CY, MID_Z, MID_Z + PCB_T + PCB_COMP_H,
                   PCB_W, PCB_D)
    battery  = _b(BAT_X0, BAT_Y0, BAT_Z0, BAT_X1, BAT_Y1, BAT_Z1)
    barrel   = _at(BTN_CX, BTN_CY, H - TOP_TH - BTN_BODY_LEN, H - TOP_TH,
                   BTN_BODY_D, BTN_BODY_D)
    uswitch  = _at(BTN_CX, BTN_CY,
                   H - TOP_TH - BTN_BODY_LEN - BTN_SWITCH_LEN,
                   H - TOP_TH - BTN_BODY_LEN, BTN_SWITCH_D, BTN_SWITCH_D)

    parts = [("speaker", speaker), ("PCB", pcb), ("battery", battery),
             ("button barrel", barrel), ("microswitch", uswitch)]

    # --- the stack must not interpenetrate ---
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            if _hit(parts[i][1], parts[j][1]):
                errs.append(f"{parts[i][0]} intersects {parts[j][0]}")

    # --- everything tray-mounted has to pass up through the bottom opening ---
    posts = [(f"PCB post ({px:.0f}, {py:.0f})",
              _at(px, py, BOT_TH, MID_Z, POST_X, POST_Y))
             for px, py in pcb_posts()]
    bosses = [(f"speaker boss ({bx:.0f}, {by:.0f})",
               _at(bx, by, BOT_TH, BOT_TH + SPK_MOUNT_BOSS_H,
                   SPK_MOUNT_BOSS_OD, SPK_MOUNT_BOSS_OD))
              for bx, by in spk_boss_positions()]
    cradle = [("battery cradle support",
               _b(BAT_X0 - BAT_WALL_TH, BAT_Y0 - BAT_WALL_TH, BOT_TH,
                  BAT_X0, BAT_Y1 + BAT_WALL_TH, MID_Z)),
              ("battery cradle floor",
               _b(BAT_X0 - BAT_WALL_TH, BAT_Y0 - BAT_WALL_TH,
                  MID_Z - BAT_FLOOR_TH, BAT_X1 + BAT_WALL_TH,
                  BAT_Y1 + BAT_WALL_TH, MID_Z))]
    arms = []
    for (mx, my), (px, py) in zip(pcb_mounts(), pcb_posts()):
        a0 = min(py - POST_Y/2, my - STANDOFF_OD/2)
        a1 = max(py + POST_Y/2, my + STANDOFF_OD/2)
        arms.append((f"PCB arm ({mx:.0f}, {my:.0f})",
                     _b(px - POST_X/2, a0, ARM_Z, px + POST_X/2, a1, MID_Z)))

    tray_mounted = posts + bosses + cradle + arms + [("speaker", speaker)]
    for name, v in tray_mounted:
        if not _within(_b(v[0], v[1], 0.0, v[3], v[4], H), tray_vol):
            errs.append(f"{name} overhangs the tray edge — it cannot pass up "
                        f"through the {W - 2*WALL - 2*PANEL_INSET:.0f} mm "
                        f"bottom opening")

    # --- the speaker is the thing everything else has to dodge ---
    for name, v in posts + cradle + arms:
        if _hit(v, speaker):
            errs.append(f"{name} collides with the speaker body")
    for name, v in posts + arms + cradle + bosses:
        for cx, cy in corner_positions():
            blk = _at(cx, cy, BOT_TH, BOT_TH + CORNER_BLOCK_H,
                      CORNER_BLOCK, CORNER_BLOCK)
            if _hit(v, blk):
                errs.append(f"{name} collides with the corner block "
                            f"at ({cx:.0f}, {cy:.0f})")
    for name, v in bosses:
        for ring_r, count, hole_d in SPK_GRILLE_RINGS:
            for k in range(count):
                a = 2*math.pi*k/count
                g = _at(SPK_CX + ring_r*math.cos(a), SPK_CY + ring_r*math.sin(a),
                        0.0, BOT_TH, hole_d, hole_d)
                if _hit(v, g):
                    errs.append(f"grille hole at r={ring_r} undercuts {name}")

    # --- PCB has to actually land on its bosses ---
    for mx, my in pcb_mounts():
        if not (PCB_CX - PCB_W/2 <= mx <= PCB_CX + PCB_W/2 and
                PCB_CY - PCB_D/2 <= my <= PCB_CY + PCB_D/2):
            errs.append(f"PCB mount ({mx:.0f}, {my:.0f}) is off the board")

    # --- switch window has to expose the switch and land on the wall ---
    if not (BAT_WIN_Y0 <= BAT_SW_Y0 and BAT_WIN_Y1 >= BAT_SW_Y1 and
            BAT_WIN_Z0 <= BAT_SW_Z0 and BAT_WIN_Z1 >= BAT_SW_Z1):
        errs.append("switch window does not fully expose the switch opening")
    if BAT_WIN_Z0 < BOT_TH or BAT_WIN_Z1 > H - TOP_TH:
        errs.append("switch window runs out of the wall vertically")
    if BAT_WIN_Y0 < WALL + CORNER_R or BAT_WIN_Y1 > D - WALL - CORNER_R:
        errs.append("switch window runs into a rounded vertical corner")

    # --- button ---
    notch_r = BTN_HOLE_D/2 + BTN_NUB_R
    if notch_r > BTN_REINF_R:
        errs.append(f"nub notch (r={notch_r:.2f}) breaks out of the "
                    f"reinforcement ring (r={BTN_REINF_R:.2f})")
    if BTN_NUB_R < BTN_NUB_D/2:
        errs.append("nub notch is smaller than the nub")
    if notch_r > BTN_FLANGE_D/2:
        errs.append(f"nub notch (r={notch_r:.2f}) sticks out past the flange "
                    f"(r={BTN_FLANGE_D/2:.2f}) and would show")
    # The top rim round is what limits flange seating.
    flat_half = W/2 - TOP_R
    if flat_half < BTN_FLANGE_D/2:
        errs.append(f"top rim round {TOP_R:.1f} leaves only {flat_half:.2f} mm "
                    f"of flat, less than the flange needs "
                    f"({BTN_FLANGE_D/2:.2f} mm)")
    if BTN_CY + notch_r > D - WALL or BTN_CX + BTN_REINF_R > W - WALL:
        errs.append("button hardware reaches a side wall")

    if errs:
        for e in errs:
            print("CLEARANCE FAIL:", e)
        raise SystemExit("clearance checks failed")

    print("clearance checks PASS")
    print(f"  shell       {W:.0f} x {D:.0f} x {H:.0f}   corners r={CORNER_R:.0f}"
          f"  top rim r={TOP_R:.0f}  bottom rim r={BOT_R:.0f}")
    print(f"  speaker     z[{speaker[2]:.2f} {speaker[5]:.2f}]"
          f"   x[{speaker[0]:.2f} {speaker[3]:.2f}]")
    print(f"  PCB         z[{pcb[2]:.2f} {pcb[5]:.2f}]"
          f"   x[{pcb[0]:.2f} {pcb[3]:.2f}] y[{pcb[1]:.2f} {pcb[4]:.2f}]")
    print(f"  battery     z[{battery[2]:.2f} {battery[5]:.2f}]"
          f"   x[{battery[0]:.2f} {battery[3]:.2f}]"
          f"   switch recessed {BAT_X0:.1f} mm")
    print(f"  barrel      z[{barrel[2]:.2f} {barrel[5]:.2f}]"
          f"   clears battery by {barrel[2] - battery[5]:.2f} mm")
    print(f"  microswitch z[{uswitch[2]:.2f} {uswitch[5]:.2f}]"
          f"   clears PCB by {uswitch[2] - pcb[5]:.2f} mm"
          f"   (envelope {BTN_SWITCH_D:.0f} mm ASSUMED)")
    print(f"  flange seat {flat_half - BTN_FLANGE_D/2:.2f} mm of flat outside "
          f"the flange")


def build_foot():
    fx, fy, fz = -50.0, 0.0, FOOT_H/2
    foot = add_cyl("foot_puck", FOOT_OD/2, FOOT_H, fx, fy, fz)
    boolean(foot, add_cyl("foot_clr", SCREW_CLEAR_D/2, FOOT_H + 2.0, fx, fy, fz))
    boolean(foot, add_cone("foot_csk", COUNTERSINK_D/2, SCREW_CLEAR_D/2,
                           COUNTERSINK_H, fx, fy, COUNTERSINK_H/2))
    foot.name = "case_foot"
    return foot


# ---------------------------------------------------------------------
# Post-build verification — things the constants cannot prove
# ---------------------------------------------------------------------
def verify_button_notches(body):
    """A later boolean can undo an earlier one and no numeric check will see
    it. Look for real vertices on the protruding half of each notch arc."""
    m = body.matrix_world
    counts = []
    for sign in (-1, 1):
        nx, ny = BTN_CX, BTN_CY + sign*BTN_HOLE_D/2
        n = 0
        for v in body.data.vertices:
            p = m @ v.co
            if p.z < H - TOP_TH - 1e-6:
                continue
            if abs(math.hypot(p.x - nx, p.y - ny) - BTN_NUB_R) > 0.15:
                continue
            if math.hypot(p.x - BTN_CX, p.y - BTN_CY) < BTN_HOLE_D/2 + 0.5:
                continue
            n += 1
        if n == 0:
            raise SystemExit(
                f"BUILD FAIL: nothing on the notch arc at ({nx:.1f}, {ny:.1f})"
                " — cut and then filled back in")
        counts.append(n)
    print(f"  notch arcs  {counts[0]} / {counts[1]} verts on the protruding half")


def verify_stl_scale(path, obj):
    """Slicers read STL units as mm and will load a 0.2 mm case without
    complaint, so a wrong global_scale is invisible until the print starts."""
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
          f"{size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm")


def main():
    check_clearances()
    clear_scene()
    body = build_body()
    verify_button_notches(body)
    tray = build_tray()
    foot = build_foot()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "case.blend"))

    for obj, fname in [(body, "body.stl"), (tray, "bottom.stl"),
                       (foot, "foot.stl")]:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.wm.stl_export(
            filepath=str(OUT_DIR / fname),
            export_selected_objects=True,
            global_scale=1.0,           # 1 unit == 1 mm; see verify_stl_scale
            forward_axis='Y', up_axis='Z', apply_modifiers=True,
        )
        verify_stl_scale(OUT_DIR / fname, obj)

    print(f"BUILT {VERSION}: body {len(body.data.vertices)} verts, "
          f"tray {len(tray.data.vertices)} verts, "
          f"foot {len(foot.data.vertices)} verts")


if __name__ == "__main__":
    main()
