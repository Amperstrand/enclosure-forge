"""Scaffold: render + artifact-proof loop (enclosure-forge S7).

Contract: renders illustrate (full + resolvable close-ups); semantic
properties are PROVEN on the exported STL via plane-section loops, not
by looking at pictures. Every loader gets an error callback; waits fail
fast on LOAD_ERROR.
"""

from __future__ import annotations


def section_loops(stl_path: str, z: float):
    """Closed cross-section loops at plane z: [(area, u0, v0, u1, v1)].

    Frame-invariant deltas (width/height) of the opening loop must match
    the parameter-derived rect — that is the artifact-level proof.
    """
    import numpy as np
    import trimesh

    mesh = trimesh.load(stl_path)
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    planar, _ = sec.to_2D()
    loops = []
    for loop in planar.discrete:
        pts = np.asarray(loop)
        x, y = pts[:, 0], pts[:, 1]
        area = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
        loops.append((area, x.min(), y.min(), x.max(), y.max()))
    return sorted(loops, reverse=True)
