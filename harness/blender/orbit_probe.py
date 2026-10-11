#!/usr/bin/env python3
"""Orbit-centring probe: render 4 azimuths, report device silhouette
centroid + bbox per frame so drift is measurable, not felt.

blender -b -P orbit_probe.py -- <repo_clone> <out_dir>
"""

import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
REPO = os.path.abspath(argv[0])
OUT = os.path.abspath(argv[1])
EXP = os.path.join(REPO, "output", "exports")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

for fname in ("V4_bottom_shell_terminal.stl", "V4_lid_terminal.stl",
              "reference_full_board.stl", "keypad_standin.stl"):
    bpy.ops.import_mesh.stl(filepath=os.path.join(EXP, fname))
    bpy.context.object.name = fname.split(".")[0]

# whole-assembly bbox centre (all imported parts)
parts = [bpy.data.objects[f] for f in
         ("V4_bottom_shell_terminal", "V4_lid_terminal",
          "reference_full_board", "keypad_standin")]
corners = [tuple(v[i] for i in range(3)) for o in parts for v in o.bound_box]
mins = [min(c[i] for c in corners) for i in range(3)]
maxs = [max(c[i] for c in corners) for i in range(3)]
cen = tuple((mins[i] + maxs[i]) / 2 for i in range(3))
print("ASSEMBLY_CENTRE", [round(c, 2) for c in cen])
print("ASSEMBLY_SIZE", [round(maxs[i] - mins[i], 2) for i in range(3)])

bottom = bpy.data.objects["V4_bottom_shell_terminal"]
bmin = [min(bottom.bound_box, key=lambda v: v[i])[i] for i in range(2)]
bmax = [max(bottom.bound_box, key=lambda v: v[i])[i] for i in range(2)]
print("BOTTOM_CENTRE_XY", [round((bmin[i] + bmax[i]) / 2, 2) for i in range(2)])

bpy.ops.object.light_add(type="AREA", location=(cen[0] + 120, cen[1] - 160, 220))
bpy.context.object.data.energy = 20000
bpy.context.object.data.size = 150
bpy.ops.object.light_add(type="SUN", location=(cen[0], cen[1], 300))
bpy.context.object.data.energy = 3.0
world = bpy.data.worlds.new("probe_world")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.28, 0.29, 0.31, 1.0)
bg.inputs[1].default_value = 1.0
scene.world = world

cam_data = bpy.data.cameras.new("probe_cam")
cam_data.lens = 50
cam = bpy.data.objects.new("probe_cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

focus = bpy.data.objects.new("focus", None)
scene.collection.objects.link(focus)
focus.location = cen
con = cam.constraints.new(type="TRACK_TO")
con.target = focus
con.track_axis = "TRACK_NEGATIVE_Z"
con.up_axis = "UP_Y"

diag = math.dist((mins[0], mins[1]), (maxs[0], maxs[1]))
R = diag * 1.35

scene.render.engine = "CYCLES"
scene.cycles.device = "GPU"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
except Exception:  # noqa: BLE001
    pass
scene.cycles.samples = 24
scene.cycles.use_denoising = False
scene.render.resolution_x = 960
scene.render.resolution_y = 540

for az in (0, 90, 180, 270):
    a = math.radians(az)
    cam.location = (cen[0] + R * math.cos(a),
                    cen[1] + R * math.sin(a),
                    cen[2] + R * 0.38)
    scene.frame_set(1)
    scene.render.filepath = os.path.join(OUT, f"probe_{az:03d}.png")
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", az)
print("PROBE_DONE")
