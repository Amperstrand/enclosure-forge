# Cross-project lessons (stage-tagged failure catalog)

Distilled from both targets' AGENTS.md corpora + session learnings.
Origins: [L] = lilygo-a7670-simhat-carrier (rule #s refer to its AGENTS.md),
[N] = nucula-enclosure, [S] = session-level (publish/infra).
Project-specific detail lives in each target's own AGENTS.md; this file
keeps only what generalizes. Stage tags: M=measure, O=orient,
E=envelope, P=parameters, B=build, V=validate, R=render, PR=print,
X=meta/process.

## M — Measure
1. Measure first, model second; provenance tag every number [L1]. STEP
   slab thickness can be bare laminate, not finished board — coupon stair
   is the arbiter [L26].
2. DXF DIMENSION defpoints are callout anchors, not hole centers; when a
   feature must FIT a hole, measure centers off placed solids [L36].
3. A cylinder scan finds only round holes; mid-slab cross-section
   innerWires is the complete hole inventory [L25].
4. Fused single-solid STEP boards are normal — slab sweeps, z-plane
   clustering, cylinder enumeration, island maps recover the structure
   [L11].
5. Board-rev drift is real: pin the rev; connector/hole changes force
   re-extraction before any print [S, N].

## O — Orient
6. Device orientation comes from the board repo's docs/photos, not
   geometric convenience. A portrait window with all booleans green is
   still wrong [S/N: the nucula screen bug].
7. A 180° flip mirrors X, not just Y: (x,y,z)→(−x,y,−z); after ANY board
   reorientation, re-derive free windows — never carry zone tables
   across a flip [L5, L18]. A mirrored placement is not a real placement:
   mirror the FIXTURE, keep board transforms pure translations [L19].

## E — Envelopes
8. Keep-out scans vs ALL component solids, not top-N [L6].
9. Auto-derive connector mating envelopes from measured parts near edges
   (TurboCase pattern); hand-type only what solids can't know. Gate above
   PCB plane when boards mount component-up; map through orientation
   transforms [L39, L44].
10. Removal is staged kinematics with component sweep volumes; tilt is
    usually wrong when a long board overhangs a tall part [L7]. Edge-flush
    parts sweep through fence windows within reach — margin on BOTH sides
    or no bite [L40].
11. Antenna keepouts are 3D law: nothing metal above/behind the coil;
    thin-wall the reading path; prefer elimination-by-envelope probes
    over modeling-and-failing candidate placements [nucula NFC rules,
    L43].
12. Intended-contact volumes must be computed in the check's own terms —
    whichever solid the boolean intersects is whose thickness the
    allowance uses [L41].

## P — Parameters
13. One parameters.py, provenance-tagged, measured values loaded from
    analysis JSONs; no magic numbers in builders [N2, L/P-contract].
14. Metadata lists driving builds AND cuts need a kind tag [L10].
15. Ecosystem standards (Gridfinity) beat ad-hoc fixtures when they exist;
    adopt-a-library criteria: spec fidelity provable, dependency audited,
    replaces >100 lines [L16, L21].

## B — Build
16. One geometry source of truth: coupons/variants/sections consume the
    same builder functions as production [L8, N5].
17. When OCC fillets fail on fused prisms, move the feature into the 2D
    profile (prints better anyway) [L9].
18. `Workplane.rect()` centers on origin [N6]; capsule/cylinder direction
    must be end−start (reversed once produced phantom 200 mm³) [N6].
19. Floating cantilevers need print-support pedestals (0.3 below the
    underside, parameter-gated); prove printability with a slice-overlap
    lint (two-slab lookback, bridge-sheet classification) [L23, L24].
20. Screwless patterns: christmas-tree snap plugs (fins above PCB plane
    keep seated checks clean) [L37]; snap arms XY-plane flexures, PETG.

## V — Validate
21. Boolean volume overlap vs real reference geometry is THE pass gate;
    bbox-distance checks are advisory (false alarms AND false comfort)
    [L3].
22. Derive placement transforms from the plane that CONTACTS the support
    feature [L4]. Photo/luminance audits are theater on black PCBs;
    boolean truth from solids [L34].
23. Intended contacts are subtracted and NAMED; plane-at-face
    intersections equal the intended contact features by arithmetic [L38].
24. Deterministic rebuild (hash-identical STL) catches environment drift
    [N3].
25. A "no honest source passes" audit result means ship the honest
    fallback and record the decision — never game the gate [L46].

## R — Render
26. Renders are never evidence; close-ups must resolve the feature under
    test or the check is theater [L22, N4].
27. Semantic properties (aspect, opening size) get artifact-level proofs
    on the exported STL (section loops, occupancy probes) [S: window bug
    aftermath].
28. Placeholder stand-ins load from the exports dir where the builder
    writes them; STL loaders need error callbacks or a 404 becomes a
    5-minute silent hang [N6-trap].
29. Photo textures: perspective-rectify before mapping; U-mirror when
    baking onto down-facing planes; plane rectangles recomputed from
    PLACED solids; audits close the loop numerically [L30-33, L45].

## PR — Print
30. Calibration coupon before any large print [L20]; fold caliper truth
    back into parameters (thickness stair is the arbiter) [L26].
31. Print feedback is a first-class input: snap plugs that don't hold get
    demoted to a variant default change; rattles tighten end play [L42].
32. Fit-check with drop-over gauge pins when under-board parts exceed
    pocket depth; pin Ø follows the MODELLED drill [L15].

## PR2 — External peripherals (2026-10-10, nucula V4)
37. The intended peripheral is part of the measurement: board docs name
    it (nucula keyboard-interface.md cites the Adafruit 3845 arrangement
    on J3) — read them before designing its mounting.
38. Official datasheet dims beat gated 3D models: every download path for
    the exact keypad STEP is login-walled (printables CF+account, GrabCAD
    401 API, thangs/tinkercad/3dsearch). Build the stand-in from the
    official outline ONLY, tag the key grid conservative, disclose
    everywhere, and keep bay dims independent of stand-in cosmetics.
39. A peripheral wider than the board forces a zone flare: derive the
    flare from peripheral outline + service margins (not aesthetics), use
    vertical seam faces only, and re-run the full validation matrix on the
    flared variant.
40. Flush panel-mount cutouts die on interior tall parts: bottom-zone
    vertical spans are bounded by edge connectors (USB) and service
    headers + pigtails — probe the span budget before choosing recess
    depth; an exterior bay with its own podium is the fallback that
    never touches the cavity.

## X — Meta/process
33. Generated assets (renders) deploy via CI to Pages, not git; audits
    run in the pipeline; orphan-branch deploys from a job dir [L47].
34. Remote build box pattern: rsync (exclude-aware), frozen venv, visible
    multiplexer panes with anchored completion markers [S].
35. Vendor reference geometry with provenance (upstream commits
    recorded); pip-audit every dependency; keep the set minimal [L13,
    lilygo README].
36. A methodology that reproduces across two measurement front-ends is a
    framework; each new target must cross-apply rules and sync lessons
    back here [S].

## Landscape update (2026-10-10, second scan — agentic CAD + self-improving eng agents)

- ModelRift CadQuery-vs-OpenSCAD agentic benchmark (2026-09): 6 unattended
  runs, independent mesh verification. Verdict that validates our gate:
  "every defect that would have ruined a print was found by a number,
  not a screenshot"; neither tool's self-report is the last word (OCCT
  union silently dropped a solid with valid=True; caught only by volume).
  CadQuery wins on verifiability (query the kernel + assert), which is
  exactly our validate.py pattern.
