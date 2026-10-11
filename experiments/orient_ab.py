#!/usr/bin/env python3
"""dspy experiment #1: few-shot vs zero-shot Orient on a held-out board.

Train demos: recorded traces (rp2040 operator, easyesp32/easyesp32s3 LM).
Held out: easyduino-pico. Graded deterministically against known pico
facts: micro-USB at the v=0 edge; 4 mounting holes (boss class);
portrait stick. Output: experiments/runs/orient-ab-result.json
"""

import json
import os
import sys

import dspy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.lm_opencode import OpenCodeLM  # noqa: E402
from harness.signatures import Orient  # noqa: E402

T = "~/src/enclosure-forge/traces/lm"
DEMO_SOURCES = [
    ("~/src/rp2040-devboard-enclosure/stages/02-orient.json",
     "orientation_convention"),
    (f"{T}/easyesp32-s2-orient-lm.json", "orientation_convention"),
    (f"{T}/easyesp32s3-s2-orient-lm.json", "orientation_convention"),
]

PICO_CTX = (
    "Board: Easyduino Pi Pico 2040 (RP2040 Pico-format stick). Outline "
    "21.0 x 51.0 x 1.6mm. 4 mounting holes at (3.99,48.7) (3.99,2.3) "
    "(17.39,2.3) (16.59,48.7) — note the slanted-end hole offset at "
    "u 16.59. USB micro-B J1 at u 5.86..15.5 on the v=0 edge "
    "(v 1.4..7.72). Three 8.5mm castellated headers mid-board. "
    "Dev board, no display."
)

GRADES = {
    "usb_v0": ("usb", "v=0", "v-min", "bottom edge", "one short edge",
               "v = 0", "bottom"),
    "retention_holes": ("4 mounting holes", "mounting holes", "boss",
                        "four holes", "m2", "holes at"),
    "portrait": ("portrait", "stick", "long axis", "vertical"),
}


def grade(text: str) -> dict:
    t = text.lower()
    return {k: any(s.lower() in t for s in syms)
            for k, syms in GRADES.items()}


def main():
    demos = []
    for path, field in DEMO_SOURCES:
        d = json.load(open(os.path.expanduser(path)))
        ctx_key = "board_context"
        demos.append(dspy.Example(
            board_context={
                "~/src/rp2040-devboard-enclosure/stages/02-orient.json":
                    "Square 53.34 RP2040 board, USB micro-B J1 at v=0 edge, "
                    "dual 2x18 headers on both u edges, 4 M2.5 holes",
                f"{T}/easyesp32-s2-orient-lm.json":
                    "Easyduino ESP32 28.4x47.9 stick, USB-C at v-max edge, "
                    "no mounting holes, WROOM module",
                f"{T}/easyesp32s3-s2-orient-lm.json":
                    "Easyduino ESP32-S3 25.9x63.9 stick, dual USB-C at "
                    "v-max, no mounting holes",
            }[path],
            orientation_convention=d[field],
            user_facing_features=d.get("user_facing_features", ""),
        ).with_inputs("board_context"))

    results = {}
    dspy.configure(lm=OpenCodeLM(timeout=700, tries=1))

    zero = dspy.ChainOfThought(Orient)
    r0 = zero(board_context=PICO_CTX)
    results["zeroshot"] = {"text": r0.orientation_convention[:1200],
                           **grade(r0.orientation_convention)}

    few = dspy.ChainOfThought(Orient)
    few.demos = demos
    r1 = few(board_context=PICO_CTX)
    results["fewshot"] = {"text": r1.orientation_convention[:1200],
                          **grade(r1.orientation_convention)}

    zero_shot_ref = json.load(open(os.path.expanduser(
        f"{T}/easypico-s2-orient-lm.json")))["orientation_convention"]
    results["zeroshot_recorded"] = grade(zero_shot_ref)

    out = os.path.expanduser(
        "~/src/enclosure-forge/experiments/runs/orient-ab-result.json")
    json.dump(results, open(out, "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items()
                          if kk in GRADES}
                      for k, v in results.items()}, indent=1))
    print("WROTE", out)


main()
