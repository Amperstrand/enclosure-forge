# enclosure-forge — status 2026-10-11

One-page snapshot of everything built and what it proved. Read this
first when resuming; the details live in the referenced files.

## The corpus (7 validated targets + 1 retrofitted)

| # | Target | Front-end | Checks | Score | What it proved |
|---|---|---|---|---|---|
| 1 | lilygo-a7670-simhat-carrier | STEP/DXF | 63 | (legacy schema) | the method works; 47 lessons distilled; physical print feedback folded in |
| 2 | nucula-enclosure | KiCad | **104** | 0.80 | deep design: NFC law, OLED pop-out, breakaway section, payment terminal (V4/V5/V6), config matrix, Pages configurator; the portrait-window regression → P3 |
| 3 | rp2040-devboard-enclosure | KiCad | 7 | 1.00 | first harness-built target; **first fully-LM-mode board** (S2/S3/S4 via OpenCodeLM) |
| 4 | easyduino-esp32-enclosure | KiCad | 7 | 0.85 | first zero-hole board → pad-and-rail retention class |
| 5 | easyduino-esp32s3-enclosure | KiCad | 7 | 1.00 | template reuse: **zero debug iterations** |
| 6 | easyduino-pico-enclosure | KiCad | 7 | 1.00 | template reuse: **zero debug iterations**; authentic slanted-end hole |
| 7 | specter-diy-case | **reference_stl** (NEW) | 7 | 0.80 | **reproduction milestone**: measured from the human snapcase STLs, matches/beats on every static metric; cable channels added (v2) |

## The harness

```
harness/
  frontends/kicad_extract.py   generic KiCad 6-10 extractor
                               (bare line/arc, footprint outlines, heights)
  signatures.py                4 DSPy signatures (Orient, Envelopes,
                               Parameters, DebugPatch) — the optimizable
                               contract
  program.py                   BoardToCase(dspy.Module) — composes stages
  metric.py                    boolean-gate score + speed + semantic veto
  recorder.py                  (trace recorder; record mode IS trainset
                               generation)
  run_board.py                 operator-in-the-loop CLI driver
  lm_opencode.py               OpenCodeLM: dspy inference piped through
                               `opencode run` (no API key needed)
  render_best.py               GLB assembly + PNG views; --no-pcb toggle
  blender/nucula_hero.py       photoreal Blender scene (explode+orbit,
                               GPU Cycles, resumable chunks)
  blender/orbit_probe.py       4-azimuth centroid proof (camera centering)
```

## The prompt library (17 prompts)

| Prompt | What it does | Origin |
|---|---|---|
| P1-P2 | measurement (STEP/DXF, KiCad) | target #1 |
| P3 | orient: derive device semantics from board docs | portrait-window bug |
| P4 | fastener truth from measured holes | target #1 |
| P5 | keep-out scan + mating + removal kinematics | targets #1-#2 |
| P6 | coupon shares production builders | target #1 |
| P7 | validate matrix (boolean gate) | targets #1-#2 |
| P8 | render honest + artifact-proof | portrait-window bug |
| P9 | print fold-back | target #1 |
| P10 | lessons sync | ongoing |
| P11 | board-rev drift check | nucula J2 PH→SH |
| P12 | remote build box pattern | ai-legion |
| P13 | peripheral bay (flush elimination) | nucula V4 keypad |
| P14 | readme refresh (from machine truth only) | target #3 |
| P15 | render best (GLB + PNGs + links) | target #3 |
| P16 | silhouette-class polish (count the steps) | nucula V5/V6 |
| P17 | config-matrix modularity | nucula config system |

## The lessons (51)

Distilled in `references/lessons.md`, tagged by stage. The load-bearing
ones for the next session:
- **3** boolean volume = the pass gate
- **6** device orientation from board docs, not convenience
- **41** KiCad 10 dialects + footprint outlines
- **47** wall-widening re-closes piercings
- **50** tall sandwiches need guide rails, not edge lips
- **51** A/B graders need held-out diversity

## The dspy experiments (2 run, both honest)

| Experiment | Result | Reading |
|---|---|---|
| Orient A/B #1 (pico held-out) | 3/3 both arms pass | ceiling effect: family-similar boards can't discriminate (lesson 51) |
| Orient A/B #2 (nucula held-out) | 3/4 both arms tie | the P3 instructions carry the portrait fix; NFC grader needs recalibration |

**Status: prompts are already good enough that the simple A/B can't
separate arms.** The next dspy experiment needs either harder boards or
optimization of the debug loop (where iteration counts actually vary).

## The human-design playbook

`references/human-design-playbook.md` (300 lines): specter-diy (3 case
lines), SeedSigner (9 designs, one tree), zynthian-case (14 parts).
Measured bed-contact, shelf area, silhouette regimes, part count,
assembly order. The distinctive human decisions our pipeline doesn't
yet produce: donor-hardware reuse, cable channels as geometry (t7 v2
closes this), service zoning, mid-build donor disassembly, hardware-rev
disclaimers.

## The benchmark

`experiments/benchmark.py` — deterministic, LM-free. Per repo: forge
score + silhouette regimes (cross-section based) + bed-contact % +
shelf area. Baseline: `experiments/benchmark-baseline.json`. First
catch: the V5 phantom chamfer (the loft was there but the bands ran
full-height).

## What is deliberately NOT done yet

- **Physical prints**: zero across all 7 targets. The V0 coupon for
  nucula is the first gate; specter-diy t7 needs one too.
- **dspy compilation**: 2 A/B experiments is not a trainset. The pipe
  is stage-grade (60-800s/call); BootstrapFewShot needs a real key or
  a local model. The traces accumulate either way.
- **The STEP/DXF front-end** is not in the harness (lilygo used the
  pre-harness scripts). A target with only manufacturer CAD would
  exercise a different extraction path.
- **The reproduction gap**: t7 matches the human on static metrics but
  lacks snap hooks, scanner sub-enclosure (v2 has the tray but not the
  back-mount), and the hardware-rev disclaimer pattern.