- AnalogAgent (ACM 2026): self-improving analog-circuit agents with a
  self-evolving memory ("Adaptive Design Playbook") — curated, deduped,
  retrieved per task. Our lessons.md + run manifests are that playbook;
  adopt the retrieval step when the corpus grows.
- CADSmith / ai-cad: multi-agent CadQuery loops with kernel-measurement
  validators and regression-gated repairs; ai-cad runs keyless through
  the claude CLI's own auth — the same pattern as our OpenCodeLM pipe.
- Verdict: the pieces exist (agentic CadQuery loops, self-improving
  engineering agents, keyless CLI harnesses); nobody combines
  board-repo -> validated enclosure with boolean gates against extracted
  reference geometry + cross-project lesson distillation + dspy
  compilation. The niche holds. Borrow: playbook retrieval (AnalogAgent),
  numeric-gates-over-vision (ModelRift), regression-gated repairs (ai-cad).

## M — Measure (2026-10-10 evening, harness runs)
41. KiCad 10 renamed gr_line/gr_arc to bare line/arc, and boards may
    draw the outline INSIDE a footprint (board-frame-footprint trick):
    collect Edge.Cuts from both levels, transformed through placements
    (easyduino extractor fix).
42. Module height rules matter: WROOM defaulting to the 1.0 passive
    class silently under-sizes interiors (3.2 real).
43. LM-chosen parameters can pass the gate with a WEAK envelope
    (USB_REACH 2.0 mm covering no connector) — gate quality is itself a
    regression class; veto: envelope reach must cover the connector
    face + minimum plug body.
44. Local validation of small cases is a sub-10-minute class — the
    build box is a convenience, not a dependency.
45. A loft between two rects is a SOLID BLOCK, not a ring: the V5
    chamfered shoulder ran through the keyboard-section cavity (4 red
    checks, U8 345 mm3) until the interior was subtracted. Lofts need
    explicit cavity cuts — same class as "a mirrored placement is not a
    placement".
46. Product polish is a geometry class with its own checks: raised
    presentation (bay depth), chamfered transitions (sloped loft with
    cavity cut), vertical-edge-only radii (top rounding hurts FDM).
    Re-run the full matrix after any of them (V5: 80/80).
47. Fusing WIDER walls silently re-closes every opening cut into the
    slim profile: antenna windows, USB, battery slots (V6 lost 678.8 +
    8.7 mm3 to this). Re-assert all wall-piercings after any
    wall-widening fuse; the boolean gate catches them by volume.
48. Silhouette count is a design metric: uniform slab (1) reads as
    product; stacked steps (3+) reads as hobbyist. Flushness is
    artifact-provable (bbox zmax == face plane).
49. reference_stl front-end: when no board files exist but a human
    case does, measure the reference STLs (cavity sections = board
    envelope; aperture = rim) and tag derived_reference_stl. Target #7
    went boardless this way.
50. Tall sandwiches (>=5mm stacks) cannot slide under PCB-style edge
    lips - they ARE the edge. Full-height guide rails + lid-frame clamp
    is the correct retention class (and matches the human snapcase).
51. Stage A/B graders need headroom: an orientation grader that all
    arms pass on family-similar boards measures nothing - held-out
    diversity is a grader property, not just a trainset property.
