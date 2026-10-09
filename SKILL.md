---
name: enclosure-forge
description: Design a 3D-printable enclosure or carrier for an electronics
  board from its design files (manufacturer STEP/DXF or KiCad project), with
  boolean-validated geometry, calibration coupons, and honest renders. Use
  when asked to design/model/iterate a case, enclosure, carrier, tray,
  holder, or housing for a PCB or dev board, or to extend/fix an existing
  enclosure built with this method.
---

# enclosure-forge — board file → validated enclosure

You are executing a staged pipeline. Two rules govern everything:

1. **No dimension is typed from memory.** Every geometric claim about the
   board comes from measured/parsed reference files, tagged with a
   provenance class. Design decisions are literals; measurements are not.
2. **The boolean gate is the design review.** A stage is done when its
   machine-readable check passes — zero unexpected common volume against
   real reference geometry. Renders illustrate; they never prove.

## Stages, gates, routing

Execute in order; a failed gate sends you back one stage, not forward.

### S0 — Intake
Acquire the board's design files (clone the repo / vendor the STEP/DXF).
**Pin the rev** (commit hash) and record it — board repos drift while
enclosures are being built. Check license/attribution for reference
geometry.
Gate: files exist locally; rev recorded in the run manifest.
→ `references/frontends.md` for choosing the measurement front-end.

### S1 — Measure
Run the appropriate extractor into `analysis/*.json` (geometry, holes,
components, rule areas). Cross-check hole diameters between sources when
two exist (DXF callouts vs STEP cylinders can disagree; take the tighter
for fastener fits, document the delta). Enumerate ALL holes via a
mid-slab cross-section (innerWires) — cylinder scans miss slots/ovals.
Gate: extraction regenerates byte-stable JSONs; provenance classes on
every number.
→ prompts P1–P2.

### S2 — Orient (device semantics)
Before placing ANY user-facing feature (screen window, button ports,
connector openings, label orientation), derive the **device orientation**
from the board repo's docs/photos: how is the device held, which end is
up, what does the user see? Boolean checks cannot catch a window that is
geometrically perfect but semantically rotated.
Gate: orientation convention written down with a board-repo citation
before the first user-facing feature is cut.
→ prompt P3. (This stage exists because of a real bug: a portrait OLED
window, all checks green, screen sideways.)

### S3 — Envelopes
Derive keep-outs and service envelopes from measured solids: component
clearance (ALL solids, not top-N), antenna rule areas, connector mating
envelopes (auto-derived from measured parts near board edges — never
hand-typed for parts the solids know), removal/install kinematics
(staged sweeps; components sweep volumes during removal).
Gate: envelope set covers every connector + antenna + battery + removal
path, each with a named check planned.
→ prompts P3–P5.

### S4 — Parameters
All dimensions in ONE `parameters.py`, each tagged
(`extracted_*` / `derived_*` / `manufacturer_doc` /
`conservative_assumption` / `enclosure_design_decision`); measured values
load from `analysis/*.json`. No magic numbers in builders.
Gate: `grep` finds no bare literals in shell/builders; provenance table
generates `docs/geometry_provenance.md`.
→ `templates/parameters_template.py`.

### S5 — Build
Shell builders consume parameters only. The calibration coupon calls the
SAME builder functions as production parts (a coupon validating stale
geometry is worse than none). Move fillets/chamfers into 2D profiles when
OCC fillets fail on fused prisms.
Gate: build regenerates hash-identical STLs (deterministic rebuild check).
→ `templates/build_template.py`, prompt P6.

### S6 — Validate
Boolean pass gate: zero unexpected common volume; INTENDED contacts
(lips, pads, plug fins) subtracted and NAMED. Include watertight/positive
volume, deterministic rebuild, feature-presence probes. Both build
profiles/variants in one run.
Gate: all checks PASS, report written to `analysis/interference_report.json`.
→ `references/validation.md`, prompt P7.

### S7 — Render + artifact proofs
Renders for humans: full views AND close-ups (zoom enough to resolve the
feature under test). Verification for machines: when a semantic property
matters (window aspect, opening size), prove it on the exported STL
(plane-section loop analysis, occupancy probes) — not by looking at
pictures.
Gate: per-render luminance/size sanity; artifact-level section proof for
the feature under change.
→ `references/toolchain.md` (render pipeline traps), prompt P8.

### S8 — Print loop
Coupon FIRST (hole ladder, thickness stairs, real feature bays at
production profile). Fold print feedback into parameters and re-run the
full validation matrix. Record what the coupon decided, in
`testing_status`-style machine-readable form.
Gate: coupon decision recorded; any parameter change re-validated.
→ prompt P9.

### S9 — Lessons sync
Diff what failed vs what the docs claimed. Append new failure modes to the
target repo's AGENTS.md (project-specific) and the generalizable ones to
`enclosure-forge/references/lessons.md` (this repo), then prune stale
rules. Log the run in `experiments/runs/`.
→ prompt P10.

## Failure mode you must not commit

Shipping a design change with green booleans but unverified semantics
(orientation, mating direction, handedness). If the board repo can answer
a semantic question, S2 answers it from there before any geometry is cut.
