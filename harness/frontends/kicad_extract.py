#!/usr/bin/env python3
"""Generic KiCad .kicad_pcb -> analysis/*.json extractor (enclosure-forge S1).

Works on KiCad 6/7/8/9 s-expression boards (footprint nodes; KiCad 5
`module` nodes are NOT handled). Produces the schema the templates and
validators consume:

  analysis/pcb_geometry.json      outline, thickness, mounting holes, origin
  analysis/component_geometry.json  per-ref footprint bbox + height class

Provenance: everything here is extracted_kicad / derived_kicad. Height
classes are conservative_assumption until a datasheet/STEP overrides
them (COMP_HEIGHTS table below).

Usage: python3 kicad_extract.py <board.kicad_pcb> <out_dir> [--cross-check step]
"""

from __future__ import annotations

import json
import math
import os
import re
import sys


def parse_sexp(text: str):
    """Minimal s-expression parser -> nested lists of strings/numbers."""
    tok = re.findall(r'"[^"]*"|\(|\)|[^\s()]+', text)
    pos = 0

    def parse():
        nonlocal pos
        if tok[pos] == "(":
            pos += 1
            out = []
            while tok[pos] != ")":
                out.append(parse())
            pos += 1
            return out
        s = tok[pos]
        pos += 1
        if s.startswith('"'):
            return s[1:-1]
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s

    forms = []
    while pos < len(tok) and tok[pos] != ")":
        forms.append(parse())
    return forms


def find(node, key):
    for child in node:
        if isinstance(child, list) and child and child[0] == key:
            return child
    return None


