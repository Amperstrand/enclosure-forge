#!/usr/bin/env python3
"""Fleet benchmark: quality metrics for enclosure repos (enclosure-forge).

Per repo: forge score (boolean gate) + STATIC DESIGN METRICS computed
from the exported STLs with trimesh — no LM, fully deterministic:

  silhouette_steps : count of >1mm jumps in the outer width profile
                     along z (P16: 1 = uniform product, 3+ = hobbyist)
  bed_contact_pct  : % of surface area lying in the z-min plane
                     (print orientation quality; playbook metric)
  shelf_area_cm2   : down-facing area >=0.5mm above the bed
                     (support burden; playbook metric)

Usage: python3 experiments/benchmark.py   (from the forge root)
"""

from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.metric import score_report  # noqa: E402

REPOS = {
    "nucula-V6-slab": ("~/src/nucula-enclosure",
                       "V6_bottom_shell_slab.stl", 3),
    "nucula-V5-terminal": ("~/src/nucula-enclosure",
                           "V4_bottom_shell_terminal.stl", 3),
    "rp2040": ("~/src/rp2040-devboard-enclosure", "bottom_shell.stl", 1),
    "easyduino-esp32": ("~/src/easyduino-esp32-enclosure",
                        "bottom_shell.stl", 2),
    "easyduino-esp32s3": ("~/src/easyduino-esp32s3-enclosure",
                          "bottom_shell.stl", 1),
    "easyduino-pico": ("~/src/easyduino-pico-enclosure",
                       "bottom_shell.stl", 1),
}


def static_metrics(stl_path: str) -> dict:
    m = trimesh.load(stl_path)
    z = m.vertices[:, 2]
    zmin = z.min()

    # silhouette regimes: distinct outer-width clusters (1.5mm bins) of
    # cross-SECTIONS at 1mm z-steps (vertex bands miss wall mid-spans;
    # sections capture the full profile). 1 = uniform product silhouette.
    widths = []
    for z0 in np.arange(max(zmin, 0.0), z.max(), 1.0):
        sec = m.section(plane_origin=[0, 0, z0], plane_normal=[0, 0, 1])
        if sec is None:
            continue
        pts = np.vstack([np.asarray(p) for p in sec.discrete])
        widths.append(round((pts[:, 0].max() - pts[:, 0].min()) / 1.5))
    from collections import Counter
    counts = Counter(widths)
    total = max(1, len(widths))
    steps = sum(1 for k, n in counts.items() if n / total >= 0.05)

    # face metrics: bed contact + shelves
    normals = m.face_normals
    centers = m.triangles_center
    areas = m.area_faces
    bed = (normals[:, 2] < -0.95) & (centers[:, 2] < zmin + 0.05)
    shelf = (normals[:, 2] < -0.95) & (centers[:, 2] > zmin + 0.5)
    return {
        "silhouette_regimes": steps,
        "bed_contact_pct": round(float(areas[bed].sum() / areas.sum() * 100), 1),
        "shelf_area_cm2": round(float(areas[shelf].sum() / 100.0), 2),
    }


def main():
    rows = []
    for name, (repo, part, iters) in REPOS.items():
        repo = os.path.expanduser(repo)
        report = os.path.join(repo, "analysis", "interference_report.json")
        hits = (sorted(glob.glob(os.path.join(repo, "output", "exports", part)))
                + sorted(glob.glob(os.path.join(repo, "exports", part))))
        row = {"repo": name}
        if os.path.exists(report):
            row.update(score_report(report, iters))
        else:
            row.update({"score": None, "passed": None, "total": None})
        if hits:
            row.update(static_metrics(hits[0]))
            row["stl"] = os.path.basename(hits[0])
        else:
            row.update({"silhouette_regimes": None, "bed_contact_pct": None,
                        "shelf_area_cm2": None, "stl": "MISSING"})
        rows.append(row)

    print(f"{'repo':22s} {'score':>6s} {'checks':>8s} {'reg':>4s} "
          f"{'bed%':>6s} {'shelf_cm2':>9s}")
    for r in rows:
        sc = r['score'] if r['score'] is not None else '-'
        ck = f"{r['passed']}/{r['total']}" if r['passed'] is not None else '-'
        rg = r.get('silhouette_regimes', '-')
        print(f"{r['repo']:22s} {sc:>6} {ck:>8s} {rg:>4} "
              f"{r.get('bed_contact_pct', '-'):>6} "
              f"{r.get('shelf_area_cm2', '-'):>9}")
    out = os.path.join(os.path.dirname(__file__), "benchmark-baseline.json")
    json.dump(rows, open(out, "w"), indent=1, default=str)
    print("\nbaseline ->", out)


if __name__ == "__main__":
    main()
