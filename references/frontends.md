# Measurement front-ends: STEP/DXF vs KiCad

Same output contract (`analysis/*.json`: board slab, outline, holes,
component solids/zones, rule areas, provenance), two input worlds.

## Manufacturer STEP + DXF (target: lilygo carrier)
- Boards arrive as fused single solids: recover structure via
  cross-section area sweeps (slab), planar-face clustering (z-planes),
  cylinder enumeration filtered to the outline bbox (holes — beware
  corner-fillet masquerades), island maps at several z (components).
- DXF `DIMENSION` values cross-check STEP cylinders; defpoints are NOT
  centers (see lessons M2). DXF lacks slots/ovals → the mid-slab
  innerWires pass still applies to the STEP.
- Product-page photos are primary reference material for parts STEP
  omits (relay model, wire-entry direction, silkscreen rev); download
  full width, vision on downscales misreads part numbers.

## KiCad `.kicad_pcb` (target: nucula enclosure)
- Parse s-expressions directly: Edge.Cuts stitch (arcs!), footprint
  pads/courtyards, `ruleareas` verbatim (the board designer's antenna
  law), board thickness, NPTH/mouse-bites, breakaway topology via
  point-in-polygon on Edge.Cuts.
- Mind KiCad's Y-down + footprint rotation/mirror conventions when
  mapping to board-local (u,v); document the transform once, in the
  extractor.
- The board repo's `docs/` (breakaway geometry, connector selection,
  orientation corrections) is part of the measurement: connectors get
  SWAPPED between revs — P11 (drift check) exists for this.
- Re-extraction needs the hardware repo (`NUCULA_REPO=…`); commit the
  extracted JSONs so validate/build run without it.

## Choosing / mixing
Both targets ended with identical downstream architecture
(parameters → builders → boolean gate) — the front-end is a swappable
S1 module. When both sources exist, extract BOTH and cross-check hole
diameters/outline; when they disagree, take the tighter for fits and
record the delta.
