# Prompt library (P1..P12)

Stage-keyed, copy-paste runnable, battle-tested across two targets
(lilygo STEP/DXF, nucula KiCad). Prompts are versioned data: when an A/B
run (see `experiments/`) proves an edit, change it here and add a
changelog line at the bottom.

Conventions: `analysis/*.json` = machine-extracted board geometry;
"boolean check" = common-volume test against real reference solids;
"provenance tag" = the five classes from SKILL S4.

---

**P1 — measure-step** *(S1, STEP/DXF front-end)*
> Clone the vendor repo; find STEP/DXF under dimensions/. Enumerate the
> PCB slab (cross-section sweeps), outline, holes (cylinders within one
> radius of the outline bbox — corner fillets masquerade as big holes),
> and component solids into `analysis/*.json`. ALSO take a mid-slab
> cross-section and enumerate innerWires — that is the complete hole
> inventory (slots/ovals evade cylinder filters). Cross-check hole
> diameters between DXF dims and STEP cylinders; report deltas, take the
> tighter for fastener sizing. Do not model anything yet.

**P2 — measure-kicad** *(S1, KiCad front-end)*
> Parse the `.kicad_pcb` s-expression: Edge.Cuts stitch → outline, tabs,
> notches, breakaway gaps; `(general (thickness))`; footprint pads +
> courtyard → component bboxes; PCB rule areas verbatim (antenna keepouts
> are the board designer's own law). Record the KiCad-origin→board-local
> transform. Every extracted number gets provenance
> `extracted_kicad`/`derived_kicad`. Do not model anything yet.

**P3 — orient** *(S2, device semantics — run before cutting ANY user-facing feature)*
> From the board repo's docs/photos (not from geometric convenience):
> how is the device held? Which end is up? Where do connectors mate from,
> what direction do cables exit, which way does the display read, which
> face does the user see? Write the orientation convention with a
> citation (doc path or photo), then map every user-facing feature
> (windows, button ports, port openings, labels) through it. If a
> connector's mating direction is ambiguous from solids alone, pull the
> manufacturer drawing before assuming.

**P4 — fastener-truth** *(S1/S4)*
> From the measured hole diameters (placement measured off placed solids,
> never off DXF dimension callout anchors — defpoints sit off-center),
> derive the correct metric screw size; refuse to default to M2/M3.
> Report the self-tap pilot diameter for the actual print material.

**P5 — keep-out-scan + mating + removal** *(S3)*
> Given component solids: (a) compute every ≥N-mm window of bare laminate
> in the AS-ORIENTED frame; verify support candidates against ALL solids,
> not top-N (~80 components on a hat-class PCB). (b) Auto-derive side/end
> exit mating envelopes for every measured part near a board edge (±
> orientation mapping); hand-type envelopes only for what solids cannot
> know (plug bodies, swap sweeps). (c) Write staged removal kinematics
> (release → lift δ → slide s → lift clear) and boolean-test each stage
> INCLUDING component sweep volumes; re-run after ANY layout shift —
> compressed layouts re-collide features that were fine at full size.

**P6 — coupon-shares-builders** *(S5/S8)*
> Extract the exact production geometry into a calibration coupon that
> calls the same builder functions (lip bay, slits, hole ladder,
> thickness stairs, one real clip bay at production profile/flip).
> Validate the coupon itself: enumerate its feature radii/voids from the
> model, and boolean-seat the reference board in its bay.

**P7 — validate-matrix** *(S6)*
> Build the check suite: seated interference (INTENDED contacts subtracted
> and named), component clearance vs ALL solids, connector envelopes,
> antenna keepouts, watertight/positive volume, deterministic rebuild
> (hash-identical STL), feature presence. All variants in one run. Zero
> unexpected mm³ is the only pass criterion — bbox-distance checks are
> advisory. Write `analysis/interference_report.json`; CI runs this.

**P8 — render-honest + artifact-proof** *(S7)*
> Render full + per-feature close-ups (zoom until the feature is
> resolvable; whole-model scale checks are theater). Then prove the
> semantic property under change on the EXPORTED STL: plane-section the
> deck band, list the closed loops with areas+bboxes, and show the
> opening's size/aspect/position match the parameters. Report both the
> renders (for humans) and the section numbers (for the record).

**P9 — print-fold-back** *(S8)*
> Print order: coupon → fit-check → production. After each print, fold
> measurements into parameters (thickness stair arbiter wins over model
> numbers; a ~0.05 mm interference in a hook slot reads as "perfectly
> firm" — model the measured value, keep clearances explicit), re-run the
> full validation matrix, and record what the coupon decided in a
> machine-readable testing-status file.

**P10 — lessons-sync** *(S9)*
> Diff what failed vs what the docs claimed. Append new failure modes to
> the target repo's AGENTS.md (project-specific traps) and the
> generalizable ones to enclosure-forge `references/lessons.md`. Delete
> rules that no longer apply. Log the run manifest in `experiments/runs/`.

**P11 — board-rev-drift** *(S0/S1, before any physical print)*
> Compare the board repo's current rev against the rev the enclosure's
> `analysis/*.json` were extracted from. If connectors, mounting holes,
> or outlines moved: re-extract, re-derive the affected envelope set
> (wire routes die on connector swaps), and re-run the matrix before
> printing. Record the drift in MEASUREMENTS_NEEDED-class docs.

**P12 — remote-build-box** *(meta: heavy compute)*
> When validation/rendering exceeds the local machine, rsync the repo
> (exclude .git/.venv/__pycache__; remember exclude-protects-delete on
> __pycache__), create the venv from the frozen requirements on the box,
> and drive commands through a visible terminal multiplexer pane with
> anchored completion markers (`echo DONE_$?` + regex `^DONE_[0-9]+$` —
> bare markers false-match the echoed command line).

## Changelog

- 2026-10-09: P3 (orient) and P11 (board-rev drift) added after the
  nucula portrait-window bug (all booleans green, screen semantically
  rotated) and the J2 PH→SH connector drift discovery. P8 gained the
  artifact-proof clause for the same reason.
