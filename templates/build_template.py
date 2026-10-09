"""Scaffold: builder/exporter (enclosure-forge S5).

Contract: builders consume parameters only (no magic numbers); the
calibration coupon calls the SAME builder functions; exports land in
output/exports (STEP+STL); STL hashing feeds the determinism check.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "output", "exports")


def export(name: str, solid) -> None:
    w = cq.Workplane(obj=solid)
    cq.exporters.export(w, os.path.join(OUT, name + ".step"))
    cq.exporters.export(w, os.path.join(OUT, name + ".stl"),
                        exportType="STL", tolerance=0.05, angularTolerance=0.2)
    bb = solid.BoundingBox()
    print(f"{name:24s} vol {solid.Volume():9.1f} mm^3  "
          f"bbox {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
