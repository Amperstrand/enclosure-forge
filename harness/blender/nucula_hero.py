#!/usr/bin/env python3
"""Nucula V4 hero animation — photoreal Blender scene (enclosure-forge).

Run headless on the GPU box:
  blender -b -P nucula_hero.py -- <repo_clone> <out_dir> [frames]

Scene: exploded payment-terminal assembly (bottom, board, battery,
glass, keypad, lid) settling together, then a slow turntable.
Cycles + OptiX, 1080p, MP4. Parts import pre-positioned (one CAD frame).
"""

import math
import os
import sys

import bpy
import bpy_extras.node_shader_utils  # noqa: F401  (available in 4.x)

argv = sys.argv[sys.argv.index("--") + 1:]
REPO = os.path.abspath(argv[0])
OUT = os.path.abspath(argv[1]) if len(argv) > 1 else "/tmp/nucula-hero"
FRAMES = int(argv[2]) if len(argv) > 2 else 165
EXP = os.path.join(REPO, "output", "exports")
os.makedirs(OUT, exist_ok=True)

PARTS = [
    ("V4_bottom_shell_terminal.stl", "bottom", "petg_slate", 0.0),
    ("reference_full_board.stl", "board", "pcb", 0.0),
    ("battery.stl", "battery", "battery", 0.0),
    ("glass.stl", "glass", "glass", 90.0),
    ("keypad_standin.stl", "keypad", "keypad", 60.0),
    ("V4_lid_terminal.stl", "lid", "petg_slate", 40.0),
]


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_stl(name, path):
    before = set(bpy.data.objects)
    bpy.ops.import_mesh.stl(filepath=path)
    obj = [o for o in bpy.data.objects if o not in before][0]
    obj.name = name
    return obj


def principled(name, base, rough=0.4, metallic=0.0, coat=0.1,
               transmission=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if "Coat Weight" in bsdf.inputs:            # blender 4.x
        bsdf.inputs["Coat Weight"].default_value = coat
    if "Transmission Weight" in bsdf.inputs:    # blender 4.x
        bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["IOR"].default_value = ior
    return mat


def main():
    clear_scene()
    scene = bpy.context.scene

    mats = {
        "petg_slate": principled("PETG_slate", (0.16, 0.19, 0.23),
                                 rough=0.34, coat=0.18),
        "pcb": principled("PCB", (0.045, 0.07, 0.055), rough=0.42,
                          metallic=0.12),
        "glass": principled("Glass", (0.92, 0.94, 0.96), rough=0.04,
                            transmission=0.92, ior=1.5),
        "keypad": principled("Keypad", (0.10, 0.11, 0.12), rough=0.48,
                             coat=0.05),
        "battery": principled("Battery", (0.55, 0.33, 0.22), rough=0.5,
                              metallic=0.25),
    }

    objs = {}
    for fname, key, matname, lift in PARTS:
        path = os.path.join(EXP, fname)
        if not os.path.exists(path):
            raise SystemExit(f"missing {path}")
        o = import_stl(key, path)
        o.data.materials.append(mats[matname])
        objs[key] = o
        for poly in o.data.polygons:
            poly.use_smooth = True

    bb = objs["bottom"].dimensions
    bbox = objs["bottom"].bound_box
    center = (sum(v[0] for v in bbox) / 8, sum(v[1] for v in bbox) / 8, 0)

    # ground plane
    bpy.ops.mesh.primitive_plane_add(size=900, location=(center[0], center[1], -14))
    floor = bpy.context.object
    floor.data.materials.append(principled("Floor", (0.72, 0.73, 0.75),
                                           rough=0.62))

    # lights: key / fill / rim (studio)
    def area(name, loc, size, energy):
        bpy.ops.object.light_add(type="AREA", location=loc)
        lt = bpy.context.object
        lt.data.shape = "SQUARE"
        lt.data.size = size
        lt.data.energy = energy
        lt.name = name
        return lt

    area("key", (center[0] + 120, center[1] - 160, 220), 140, 5200)
    area("fill", (center[0] - 190, center[1] - 60, 90), 180, 1600)
    area("rim", (center[0] - 40, center[1] + 190, 160), 90, 3000)

    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.045, 0.05, 0.06, 1.0)
    bg.inputs[1].default_value = 1.0
    scene.world = world

    # camera
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    R = max(bb.x, bb.y) * 1.55 + 30
    settle_frame = int(FRAMES * 0.38)

    # explode offsets animate to zero
    for key, (_, _, _, lift) in zip(objs, PARTS):
        o = objs[key]
        o.location.z = lift
        o.keyframe_insert("location", frame=1)
        o.location.z = 0.0
        o.keyframe_insert("location", frame=settle_frame)
        # ease
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "EASE_OUT"

    # turntable: rotate the whole assembly via parent empty
    empty = bpy.data.objects.new("assembly", None)
    scene.collection.objects.link(empty)
    empty.location = (center[0], center[1], 0)
    for o in objs.values():
        o.parent = empty
    empty.rotation_euler.z = 0.0
    empty.keyframe_insert("rotation_euler", frame=settle_frame)
    empty.rotation_euler.z = math.radians(360)
    empty.keyframe_insert("rotation_euler", frame=FRAMES)

    # camera path: dolly in during settle, then slow orbit opposite
    def cam_at(frame, radius, elev_deg, az_deg):
        el, az = math.radians(elev_deg), math.radians(az_deg)
        cam.location = (
            center[0] + radius * math.cos(el) * math.sin(az),
            center[1] - radius * math.cos(el) * math.cos(az),
            radius * math.sin(el))
        rot = (math.pi / 2 - el, 0.0, az)
        cam.rotation_euler = (0, 0, 0)
        cam.rotation_euler = rot
        cam.keyframe_insert("location", frame=frame)
        cam.keyframe_insert("rotation_euler", frame=frame)

    cam_at(1, R * 1.5, 32, 38)
    cam_at(settle_frame, R, 22, 30)
    cam_at(FRAMES, R * 0.96, 18, 30 - 150)

    # render settings
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "CUDA"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
    except Exception as exc:  # noqa: BLE001
        print("cuda fallback:", exc)
        scene.cycles.device = "GPU"
    scene.cycles.samples = 256
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.fps = 30
    scene.frame_start, scene.frame_end = 1, FRAMES
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.filepath = os.path.join(OUT, "nucula_hero.mp4")

    for still in (int(FRAMES * 0.2), settle_frame, int(FRAMES * 0.8)):
        scene.frame_set(still)
        scene.render.filepath = os.path.join(OUT, f"still_{still:03d}.png")
        scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(write_still=True)

    scene.render.filepath = os.path.join(OUT, "nucula_hero.mp4")
    scene.render.image_settings.file_format = "FFMPEG"
    bpy.ops.render.render(animation=True)
    print("HERO_DONE", OUT)


main()
