#!/usr/bin/env python3
"""Generic Blender hero renderer for any enclosure repo (enclosure-forge).

Renders an exploded assembly settling + 360° orbit on GPU (Cycles CUDA).

Usage (on the render box, in a directory with the repo cloned):
  blender -b -P hero_generic.py -- <repo_path> <out_dir> <frames> [saveonly]

Reads bottom_shell.stl + lid.stl (+ optional extras) from output/exports/.
"""

import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
REPO = os.path.abspath(argv[0])
OUT = os.path.abspath(argv[1])
FRAMES = int(argv[2]) if len(argv) > 2 else 200
SAVEONLY = len(argv) > 3 and argv[3] == "saveonly"
EXP = os.path.join(REPO, "output", "exports")
os.makedirs(OUT, exist_ok=True)

# discover parts
import glob  # noqa: E402
bottom_p = (sorted(glob.glob(os.path.join(EXP, "*bottom*.stl")))
            + sorted(glob.glob(os.path.join(EXP, "bottom_shell.stl"))))
lid_p = (sorted(glob.glob(os.path.join(EXP, "*lid*.stl")))
         + sorted(glob.glob(os.path.join(EXP, "lid.stl"))))
extras = sorted(glob.glob(os.path.join(EXP, "reference_*board*.stl"))
                + glob.glob(os.path.join(EXP, "keypad_standin.stl"))
                + glob.glob(os.path.join(EXP, "scanner_tray.stl")))
bottom_p = bottom_p[0] if bottom_p else None
lid_p = lid_p[0] if lid_p else None

PARTS = []
if bottom_p:
    PARTS.append(("bottom", bottom_p, "petg_slate", 0.0))
if lid_p:
    PARTS.append(("lid", lid_p, "petg_slate", 40.0))
for i, ex in enumerate(extras):
    name = os.path.basename(ex).replace(".stl", "")
    mat = "keypad" if "keypad" in name else "petg_slate"
    lift = 60.0 + i * 15
    PARTS.append((name[:16], ex, mat, lift))

MATS = {
    "petg_slate": {"base": (0.15, 0.175, 0.21), "rough": 0.46, "coat": 0.28,
                   "metal": 0.0, "transmission": 0.0},
    "pcb": {"base": (0.045, 0.07, 0.055), "rough": 0.42, "coat": 0.0,
            "metal": 0.12, "transmission": 0.0},
    "keypad": {"base": (0.12, 0.125, 0.13), "rough": 0.55, "coat": 0.04,
               "metal": 0.0, "transmission": 0.0},
    "glass": {"base": (0.92, 0.94, 0.96), "rough": 0.04, "coat": 0.0,
              "metal": 0.0, "transmission": 0.92},
}


def principled(name, m):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*m["base"], 1.0)
    b.inputs["Roughness"].default_value = m["rough"]
    b.inputs["Metallic"].default_value = m["metal"]
    if "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = m["coat"]
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = m["transmission"]
    return mat


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    objs = {}
    for key, path, matname, lift in PARTS:
        if not os.path.exists(path):
            continue
        before = set(bpy.data.objects)
        bpy.ops.import_mesh.stl(filepath=path)
        o = [x for x in bpy.data.objects if x not in before][0]
        o.name = key
        o.data.materials.append(principled(matname, MATS[matname]))
        for poly in o.data.polygons:
            poly.use_smooth = True
        objs[key] = o

    if not objs:
        raise SystemExit("no STLs found")

    parts = list(objs.values())
    corners = [tuple(v[i] for i in range(3)) for o in parts for v in o.bound_box]
    cmin = [min(c[i] for c in corners) for i in range(3)]
    cmax = [max(c[i] for c in corners) for i in range(3)]
    center = tuple((cmin[i] + cmax[i]) / 2 for i in range(3))
    diag = math.dist((cmin[0], cmin[1]), (cmax[0], cmax[1]))

    bpy.ops.mesh.primitive_plane_add(size=900,
                                     location=(center[0], center[1], cmin[2] - 14))
    floor = bpy.context.object
    floor.data.materials.append(principled("Floor",
                                           {"base": (0.72, 0.73, 0.75),
                                            "rough": 0.62, "coat": 0,
                                            "metal": 0, "transmission": 0}))

    def area(name, loc, size, energy):
        bpy.ops.object.light_add(type="AREA", location=loc)
        lt = bpy.context.object
        lt.data.shape = "SQUARE"
        lt.data.size = size
        lt.data.energy = energy
        lt.name = name

    area("key", (center[0] + 120, center[1] - 160, 220), 140, 5200)
    area("fill", (center[0] - 190, center[1] - 60, 90), 180, 1600)
    area("rim", (center[0] - 40, center[1] + 190, 160), 90, 3000)

    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.045, 0.05, 0.06, 1.0)
    bg.inputs[1].default_value = 1.0
    scene.world = world

    hfov = 2 * math.atan(18.0 / 85.0)
    R = (diag * 1.18) / (2 * math.tan(hfov / 2))
    settle_frame = int(FRAMES * 0.38)

    orbit = bpy.data.objects.new("orbit", None)
    scene.collection.objects.link(orbit)
    orbit.location = center
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 85
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.parent = orbit
    cam.location = (R, 0.0, R * 0.34)

    focus = bpy.data.objects.new("focus", None)
    scene.collection.objects.link(focus)
    focus.location = center
    con = cam.constraints.new(type="TRACK_TO")
    con.target = focus
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"

    for key, (_, _, _, lift) in zip(objs, PARTS):
        o = objs[key]
        o.location.z = lift
        o.keyframe_insert("location", frame=1)
        o.location.z = 0.0
        o.keyframe_insert("location", frame=settle_frame)
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"

    orbit.rotation_euler.z = math.radians(-14)
    orbit.keyframe_insert("rotation_euler", frame=1)
    orbit.rotation_euler.z = 0.0
    orbit.keyframe_insert("rotation_euler", frame=settle_frame)
    orbit.rotation_euler.z = math.radians(346)
    orbit.keyframe_insert("rotation_euler", frame=FRAMES)
    for fc in orbit.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
    cam.location = (R * 1.3, 0.0, R * 0.5)
    cam.keyframe_insert("location", frame=1)
    cam.location = (R, 0.0, R * 0.34)
    cam.keyframe_insert("location", frame=settle_frame)

    if SAVEONLY:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "hero.blend"))
        print("BLEND_SAVED")
        return

    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "CUDA"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
    except Exception:
        pass
    scene.cycles.samples = 192
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.fps = 30
    scene.frame_start, scene.frame_end = 1, FRAMES

    for still in (int(FRAMES * 0.2), settle_frame, int(FRAMES * 0.8)):
        scene.frame_set(still)
        scene.render.filepath = os.path.join(OUT, f"still_{still:03d}.png")
        scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(write_still=True)

    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(OUT, "frames", "frame_####.png")
    os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
    bpy.ops.render.render(animation=True)
    print("HERO_DONE", OUT)


main()
