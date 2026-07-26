"""Render preview images of the case from case.blend.

Run with:
    "K:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" \
        --background --python render_preview.py

Outputs preview-*.png next to the model. Purely a visual sanity check --
build_case.py's check_clearances() is the authoritative test.

A proxy box is drawn at the battery holder's nominal position so the pocket
and the switch window can be judged against the part they exist for.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(r"I:\code\ah-my-groin-button\case")
sys.path.insert(0, str(HERE))

from build_case import (  # noqa: E402  -- needs HERE on sys.path first
    BAT_CX, BAT_W, BAT_H, BAT_D, BAT_FRONT_Y, BOT_TH,
    BAT_SW_CX, BAT_SW_CZ, BAT_SW_FROM_RIGHT, BAT_SW_FROM_TOP,
)

bpy.ops.wm.open_mainfile(filepath=str(HERE / "case.blend"))
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'OBJECT'
scene.display.shading.show_cavity = True

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
    return o


# Proxy battery holder, plus a marker for the switch opening on its face.
bat = add_box("proxy_battery", BAT_W, BAT_D, BAT_H,
              BAT_CX, BAT_FRONT_Y + BAT_D/2, BOT_TH + BAT_H/2,
              (0.20, 0.55, 0.30, 1.0))
sw = add_box("proxy_switch",
             max(BAT_SW_FROM_RIGHT) - min(BAT_SW_FROM_RIGHT),
             2.0,
             max(BAT_SW_FROM_TOP) - min(BAT_SW_FROM_TOP),
             BAT_SW_CX, BAT_FRONT_Y - 0.5, BAT_SW_CZ,
             (0.90, 0.15, 0.15, 1.0))


def render(name, loc, target, hide=()):
    for o in hide:
        o.hide_render = True
    cam_data = bpy.data.cameras.new(name)
    cam_data.clip_end = 5000.0
    cam_data.lens = 55.0
    cam = bpy.data.objects.new(name, cam_data)
    scene.collection.objects.link(cam)
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam
    scene.render.filepath = str(HERE / ("preview-%s.png" % name))
    bpy.ops.render.render(write_still=True)
    print("rendered preview-%s.png" % name)
    for o in hide:
        o.hide_render = False


# 1. Straight at the front wall -- is the window over the switch?
render("front-switch", (BAT_SW_CX, -230.0, BAT_SW_CZ + 10.0),
       (BAT_SW_CX, 0.0, BAT_SW_CZ))

# 2. Three-quarter from the front-right, body hidden, showing the pocket.
render("tray-pocket", (330.0, -240.0, 190.0), (140.0, 45.0, 25.0), hide=(body,))

# 3. Everything together from the front-left.
render("assembled", (-160.0, -330.0, 230.0), (100.0, 65.0, 40.0))

sys.stdout.flush()
