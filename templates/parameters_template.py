"""Scaffold: parameter module contract (enclosure-forge S4).

Every dimension lives here, each tagged with a provenance class:
extracted_* / derived_* / manufacturer_doc / conservative_assumption /
enclosure_design_decision. Measured values LOAD from analysis/*.json —
the only literals are design decisions. Builders import nothing else.
"""

from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    with open(os.path.join(ROOT, "analysis", name)) as f:
        return json.load(f)


GEOM = _load("pcb_geometry.json")     # outline, slab, holes (P1/P2 output)
COMPS = _load("component_geometry.json")

# measured (extracted_kicad / extracted_step) -------------------------------
BOARD_W = GEOM["outline"]["w"]
BOARD_T = GEOM["thickness"]

# design decisions (enclosure_design_decision) ------------------------------
WALL_T = 1.6            # shell wall
PCB_SUPPORT_H = 1.8     # board seat height

# conservative assumptions (conservative_assumption) ------------------------
COMP_DEFAULT_H = 1.0    # generic passives <= 1.0; validator re-checks


def comp_height(ref: str) -> float:
    """Component height with per-ref overrides; validator re-checks all."""
    return {"J1": 3.31}.get(ref, COMP_DEFAULT_H)


def derived() -> dict:
    """Computed quantities (single source); builders consume D, not math."""
    d = {
        "lid_int_z": PCB_SUPPORT_H + BOARD_T + comp_height("J2"),
        # ... envelope/keepout zones from GEOM/COMPS
    }
    return d


D = derived()