def find_all(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def rotate(pts, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return [(x * c - y * s, x * s + y * c) for x, y in pts]


# conservative height classes by footprint-name substring (mm above the
# board face the part mounts on) -- override per-project after datasheets
COMP_HEIGHTS = [
    ("PinHeader_2.54mm", 8.5), ("PinSocket_2.54mm", 8.5),
    ("USB", 3.3), ("ZX62", 3.35), ("USB_C", 3.35),
    ("SOT-223", 6.5), ("SOT-23", 1.4), ("SOIC-8", 2.0),
    ("SOIC-16", 2.7), ("QFN-56", 0.9), ("QFN-48", 0.9), ("QFN-32", 0.9),
    ("Crystal", 0.9), ("ABM8", 0.9), ("C_0402", 0.5), ("C_0603", 0.7),
    ("C_0805", 1.0), ("C_1206", 1.2), ("R_0402", 0.5), ("R_0603", 0.7),
    ("R_0805", 1.0), ("LED", 0.8), ("Button", 2.0), ("SW_", 2.0),
    ("Connector", 7.0), ("JST", 5.6), ("TF", 2.0), ("microSD", 2.0),
]


def height_for(footprint_name: str) -> float:
    for pat, h in COMP_HEIGHTS:
        if pat.lower() in footprint_name.lower():
            return h
    return 1.0  # conservative_assumption: generic passives


def footprint_bbox(fp):
    """Footprint bbox in board coords from pads (+courtyard if present)."""
    at = find(fp, "at")
    x, y = float(at[1]), float(at[2])
    deg = float(at[3]) if len(at) > 3 else 0.0
    pts = []
    for pad in find_all(fp, "pad"):
        pad_at = find(pad, "at")
        if pad_at is None:
            continue
        px, py = float(pad_at[1]), float(pad_at[2])
        size = find(pad, "size")
        w = float(size[1]) if size else 1.0
        h = float(size[2]) if size else 1.0
        for dx, dy in ((-w / 2, -h / 2), (w / 2, h / 2)):
            rx, ry = rotate([(px + dx, py + dy)], deg)[0]
            pts.append((x + rx, y + ry))
    for gr in find_all(fp, "fp_line") + find_all(fp, "fp_rect"):
        layer = find(gr, "layer")
        if layer and "Courtyard" in str(layer[1]):
            s = find(gr, "start")
            e = find(gr, "end")
            if s and e:
                for px, py in ((float(s[1]), float(s[2])),
                               (float(e[1]), float(e[2]))):
                    rx, ry = rotate([(px, py)], deg)[0]
                    pts.append((x + rx, y + ry))
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def main() -> int:
    pcb_path, out_dir = sys.argv[1], sys.argv[2]
    forms = parse_sexp(open(pcb_path).read())
    root = next(f for f in forms if f and f[0] == "kicad_pcb")

    gen = find(root, "general") or []
    thickness = next((t for t in gen if isinstance(t, (int, float))), None)

    # outline: every Edge.Cuts line/arc/rect segment -> polyline
    segs = []
    for layer_list in (root,):
        for gr in find_all(layer_list, "gr_line") + find_all(layer_list, "gr_rect"):
            lay = find(gr, "layer")
            if not lay or "Edge.Cuts" not in str(lay[1]):
                continue
            s, e = find(gr, "start"), find(gr, "end")
            if s and e:
                segs.append(((float(s[1]), float(s[2])), (float(e[1]), float(e[2]))))
        for ga in find_all(layer_list, "gr_arc"):
            lay = find(ga, "layer")
            if not lay or "Edge.Cuts" not in str(lay[1]):
                continue
            s, m, e = find(ga, "start"), find(ga, "mid"), find(ga, "end")
            if s and m and e:
                segs.append(((float(s[1]), float(s[2])), (float(m[1]), float(m[2]))))
                segs.append(((float(m[1]), float(m[2])), (float(e[1]), float(e[2]))))
    pts = [p for seg in segs for p in seg]
    if not pts:
        print("no Edge.Cuts geometry found", file=sys.stderr)
        return 1
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)

    comps, holes = {}, []
    for fp in find_all(root, "footprint"):
        name = fp[1] if len(fp) > 1 and isinstance(fp[1], str) else "?"
        ref = None
        for t in find_all(fp, "fp_text") + find_all(fp, "property"):
            key = str(t[1]).lower()
            if key == "reference" and len(t) > 2:
                ref = t[2]
                break
        bb = footprint_bbox(fp)
        if bb is None:
            continue
        if "MountingHole" in name:
            pad = find_all(fp, "pad")
            drill = 2.7
            if pad:
                dr = find(pad[0], "drill")
                if dr:
                    drill = float(dr[1])
            holes.append({"ref": ref,
                          "center": [round((bb[0] + bb[2]) / 2 - x0, 3),
                                     round((bb[1] + bb[3]) / 2 - y0, 3)],
                          "drill": drill})
            continue
        comps[ref or name] = {
            "footprint": name,
            "u": [round(bb[0] - x0, 3), round(bb[2] - x0, 3)],
            "v": [round(bb[1] - y0, 3), round(bb[3] - y0, 3)],
            "height": height_for(name),
            "height_provenance": "conservative_assumption",
        }

    geom = {
        "source": os.path.basename(pcb_path),
        "outline": {"w": round(x1 - x0, 3), "h": round(y1 - y0, 3),
                    "origin_kicad": [x0, y0]},
        "thickness": thickness if thickness is not None else 1.6,
        "thickness_provenance": "extracted_kicad (may be bare laminate - "
                                "verify with calipers/coupon stair)",
        "mounting_holes": holes,
        "coordinate_note": "board-local (u,v) = KiCad (X-x0, Y-y0); "
                           "KiCad Y grows toward v-max",
    }
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "pcb_geometry.json"), "w") as f:
        json.dump(geom, f, indent=1)
    with open(os.path.join(out_dir, "component_geometry.json"), "w") as f:
        json.dump(comps, f, indent=1)
    print(f"outline {geom['outline']['w']} x {geom['outline']['h']} "
          f"thickness {geom['thickness']} | {len(comps)} components | "
          f"{len(holes)} mounting holes -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
