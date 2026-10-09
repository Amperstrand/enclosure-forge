# The boolean gate — doctrine and check taxonomy

## Doctrine

- The only pass criterion: **zero unexpected common volume** (mm³)
  between enclosure solids and real reference geometry (placed
  manufacturer STEP, or KiCad-derived board + component solids).
- Every check reports a machine-readable number (volume, bbox, count) to
  `analysis/interference_report.json`. CI runs the suite; a red check
  fails the build.
- INTENDED contacts (support pads on bare laminate, retention lips,
  snap-plug fins, wire-exit relief) are subtracted by NAME. A check that
  can't name its intended contacts isn't a check.
- Bbox-distance checks are advisory only: bbox granularity produces both
  false alarms (designed clearances flagged) and false comfort.

## Check taxonomy (grow with the design)

| Class | Examples | Criterion |
|---|---|---|
| Seated interference | board vs bottom, board vs lid | 0 mm³ after named contacts |
| Component clearance | every placed component vs both shells | 0 mm³, ALL solids |
| Mating envelopes | USB plug, SMA, side/end-exit housings, SIM swap | 0 mm³ inside envelope |
| Antenna law | NFC rule areas, ESP32 keepout, reading-path wall | ≤ NFC_WALL_T; no metal in zone |
| Battery | seat clear, swell allowance, wire route | 0 mm³ + explicit allowances |
| Kinematics | removal stages incl. component sweeps | 0 mm³ at every stage |
| Feature presence | window size/aspect, fin ring above board, tab-in-lip-band | geometric predicate on solids |
| Solid health | watertight, positive volume, per-part volume | boolean of the model itself |
| Determinism | rebuild → hash-identical STL | equal hashes |
| Artifact proof | STL plane-section loops: opening bbox/area/aspect | equals parameter-derived rect |

## Artifact-level proofs (for semantic properties)

When the property a human cares about (window aspect, opening position)
is not expressible as a volume check, prove it on the EXPORTED STL, not a
render: `mesh.section(plane at feature band)` → closed loops with shoelace
areas + bboxes. Frame-invariant deltas (width × height) match the
parameter-derived rect exactly when the artifact is right.

## Honest disclosure

Checks may PASS-WITH-DISCLOSURE (e.g. dielectric glass over an antenna
rule area) — the report names the disclosure and a MEASUREMENTS_NEEDED
item owns the physical verification. Never silently widen a gate to make
a number pass; when no honest source passes, ship the honest fallback and
record the decision.
