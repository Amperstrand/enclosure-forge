"""Scaffold: boolean validation harness (enclosure-forge S6).

Contract: zero unexpected common volume against real reference solids;
INTENDED contacts subtracted and NAMED; report to
analysis/interference_report.json; exit code = pass gate (CI runs this).
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPORT = []


def check(name, ok, value, expect, note=""):
    REPORT.append({"name": name, "pass": bool(ok), "value": value,
                   "expect": expect, "note": note})
    print(f"  {'PASS' if ok else 'FAIL'} {name} {value} {note}")


def vol(solid) -> float:
    return solid.Volume() if solid is not None else 0.0


def inter(a, b) -> float:
    """Common volume of two solids; 0.0 on None/disjoint."""
    if a is None or b is None:
        return 0.0
    c = a.intersect(b)
    return vol(c)


def intended_contacts():
    """Named solids that ARE allowed to touch (lips, pads, fins).

    Returned as {name: solid}; seated checks subtract these before
    asserting zero. A check that cannot name its contacts is not a check.
    """
    return {}  # e.g. {"retention_lip": shell_libretention_lip_solid()}


def main() -> int:
    # from cad import reference as R, shell as S
    # board = R.board_solid()
    # shell = S.bottom_shell()
    # intended = S.fuse_all(list(intended_contacts().values()))
    # unexpected = vol(inter(board, shell.cut(intended)))
    # check("seated_board_interference", unexpected < 0.5, unexpected, "<0.5 mm3")
    # ... component_clearance (ALL solids), envelopes, antenna zones,
    #     kinematics stages, solids_valid, deterministic rebuild (STL hash)
    out = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "analysis", "interference_report.json")
    with open(out, "w") as f:
        json.dump(REPORT, f, indent=1)
    failed = sum(1 for r in REPORT if not r["pass"])
    print(f"\n{len(REPORT)} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
