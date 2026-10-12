#!/usr/bin/env python3
"""dspy experiment #2: Orient A/B on an AMBIGUOUS board (nucula).

The portrait-window regression makes nucula the right held-out: display
+ keypad + NFC coil + USB on the long edge create real orientation
ambiguity. Ground truth = the operator-recorded convention (post-fix).
Grades discriminate: screen-above-keypad, USB long-edge, NFC opposite
the keypad, landscape screen.
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
     "Square 53.34 RP2040 board, USB micro-B at v=0 edge, dual 2x18 "
     "headers on both u edges, 4 M2.5 holes"),
    (f"{T}/easyesp32-s2-orient-lm.json",
     "Easyduino ESP32 28.4x47.9 stick, USB-C at v-max edge, no holes"),
    (f"{T}/easyesp32s3-s2-orient-lm.json",
     "Easyduino ESP32-S3 25.9x63.9 stick, dual USB-C at v-max, no holes"),
]

g = json.load(open(os.path.expanduser(
    "~/src/nucula-enclosure/analysis/pcb_geometry.json")))
c = json.load(open(os.path.expanduser(
    "~/src/nucula-enclosure/analysis/component_geometry.json")))
tall = "; ".join(f"{r}={v.get('footprint','?').split(':')[-1][:24]} h{v.get('height')}"
                 for r, v in list(c.items())[:8] if isinstance(v, dict))
NUCULA_CTX = (
    "Board: nucula (ESP32-C3 + NFC + OLED + detachable keyboard). "
    "Outline 60 x 110 x 1.6mm, portrait. OLED flex socket DS1 around "
    "u 21..39 v 54..62. USB micro-B J1 on the LONG u=0 edge around "
    "v 56..67. 40x40mm NFC coil at u 10..51 v 1..41. Detachable 3x4 "
    "keypad header J3 at the v-max end (v 105..110). Battery JST at "
    "v 46..55. Payment-terminal-class device. Components: " + tall
)

GRADES = {
    "screen_top_keypad_bottom": ("screen.*top", "display.*top",
                                 "keypad.*below", "keypad.*bottom",
                                 "keyboard.*bottom", "screen above"),
    "usb_long_edge": ("long edge", "u=0", "u-min", "left edge",
                      "side edge", "u = 0"),
    "nfc_away_from_keypad": ("nfc.*opposite", "coil.*away",
                             "nfc.*bottom.*keypad", "coil.*far",
                             "reading.*opposite", "coil at the",
                             "nfc at the"),
    "landscape_screen": ("landscape", "57.5", "wide"),
}


import re  # noqa: E402


def grade(text: str) -> dict:
    t = text.lower()
    out = {}
    for k, pats in GRADES.items():
        out[k] = any(re.search(p, t) for p in pats)
    return out


def main():
    demos = []
    for (path, ctx), (src, field) in zip(
            DEMO_SOURCES,
            [("rp", "orientation_convention"),
             ("e32", "orientation_convention"),
             ("e32s3", "orientation_convention")]):
        d = json.load(open(os.path.expanduser(path)))
        demos.append(dspy.Example(
            board_context=ctx,
            orientation_convention=d[field],
            user_facing_features=d.get("user_facing_features", ""),
        ).with_inputs("board_context"))

    dspy.configure(lm=OpenCodeLM(timeout=700, tries=1))
    results = {}

    zero = dspy.ChainOfThought(Orient)
    r0 = zero(board_context=NUCULA_CTX)
    results["zeroshot"] = {"text": r0.orientation_convention[:1500],
                           **grade(r0.orientation_convention)}

    few = dspy.ChainOfThought(Orient)
    few.demos = demos
    r1 = few(board_context=NUCULA_CTX)
    results["fewshot"] = {"text": r1.orientation_convention[:1500],
                          **grade(r1.orientation_convention)}

    out = os.path.expanduser(
        "~/src/enclosure-forge/experiments/runs/orient-ab2-nucula.json")
    json.dump(results, open(out, "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items()
                          if kk != "text"} for k, v in results.items()},
                     indent=1))
    print("WROTE", out)


main()
