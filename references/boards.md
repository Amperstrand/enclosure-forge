# Target gallery

Completed enclosures produced by this pipeline. Each target repo owns its
project-specific traps (its AGENTS.md); this file records what each
target PROVED about the method.

## lilygo-a7670-simhat-carrier (target #1) — STEP/DXF front-end
https://github.com/Amperstrand/lilygo-a7670-simhat-carrier
- Dual-board carrier (T-A7670X modem + T-SimHat relay hat), snap-cage
  for a hole-less board, screw mount for the other, antenna side tray
  chosen by elimination probes, Gridfinity fit-check, photo-baked
  textured renders audited in CI, v0.3 physical print feedback folded in.
- Proved: boolean gate as design review across 47 documented lessons;
  photobake audit loop; renders-to-Pages CI; the coupon-first print loop
  under real hardware constraints (battery holders exceeding pocket
  depth).

## nucula-enclosure (target #2) — KiCad front-end
https://github.com/Amperstrand/nucula-enclosure
- Enclosure family V0–V3 for the Nucula NFC board (ESP32-C3 + NFC coil
  + OLED + breakaway keyboard section): pop-out screen window, no-metal
  construction, battery-under-board wire routing, 57-check validation.
- Proved: the method ports to the KiCad front-end unchanged
  (parameters → builders → boolean gate); snap-fit lids replace screws
  when holes are antenna-adjacent; the orient stage (P3) exists because
  its screen window shipped portrait with every boolean green; board-rev
  drift (connector swap) surfaced here and became P11.

## rp2040-devboard-enclosure (target #3) — first harness run
https://github.com/Amperstrand/rp2040-devboard-enclosure
- Minimal dev-board case (square 53.34 board, 4×M2.5 bosses from measured
  holes, micro-USB opening, dual header exit reliefs, friction lid), 7/7
  checks, built end-to-end by the harness v0 in operator/record mode.
- Proved: the generic KiCad front-end (cross-validated on nucula's own
  numbers), the stage-trace format, the metric plumbing, and the debug
  loop as data (two iterations, both root-caused by arithmetic, recorded
  in the target's stages/*.json).

## The next target
Clone whichever scaffold is closest (STEP/DXF → carrier repo; KiCad →
nucula repo), execute SKILL.md stages S0–S9, log the run manifest, and
sync generalizable lessons back here. Target #3 is the trigger to
automate `experiments/`.
