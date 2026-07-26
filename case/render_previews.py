"""Render whole-case views (perspective / top / front / bottom / exploded).

Largely superseded by render_preview.py, which targets specific features with
controlled framing. This one still earns its keep for the exploded and
all-round shots.
"""
from pathlib import Path
import math
import sys
import bpy

sys.path.insert(0, str(Path(__file__).parent))
from build_case import OUT_DIR  # noqa: E402

bpy.ops.wm.open_mainfile(filepath=str(OUT_DIR / "case.blend"))

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'

# Set up lighting (workbench engine has its own auto-lighting; we just set a
# studio-style view).
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (0.8, 0.4, 0.3)   # rough plastic-orange tint
scene.display.shading.show_cavity = True

# Calculate scene centre & size
import bmesh
verts = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        m = obj.matrix_world
        for v in obj.data.vertices:
            verts.append(m @ v.co)
xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
cx, cy, cz = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2, (min(zs)+max(zs))/2
size = max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))

def render_view(name, eye_offset, look_at=(cx, cy, cz)):
    # Camera
    if 'Camera' in bpy.data.objects:
        cam = bpy.data.objects['Camera']
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = 'Camera'
    cam.location = (look_at[0] + eye_offset[0], look_at[1] + eye_offset[1], look_at[2] + eye_offset[2])
    # Aim at the target
    direction = (look_at[0] - cam.location[0],
                 look_at[1] - cam.location[1],
                 look_at[2] - cam.location[2])
    rot_euler = bpy.data.objects['Camera'].rotation_euler
    import mathutils
    dir_vec = mathutils.Vector(direction)
    cam.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 50
    scene.camera = cam

    scene.render.filepath = str(OUT_DIR / f"render-{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"rendered {name}")

# Closed-view renders first
render_view("perspective", (size*1.2, -size*1.5, size*1.0))
render_view("top",          (0, 0, size*1.8))
render_view("front",        (0, -size*2.0, size*0.3))
render_view("bottom",       (0, 0, -size*1.8))

# Exploded view — lift the body UP by 60 mm
if 'case_body' in bpy.data.objects:
    bpy.data.objects['case_body'].location.z += 60
render_view("exploded", (size*1.3, -size*1.5, size*1.2))

# Tray-only view: hide the body
if 'case_body' in bpy.data.objects:
    bpy.data.objects['case_body'].hide_render = True
render_view("tray_top", (0, 0, size*1.4), look_at=(100.0, 65.0, 15.0))
