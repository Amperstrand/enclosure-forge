#!/usr/bin/env python3
"""Operator-in-the-loop runner for the first-iteration harness.

Usage (record mode — today's default):
  python3 harness/run_board.py --board <board_repo> --out <enclosure_repo> \
      --record traces/<id>.jsonl

Stages:
  S1 deterministic: kicad_extract (auto)
  S2..S5 judgment:  the runner prints each stage signature prompt; the
                    operator writes stages/<NN>-<name>.json in the
                    enclosure repo; every ingest is appended to the
                    trace JSONL (bootstrap-ready for BootstrapFewShot).
  S6 deterministic: build + validate (invoked separately per iteration;
                    each run appends a metric event to the trace).

Once an LM is configured (dspy.configure(lm=...)), the same stages run
via program.BoardToCase and the trace records itself.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def append_trace(path, event):
    event["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")


def stage_prompt(name, sig_doc, fields):
    print(f"\n=== STAGE {name} ===")
    print(sig_doc.strip())
    for role, fs in fields.items():
        print(f"{role}:")
        for fname, desc in fs:
            print(f"  - {fname}: {desc}")
    print("Write your answer as JSON to stages/ and re-run.\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("--validate", action="store_true",
                    help="run S6 build+validate in the out repo and "
                         "record the metric event")
    args = ap.parse_args()

    stages_dir = os.path.join(args.out, "stages")
    os.makedirs(stages_dir, exist_ok=True)

    if args.validate:
        for script in ("scripts/build.py", "scripts/validate.py"):
            r = subprocess.run(
                [sys.executable, os.path.join(args.out, script)],
                capture_output=True, text=True)
            tail = (r.stdout + r.stderr).strip().splitlines()[-6:]
            for line in tail:
                print("  |", line)
            append_trace(args.record, {
                "stage": "S6_validate", "script": script,
                "returncode": r.returncode, "tail": tail})
            if r.returncode != 0 and "validate" in script:
                return r.returncode
        return 0

    # S1: deterministic extraction
    pcb = None
    for dirpath, _dirs, files in os.walk(args.board):
        for fn in files:
            if fn.endswith(".kicad_pcb"):
                pcb = os.path.join(dirpath, fn)
                break
        if pcb:
            break
    if not pcb:
        print("no .kicad_pcb under", args.board)
        return 1
    out_analysis = os.path.join(args.out, "analysis")
    r = subprocess.run(
        [sys.executable",
         os.path.join(ROOT, "harness", "frontends", "kicad_extract.py"),
         pcb, out_analysis], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    append_trace(args.record, {"stage": "S1_extract", "pcb": pcb,
                               "output": (r.stdout + r.stderr).strip()})

    # S2..S4: print the signature prompts (operator answers into stages/)
    from harness.signatures import Envelopes, Orient, Parameters
    for n, sig in (("S2_orient", Orient), ("S3_envelopes", Envelopes),
                   ("S4_parameters", Parameters)):
        fields = {}
        for name, field in sig.fields.items():
            role = "input" if field.json_schema_extra.get(
                "input") else "output"
            fields.setdefault(role, []).append(
                (name, (field.json_schema_extra.get("desc") or "")[:120]))
        stage_prompt(n, sig.__doc__ or "", fields)
    print("After answering all stages, iterate S6 with --validate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
