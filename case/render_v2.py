"""Preview renders for the v2 tall case.

Run with:
    "K:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" \
        --background --python render_v2.py

Writes preview-*.png into build_v2.py's OUT_DIR. Visual sanity only --
build_v2.py's check_clearances() is what actually gates the build.
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from build_v2 import (  # noqa: E402
    OUT_DIR, W, D, H, TOP_TH, BOT_TH, MID_Z,
    SPK_CX, SPK_CY, SPK_BODY_X, SPK_BODY_Y, SPK_BODY_H, SPK_MOUNT_BOSS_H,
    PCB_CX, PCB_CY, PCB_W, PCB_D, PCB_T, PCB_COMP_H,
    BAT_X0, BAT_X1, BAT_Y0, BAT_Y1, BAT_Z0, BAT_Z1,
    BAT_SW_Y0, BAT_SW_Y1, BAT_SW_Z0, BAT_SW_Z1,
    BTN_CX, BTN_CY, BTN_HOLE_D, BTN_NUB_R, BTN_BODY_D, BTN_BODY_LEN,
    BTN_SWITCH_D, BTN_SWITCH_LEN,
)

bpy.ops.wm.open_mainfile(filepath=str(OUT_DIR / "case.blend"))
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.color_type = 'OBJECT'

body = bpy.data.objects["case_body"]
tray = bpy.data.objects["case_tray"]
foot = bpy.data.objects["case_foot"]
body.color = (0.62, 0.66, 0.72, 1.0)
tray.color = (0.80, 0.62, 0.35, 1.0)
foot.hide_render = True


def box(name, x0, y0, z0, x1, y1, z1, color):
    bpy.ops.mesh.primitive_cube_add(
        size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    o = bpy.context.active_object
    o.name = name
    o.scale = (x1-x0, y1-y0, z1-z0)
    bpy.ops.object.transform_apply(scale=True)
    o.color = color
    o.hide_render = True
    return o


spk = box("proxy_speaker",
          SPK_CX - SPK_BODY_X/2, SPK_CY - SPK_BODY_Y/2,
          BOT_TH + SPK_MOUNT_BOSS_H,
          SPK_CX + SPK_BODY_X/2, SPK_CY + SPK_BODY_Y/2,
          BOT_TH + SPK_MOUNT_BOSS_H + SPK_BODY_H, (0.25, 0.30, 0.55, 1.0))
pcb = box("proxy_pcb",
          PCB_CX - PCB_W/2, PCB_CY - PCB_D/2, MID_Z,
          PCB_CX + PCB_W/2, PCB_CY + PCB_D/2, MID_Z + PCB_T + PCB_COMP_H,
          (0.15, 0.45, 0.25, 1.0))
bat = box("proxy_battery", BAT_X0, BAT_Y0, BAT_Z0, BAT_X1, BAT_Y1, BAT_Z1,
          (0.20, 0.55, 0.30, 1.0))
sw = box("proxy_switch", BAT_X0 - 1.2, BAT_SW_Y0, BAT_SW_Z0,
         BAT_X0, BAT_SW_Y1, BAT_SW_Z1, (0.90, 0.15, 0.15, 1.0))
btn = box("proxy_button",
          BTN_CX - BTN_BODY_D/2, BTN_CY - BTN_BODY_D/2,
          H - TOP_TH - BTN_BODY_LEN,
          BTN_CX + BTN_BODY_D/2, BTN_CY + BTN_BODY_D/2, H - TOP_TH,
          (0.70, 0.18, 0.18, 1.0))
usw = box("proxy_microswitch",
          BTN_CX - BTN_SWITCH_D/2, BTN_CY - BTN_SWITCH_D/2,
          H - TOP_TH - BTN_BODY_LEN - BTN_SWITCH_LEN,
          BTN_CX + BTN_SWITCH_D/2, BTN_CY + BTN_SWITCH_D/2,
          H - TOP_TH - BTN_BODY_LEN, (0.85, 0.55, 0.15, 1.0))
card = box("backing_card", BTN_CX - 55, BTN_CY - 55, H - 30,
           BTN_CX + 55, BTN_CY + 55, H - 29, (0.95, 0.45, 0.10, 1.0))

_cd = bpy.data.cameras.new("cam")
_cd.clip_end = 5000.0
_cd.lens = 55.0
_c = bpy.data.objects.new("cam", _cd)
scene.collection.objects.link(_c)
scene.camera = _c


def render(name, loc, target, show=(), hide=(), ortho=None, res=(1200, 1400),
           flat=False):
    """`ortho` is the span in mm across the LONGER image axis."""
    for o in show:
        o.hide_render = False
    for o in hide:
        o.hide_render = True
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.display.shading.light = 'FLAT' if flat else 'STUDIO'
    scene.display.shading.show_cavity = not flat
    _cd.type = 'ORTHO' if ortho else 'PERSP'
    if ortho:
        _cd.ortho_scale = ortho
    _c.location = Vector(loc)
    _c.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(OUT_DIR / ("preview-%s.png" % name))
    bpy.ops.render.render(write_still=True)
    print("rendered preview-%s.png" % name)
    for o in show:
        o.hide_render = True
    for o in hide:
        o.hide_render = False


# 1. The whole thing, rounded shell on show.
render("assembled", (-260.0, -320.0, 250.0), (60.0, 60.0, 65.0))

# 2. Body hidden, so the stack reads: speaker, PCB on its offset posts,
#    battery standing in its cradle, button and microswitch hanging in.
render("stack", (320.0, -300.0, 210.0), (55.0, 60.0, 60.0),
       show=(spk, pcb, bat, sw, btn, usw), hide=(body,))

# 3. Tray alone from the front-left -- the posts, arms and cradle.
render("tray", (-230.0, -260.0, 170.0), (60.0, 60.0, 25.0), hide=(body,))

# 4. Straight at the -X wall: is the window over the switch?
render("switch-window", (-320.0, 40.0, 84.0), (0.0, 40.0, 84.0),
       show=(bat, sw), ortho=90.0, res=(1200, 1200))

# 5. Flat-on down the button hole. Square frame, span wider than the notches.
span = BTN_HOLE_D + 2*BTN_NUB_R + 14.0
render("button-notches", (BTN_CX, BTN_CY, 320.0), (BTN_CX, BTN_CY, 0.0),
       show=(card,), hide=(tray,), ortho=span, res=(1200, 1200), flat=True)

# 6. Underside -- grille and feet pattern.
render("tray-bottom", (60.0, 60.0, -300.0), (60.0, 60.0, 0.0),
       hide=(body,), ortho=115.0, res=(1200, 1200))

sys.stdout.flush()
