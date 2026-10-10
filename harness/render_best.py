#!/usr/bin/env python3
"""Render the best version of an enclosure repo (enclosure-forge P15).

Outputs into the repo: renders/<repo>_iso|top|usb.png (three.js via the
system chromium through playwright, if available) + exports assembly
GLB (bottom + lid + board proxy, tinted) viewable in any 3D viewer.

Usage: python3 harness/render_best.py <repo_root> [part_names ...]
Defaults part names: bottom_shell lid (falls back to any bottom*/lid*).
"""

from __future__ import annotations

import glob
import os
import sys

import trimesh

THREE = os.path.expanduser(
    "~/src/nucula-enclosure/reference/three.min.js")
STLLOADER = os.path.expanduser(
    "~/src/nucula-enclosure/reference/STLLoader.js")
CHROMIUM = "/usr/lib/chromium/chromium"

COLORS = {"bottom": 0x2f3a45, "lid": 0x3c4a57, "board": 0x1a6e8a}


def _pick(repo, kind):
    pats = {"bottom": ["*bottom*.stl", "*base*.stl"],
            "lid": ["*lid*.stl", "*top*.stl", "*cap*.stl"]}
    for pat in pats[kind]:
        hits = sorted(glob.glob(os.path.join(repo, "output", "exports", pat)))
        if hits:
            return hits[0]
    return None


def assembly_glb(repo, bottom_p, lid_p, out_path):
    scene = trimesh.Scene()
    bottom = trimesh.load(bottom_p)
    lid = trimesh.load(lid_p)
    bottom.visual.face_colors = trimesh.visual.color.hex_to_rgba("#2f3a45")
    lid.visual.face_colors = trimesh.visual.color.hex_to_rgba("#3c4a57")
    scene.add_geometry(bottom, node_name="bottom")
    lid_apply = lid.copy()
    lid_apply.apply_translation([0, 0, 0])
    scene.add_geometry(lid_apply, node_name="lid")
    bb = bottom.bounds
    board = trimesh.creation.box(
        extents=[bb[1][0] - bb[0][0] - 3.2, bb[1][1] - bb[0][1] - 3.2, 1.6])
    board.apply_translation([(bb[0][0] + bb[1][0]) / 2,
                             (bb[0][1] + bb[1][1]) / 2, 1.8 + 0.8])
    board.visual.face_colors = trimesh.visual.color.hex_to_rgba("#1a6e8a")
    scene.add_geometry(board, node_name="board_proxy")
    scene.export(out_path)
    return out_path


PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{margin:0;background:#101418}</style></head><body>
<div id="v"></div>
<script src="file://__THREE__"></script><script src="file://__LOADER__"></script>
<script>
const PARTS = __PARTS__;
const VIEWS = __VIEWS__;
function render(){const c=document.getElementById('v');
const s=new THREE.Scene(); s.background=new THREE.Color(0x101418);
const r=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
r.setSize(1600,1000); c.appendChild(r.domElement);
s.add(new THREE.DirectionalLight(0xffffff,0.9).translateX(80).translateY(120).translateZ(160));
s.add(new THREE.DirectionalLight(0xbfd4dd,0.45).translateX(-120).translateY(-40).translateZ(60));
s.add(new THREE.AmbientLight(0xffffff,0.38));
let pending=PARTS.length; const meshes={};
for(const [tag,file,color] of PARTS){
 new THREE.STLLoader().load(file,g=>{const m=new THREE.Mesh(g,
  new THREE.MeshPhongMaterial({color:color,shininess:42}));
  meshes[tag]=m; if(--pending===0)shoot();});}
function shoot(){const box=new THREE.Box3();
for(const t in meshes){box.expandByObject(meshes[t]);s.add(meshes[t]);}
const ctr=box.getCenter(new THREE.Vector3());
const size=box.getSize(new THREE.Vector3());
const rad=Math.max(size.x,size.y,size.z);
const cam=new THREE.PerspectiveCamera(32,1.6,1,4000); let i=0;
function shot(){if(i>=VIEWS.length){document.title='DONE';return;}
const v=VIEWS[i];const look=v.center?new THREE.Vector3(...v.center):ctr;
const er=v.span?v.span:rad;const az=v.az*Math.PI/180,el=v.el*Math.PI/180;
const d=er*(v.dist||2.1);
cam.position.set(look.x+d*Math.cos(el)*Math.sin(az),
look.y-d*Math.cos(el)*Math.cos(az),look.z+d*Math.sin(el));
cam.up.set(0,0,1);cam.lookAt(look);r.render(scene,cam);
window.__m='S'+i;i++;}
window.__next=shot;shot();}}
render();</script></body></html>"""


def png_renders(repo, bottom_p, lid_p, name):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  playwright not installed -> PNG skipped")
        return False
    out = os.path.join(repo, "renders")
    os.makedirs(out, exist_ok=True)
    parts = [["bottom", bottom_p, COLORS["bottom"]],
             ["lid", lid_p, COLORS["lid"]]]
    views = [
        {"az": 35, "el": 28, "path": os.path.join(out, f"{name}_iso.png")},
        {"az": 0, "el": 88, "path": os.path.join(out, f"{name}_top.png")},
        {"az": -55, "el": 18, "path": os.path.join(out, f"{name}_usb.png")},
    ]
    html = (PAGE.replace("__THREE__", THREE).replace("__LOADER__", STLLOADER)
            .replace("__PARTS__", str(parts).replace("'", '"'))
            .replace("__VIEWS__", str(views).replace("'", '"')))
    tmp = os.path.join(out, "_scene.html")
    open(tmp, "w").write(html)
    try:
        with sync_playwright() as pw:
            launch = {"args": ["--allow-file-access-from-files"]}
            if os.path.exists(CHROMIUM):
                launch["executable_path"] = CHROMIUM
            browser = pw.chromium.launch(**launch)
            page = browser.new_page(viewport={"width": 1620, "height": 1040})
            page.goto("file://" + tmp)
            for k, v in enumerate(views):
                if k > 0:
                    page.evaluate("window.__next()")
                page.wait_for_function(f"window.__m === 'S{k}'", timeout=120000)
                page.screenshot(path=v["path"])
                print("  png:", os.path.basename(v["path"]))
            browser.close()
        os.unlink(tmp)
        return True
    except Exception as e:  # noqa: BLE001
        print("  png failed:", repr(e)[:140])
        return False


def main():
    repo = os.path.abspath(sys.argv[1])
    name = os.path.basename(repo).replace("-enclosure", "").replace("-devboard", "")
    bottom_p, lid_p = _pick(repo, "bottom"), _pick(repo, "lid")
    if not (bottom_p and lid_p):
        print("missing parts in", repo)
        return 1
    print(f"== {name}: {os.path.basename(bottom_p)} + {os.path.basename(lid_p)}")
    os.makedirs(os.path.join(repo, "exports"), exist_ok=True)
    glb = assembly_glb(repo, bottom_p, lid_p,
                       os.path.join(repo, "exports", f"{name}_assembly.glb"))
    print("  glb:", os.path.basename(glb))
    png_renders(repo, bottom_p, lid_p, name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
