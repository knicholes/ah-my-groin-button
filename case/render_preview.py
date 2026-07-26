"""Render preview images of the case from case.blend.

Run with:
    "K:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" \
        --background --python render_preview.py

Outputs preview-*.png into build_case.py's OUT_DIR, next to the model it
renders. Purely a visual sanity check -- build_case.py's check_clearances()
and verify_button_notches() are the authoritative tests.

Proxy boxes are drawn at the battery holder's and speaker's nominal positions
so the pockets and the switch window can be judged against the parts they
exist for.
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(r"I:\code\ah-my-groin-button\case")
sys.path.insert(0, str(HERE))

from build_case import (  # noqa: E402  -- needs HERE on sys.path first
    OUT_DIR,
    BAT_CX, BAT_CY, BAT_LEN, BAT_WIDTH, BAT_HEIGHT,
    BAT_SW_X0, BAT_SW_X1, BAT_SW_Y0, BAT_SW_Y1,
    SPK_CX, SPK_CY, SPK_BODY_X, SPK_BODY_Y, SPK_BODY_H, SPK_MOUNT_BOSS_H,
    BTN_CX, BTN_CY, BTN_HOLE_D, BTN_NUB_R,
    BOT_TH, H,
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


def add_box(name, sx, sy, sz, cx, cy, cz, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    o = bpy.context.active_object
    o.name = name
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    o.color = color
    o.hide_render = True          # opt in per shot
    return o


bat = add_box("proxy_battery", BAT_LEN, BAT_WIDTH, BAT_HEIGHT,
              BAT_CX, BAT_CY, BOT_TH + BAT_HEIGHT/2,
              (0.20, 0.55, 0.30, 1.0))
# Marker for the switch opening on the holder's downward-facing side.
sw = add_box("proxy_switch",
             BAT_SW_X1 - BAT_SW_X0, BAT_SW_Y1 - BAT_SW_Y0, 1.2,
             (BAT_SW_X0 + BAT_SW_X1)/2, (BAT_SW_Y0 + BAT_SW_Y1)/2,
             BOT_TH + 0.6,
             (0.90, 0.15, 0.15, 1.0))
spk = add_box("proxy_speaker", SPK_BODY_X, SPK_BODY_Y, SPK_BODY_H,
              SPK_CX, SPK_CY, BOT_TH + SPK_MOUNT_BOSS_H + SPK_BODY_H/2,
              (0.25, 0.30, 0.55, 1.0))

# Backing card. Parked inside the case under the button, it turns the button
# hole into a bright silhouette when shot flat-on -- otherwise the hole reads
# as an unlit cavity and the notches vanish into it.
card = add_box("backing_card", 110.0, 110.0, 1.0, BTN_CX, BTN_CY, H - 30.0,
               (0.95, 0.45, 0.10, 1.0))


# One camera, repositioned per shot. Creating a fresh camera per render leaves
# the earlier ones in the scene, where they show up as stray gizmo geometry in
# later shots -- which is exactly what happened over the button hole.
_cam_data = bpy.data.cameras.new("preview_cam")
_cam_data.clip_end = 5000.0
_cam_data.lens = 55.0
_cam = bpy.data.objects.new("preview_cam", _cam_data)
scene.collection.objects.link(_cam)
scene.camera = _cam


def render(name, loc, target, show=(), hide=(), ortho=None, res=(1600, 1000),
           flat=False):
    """One shot.

    `ortho` is the span in mm across the LONGER image axis. Getting that
    backwards is what cropped the button notches out of frame the first time:
    at 1600x1000 an ortho_scale of 115 covers 115 mm across but only 71.9 mm
    down, and the notches are 96 mm apart on Y.
    """
    for o in show:
        o.hide_render = False
    for o in hide:
        o.hide_render = True
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.display.shading.light = 'FLAT' if flat else 'STUDIO'
    scene.display.shading.show_cavity = not flat
    _cam_data.type = 'ORTHO' if ortho else 'PERSP'
    if ortho:
        _cam_data.ortho_scale = ortho
    _cam.location = Vector(loc)
    _cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(OUT_DIR / ("preview-%s.png" % name))
    bpy.ops.render.render(write_still=True)
    print("rendered preview-%s.png" % name)
    for o in show:
        o.hide_render = True
    for o in hide:
        o.hide_render = False


# 1. Straight up at the underside of the tray -- the switch hole and its
#    finger scallop, against the grille and the corner screw holes.
render("tray-bottom", (100.0, 65.0, -300.0), (100.0, 65.0, 0.0),
       hide=(body,), ortho=210.0)

# 2. Three-quarter from the front-right with the parts in place.
render("tray-pocket", (330.0, -240.0, 190.0), (140.0, 45.0, 25.0),
       show=(bat, sw, spk), hide=(body,))

# 3. Everything together from the front-left.
render("assembled", (-160.0, -330.0, 230.0), (100.0, 65.0, 40.0))

# 4. Flat-on down the button hole. Square frame and a span wider than the
#    notch-to-notch distance, or the notches fall outside the image.
span = BTN_HOLE_D + 2*BTN_NUB_R + 14.0
render("button-notches", (BTN_CX, BTN_CY, 300.0), (BTN_CX, BTN_CY, 0.0),
       show=(card,), hide=(tray,), ortho=span, res=(1200, 1200), flat=True)

# 5. Same shot zoomed onto one notch. At full-hole framing a 4 mm bump on a
#    44 mm radius is only a few percent of the outline and reads as noise;
#    this is the one that actually proves the notch is cut.
notch_y = BTN_CY + BTN_HOLE_D/2
render("button-notch-detail", (BTN_CX, notch_y, 300.0), (BTN_CX, notch_y, 0.0),
       show=(card,), hide=(tray,), ortho=26.0, res=(1200, 1200), flat=True)

sys.stdout.flush()
