"""Metric for the enclosure pipeline (enclosure-forge).

Hard signal comes from the deterministic boolean gate — no LLM judge:
  score = checks_passed_ratio * 0.7 + speed_term * 0.3
Speed term rewards few validate iterations (iterations_to_green).
Semantic-regression veto: any tripped veto class zeroes the score —
the optimizer must not learn to game the gate.

Costs: each evaluation runs real CAD booleans; run against the remote
build box and cache stage-identical re-evaluations (dspy-design.md).
"""

from __future__ import annotations

import json
import os

VETO_CLASSES = [
    # grow with every semantic bug caught; format: (class, detector)
    ("orientation_violation",
     "user-facing feature contradicts the recorded orientation "
     "convention citation"),
    ("intended_contact_unnamed",
     "check passes only by widening a gate or removing a named "
     "intended-contact subtraction"),
]


def score_report(report_path: str, iterations: int = 1,
                 semantic_failures: list[str] | None = None) -> dict:
    with open(report_path) as f:
        report = json.load(f)
    passed = sum(1 for r in report if r["pass"])
    total = max(1, len(report))
    speed = 1.0 / max(1, iterations)
    vetoed = bool(semantic_failures)
    score = 0.0 if vetoed else round(passed / total * 0.7 + speed * 0.3, 4)
    return {"score": score, "passed": passed, "total": total,
            "iterations": iterations,
            "semantic_failures": semantic_failures or [],
            "vetoed": vetoed}


def enclosure_metric(example, pred, trace=None) -> float:
    """dspy-compatible metric: expects pred.repo_dir with a validation
    report + run manifest (see experiments/eval-schema.json)."""
    repo = getattr(pred, "repo_dir", None)
    if not repo:
        return 0.0
    report = os.path.join(repo, "analysis", "interference_report.json")
    manifest = os.path.join(repo, "..", "run_manifest.json")
    iterations = 1
    if os.path.exists(manifest):
        iterations = json.load(open(manifest)).get(
            "metrics", {}).get("iterations_to_green", 1)
    if not os.path.exists(report):
        return 0.0
    sem = getattr(pred, "semantic_failures", None) or []
    return score_report(report, iterations, sem)["score"]


if __name__ == "__main__":
    import sys
    print(json.dumps(score_report(sys.argv[1],
                                  int(sys.argv[2]) if len(sys.argv) > 2 else 1),
                     indent=1))
