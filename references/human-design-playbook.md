# Human Enclosure Playbook — How Makers Actually Design 3D-Printed Cases for DIY Boards

Research notes from studying three hand-designed enclosure ecosystems (2026-10-11).
Method: cloned repos, read every enclosure README/assembly doc, ran geometric
analysis on every STL (bbox, bed-contact %, normal-area histogram, down-facing
area above the bed = bridge/shelf proxy), unpacked the shipped 3MF files to read
the embedded PrusaSlicer configs, extracted the PDF assembly instructions, and
reviewed assembly photos.

**Repos studied** (note: `BitcoinDiscoverer/Bitcoin-Discoverer` does not exist on
GitHub — substituted `zynthian/zynthian-case`, a multi-material, multi-panel
design line that contrasts with the snap-fit pill designs):

| Repo | Enclosure locations |
|---|---|
| cryptoadvance/specter-diy | `docs/enclosures/{snapcase,seedsigner,thomas}/`, `shield/3d_case/` (photos of the original), `shield/Alternative_3D_Printed_Case/` (STLs + `Assembly_Instructions.pdf`) |
| SeedSigner/SeedSigner | `enclosures/{orange_pill, simple_pill, open_pill, open_pill_mini, open_pill_mini_w_coverplate, orange_pill_mini, rugged_pill, look_screws_pill, pushcase}/` — 9 designs, one evolution tree |
| zynthian/zynthian-case | `3D Print - Big/` (14 printed parts), plus Aluminum/Lasercut/Steel variants of the same concept |

Relevance to this firmware repo: specter-diy encloses the **same
STM32F469I-DISCO devkit** our F469 CCID firmware runs on (plus a shield board
and a Waveshare QR scanner) — the closest published analogue to a
reader + devkit enclosure.

---

## 1. Design-by-Design Findings

Geometry numbers below are measured from the STLs (bed contact = % of total
surface area lying in the Z-min plane; "shelves" = down-facing area ≥0.5 mm
above the bed, i.e. what would need supports or self-supporting angles).

### 1.1 Specter-DIY Snap Case — `specter-diy/docs/enclosures/snapcase/`

Designer: @kayth21. Three parts: `Frontside.stl`, `Backside.stl`, `Scanner.stl`.

| Property | Finding |
|---|---|
| Board retention | Mixed: the Waveshare scanner is **screwed into `Scanner.stl` with the two screws scavenged from the scanner's own housing** ("Remove all screws from the scanner … Use the two small screws to lock the scanner"). The STM32F469I-DISCO + display are **friction/sandwich retained** — no screws for the boards at all. Case halves close with **printed snap hooks** ("Because of the snaps, you need a little pressure"). |
| Ports/openings | Per-feature cutouts + one deliberate **open edge**: cable routing is *designed geometry* — the scanner part has **channels the camera/FPC cables slide through** on the way to the header. No gaskets anywhere. |
| Screen | Printed bezel: front part is a shallow (10.2 mm) frame whose large rounded aperture forms the bezel around the display glass. Bare glass, no window/lens. |
| Part count | 3 prints, 2 reused screws. Why 3: the scanner needs its own sub-enclosure because it lives on the *back* and needs cable strain management; front/back split because a one-piece wrap can't capture the board sandwich. |
| Print orientation | All three flat, support-free by construction: Backside 64.4×131.4×16 mm with 30% of surface on the bed, **0.0 cm² of down-facing shelves**; Frontside 10.2 mm tall, 14% bed, 0.3 cm² shelves; Scanner 31% bed, 5.2 cm² (3%) shelves (the scanner pocket floor). |
| Assembly order (from README + geometry) | Print all → strip scanner screws → screw scanner into scanner part → place scanner part on board, **route cables through the printed channels**, connect to header → plug front onto back over the display. I.e. *peripheral modules first, shells last*. |
| 3 distinctive decisions | (1) Reusing the donor module's own screws instead of specifying new fasteners. (2) Printed **cable channels** as first-class geometry. (3) Explicit **hardware-revision coupling disclaimer**: "well tested with a Prusa MK3s and Specter hardware components from late 2022 … other hardware may produce results that do not fit" — friction fits are calibrated to a specific printer + board rev, and the README says so. |

### 1.2 Specter-DIY "Alternative" printed case — `specter-diy/shield/Alternative_3D_Printed_Case/`

Six numbered parts + `Assembly_Instructions.pdf` (fasteners: 4×6 mm, 2×8 mm,
2×10 mm M3 flatheads).

| Property | Finding |
|---|---|
| Board retention | **Screws + standoffs, but the standoffs come from the devkit kits themselves**: the instructions have you *replace* the DISCO board's 12 mm nylon spacers with the shield kit's 12.7 mm spacers, then screw through the enclosure into the board stack. The main body additionally captures the board by **flex-fit sliding** ("slightly flex the main enclosure body … sliding in at an angle at first may help") with a headphone-jack cutout as the locating feature. |
| Ports/openings | Per-port cutouts: headphone-jack cutout in the main body doubles as the assembly alignment key; USB/edges handled by leaving the board's connector edge open. Two **separate 2 mm rear panels** instead of one, purely so each can be removed independently (top panel = camera/service access, bottom = battery). |
| Screen | The main body is a 26 mm-tall open frame (side faces dominate the surface histogram; only 8% bed contact — printed **standing, open side down**); the display window is the frame's front aperture. `02_Top_Panel.stl` / `03_Bottom_Panel.stl` are dead-flat 2 mm plates (44–46% bed contact) — the flattest parts in the whole study. |
| Part count | 6 prints (`01_Main_Body` … `06_Spacer`) + 8 M3 screws. Why: serviceability — camera (`04_Camera_Holder`), power button (`05_Button`), and panel spacing (`06_Spacer`, 60.5×8×3.5 mm rib) are independent replaceables. |
| Print orientation | Body printed standing (walls vertical, support-free frame); panels printed flat; camera holder tiny (21.5×15×16, 56 triangles — box with a hole). Zero meaningful bridges anywhere. |
| Assembly order (from the PDF) | Button into body → board stack slides in at an angle (jack cutout engages) → 4×6 mm screws lock body to devkit → **unscrew the 4 nylon screws again** to expose the rear → camera module popped out of the shield and re-seated in `04_Camera_Holder` → stabilizer+camera re-seated in shield → `06_Spacer` → top panel with 2×10 mm → bottom panel with 2×8 mm. Cosmetic shells go on **dead last**. |
| 3 distinctive decisions | (1) The **camera stabilizer**: a printed collar that re-mounts the stock camera module to kill ribbon-cable flop, replacing the shield's own friction cutout. (2) **Two rear panels instead of one** so the camera/service zone opens without exposing the battery zone. (3) An assembly flow that requires **partially disassembling the donor kit mid-build** (spacer swap, camera re-seat) — the enclosure is designed as a *modification* of the devkit's existing mechanical system, not a wrapper around it. |

### 1.3 Specter-DIY "Barebones" v1 → v2 — `specter-diy/docs/enclosures/seedsigner/`

SeedSigner's own enclosure for the Specter hardware. `BBv1_{Upper,Lower}.stl` →
`BBv2_{Upper,Lower}.stl`.

| Property | Finding |
|---|---|
| Board retention | Classic **standoff sandwich**: M2.5 hardware (4×10 mm F-F spacers, 4×6 mm + 4×12 mm screws — same bill of materials as the SeedSigner pills, see below), shells screwed together through the board stack. |
| Ports/openings | Per-port cutouts; v2's headline change per `docs/enclosures/README.md` is "smaller form factor & **MicroSD access**" — v1 90×170 mm, v2 65.4×167 mm (measured). SD access was a *revision driver*, not an afterthought. |
| Screen | Bezel aperture in the 7 mm-thin upper shell. |
| Part count | 2. Uppers are 7 mm, lowers 15 mm. |
| Print orientation | Both revisions flat and clean: 25–31% bed contact, ≤0.2 cm² shelves — the v1→v2 rework kept the support-free property. |
| Assembly order | Standoffs to lower board, stack, upper on, screws. |
| 3 distinctive decisions | (1) The **v1→v2 diff itself**: width cut by 27% to fix a comfort complaint — humans re-cut the whole shell for grip feel. (2) Shipping both revisions in-tree so users on old hardware revisions can still print the match. (3) Sold as a physical product by the same person (bitcoin-store / btc-hardware-solutions links) — the design doubles as a small-batch product, which pushes toward fewer parts + no adhesive. |

### 1.4 SeedSigner evolution tree — `SeedSigner/enclosures/*`

Nine designs with explicit lineage in the READMEs. Every README carries the
same characteristic table (port accessible? SD removable? secondary hardware?
comfortable controls?) — the design *arguments* are published per design.

**Orange Pill** (`orange_pill/`) — the first, "eye-catching", 2 FDM shells
(`OP_Lower` 100×34.5×22, `OP_Upper` 100×34.5×12.5) + SLA-resin button/joystick.
M2.5 standoff sandwich (4×10 mm F-F spacers, 4×6, 4×12 mm screws). Measured:
15–17% bed contact, **0.0 cm² shelves** — support-free. Design files are
Fusion 360 (`.f3d` for all four parts). Weaknesses the later designs fix:
thumbstick clumsy, SD swap "requires partial disassembly".

**Simple Pill** (`simple_pill/`, @blackcoffeebtc) — adds the **DPAD thumbstick
topper** and **first easy SD access**; same fastener BOM. Note the export
hygiene trap: `sp_upper.stl` ships in *CAD* orientation (mesh floats at
zmin=10.4 mm, only 2% bed contact, 16% down-facing area) while `sp_lower.stl`
is print-ready — the user must know to flip the upper. A `protective_case/`
sleeve (2 more parts) is an add-on product. `sp_dpad.stl` likewise ships
floating (zmin=0.16).

**Open Pill** (`open_pill/`) — the deflationary counter-reaction: **one single
printed part, zero secondary hardware, friction fit** (79.5×34.5×26 mm, 12%
bed contact, 0.6 cm² shelves). Trade: "comfortable controls? No" — cured by a
community hack: **screw an M2.5 DIN-466 knurled nut onto the bare joystick
stem, which self-taps a thread into the plastic**. Fusion file:
`design_file/open_pill.f3d`.

**Open Pill Mini w/ Coverplate** (`open_pill_mini_w_coverplate/`) — chassis +
lid + buttons + PLA-or-TPU thumbstick (two thumbstick files, material A/B).
The README's first: "**preventing access to the SeedSigner's data-enabled USB
port as an additional security assurance**" — the port is *closed on purpose*.

**Orange Pill Mini** (`orange_pill_mini/`) — snap-fit top/bottom, hardware-free,
ZeroCam for compactness; ships `OrangePillMini_Bottom.3mf` **pre-oriented and
multicolor-ready** (5 separate mesh volumes inside the 3MF = MMU color splits,
15 227 vertices). README: "Files are preoriented for optimal printing, no
supports required"; TPU 95A recommended for buttons/thumbstick/trackball.
"Data port is closed."

**Rugged Pill** (`rugged_pill/`) — snap-fit, screws-free; geometry reveals the
boldest orientation call in the study: `RuggedPill_Top.stl` and `_Bottom.stl`
are 73.8×11.3×34.8 / 73.8×16.2×34.8 mm — the pills are exported **standing on
their long edge** (only 6–7% bed contact, 8–9% down-facing area = the rounded
shell arches, which are self-supporting overhangs at ≤45°). Printing the pill
on its side also puts the snap cantilevers **in the XY layer plane**, where
FDM snaps are strong, instead of stacked along Z where they delaminate. Ships
single-color STLs + `Multimaterial/RuggedPill_{Top,Bottom}_MMU.3mf`, and a
`RuggedPillBottom_4SeedHammer.stl` variant whose only difference is the **port
door opened** for a companion device.

**Look Screws Pill** (`look_screws_pill/`) — motivation, verbatim: "Faceplate
screws could look cool." Fasteners as *aesthetic*: 4×10 mm M2.5 risers + 8×10 mm
screws, all visible from the top. Includes `pressPad.stl` in mandatory TPU
whose cavity is **deliberately undersized** for the Waveshare HAT's stub nub —
"Do NOT PANIC! It's done on purpose to create friction" — an interference fit
documented as such. `ButtonsConnected.stl` = three caps on one sprue.

**Push Case** (`pushcase/`, @kayth21) — the most engineered: 5 prints
(`Top`, `Middle`, `Bottom`, `Button`, **`Soldering Support - Push Case -
SeedSigner.stl`** — a manufacturing *jig*, not a case part). Requires a Pi
Zero **without** presoldered header + 40× 6 mm pins; you solder the stack
*inside the printed jig* (display face-down on the jig, middle frame, Pi
face-down, insert pins with tweezers, solder). Zero screws — press-fit
sandwich ("prints must be accurate in order to fit tightly"). Ships
pre-oriented `.3mf` with full PrusaSlicer config embedded: **`support_material
= 0`**, Prusament PLA, layer 0.15 mm (first 0.15; a height range sets 4
perimeters / 5 bottom / 6 top solid layers on the fine zone), brim 0.
Assembly README even specifies "hold the device upside down so that the
buttons do not fall out" and a camera-alignment-by-tool step before pressing
the back on. Known-issue section documents a **Bambu Studio slicing bug on
the buttons** and the workaround ("use Prusa Slicer").

**Cross-cutting SeedSigner evidence:**
- 3MFs embedded config, all designs: `support_material = 0`, PLA, layer
  heights 0.15–0.25 mm, 2–3 perimeters, brim 0 → **support-free printing is
  the hard constraint**, verified by the shipped slice, not just claimed.
- Ports: the characteristic tables track "Data-enabled USB accessible?" and
  the lineage *trends toward "No"* (open_pill yes → coverplate/rugged/orange
  mini/pushcase no, with an explicit variant file to re-open it). Port state
  is a **security posture decision**, not a mechanical necessity.
- Controls: consistent two-material doctrine — PLA (or PETG) shells, TPU 95A
  (or SLA resin, in the earliest designs) buttons — and spare control parts
  ("print both [thumbstick and trackball], test which you like best").

### 1.5 Zynthian "3D Print - Big" — `zynthian-case/3D Print - Big/`

Desktop-synth enclosure (RPi + Zynscreen + knobs + joysticks), 14 printed
files: `Top Front/Back`, `Bottom Front/Back`, `Top Cover`, `Underside`,
`Left/Right Side`, `Foot L/R`, `Knob`, `Button`, `Rpi SUPPORT`, plus a
`FullAssembly.stl` reference. Same concept exists in `Aluminum - */`,
`Lasercut - */`, `Steel - PiTFT28/` — **one design expressed in four fab
processes**. Credits in `README.md` name four individual designers across
print/metal/laser/wood.

| Property | Finding |
|---|---|
| Board retention | **Screws everywhere**: panels carry screw-hole grids; the top panel's screen cutout is ringed with mounting holes + nut pockets so the display mounts from underneath (`Rpi SUPPORT.stl` is a dedicated printed bracket for the Pi). `Foot L/R` raise the base off the table. |
| Ports/openings | Panel-and-hole strategy: every connector gets its own through-hole (USB slots, encoder shafts, jack clusters, an 11-slot vent grille on the side panel). No gaskets; openings are holes in flat panels. |
| Screen | Through-cutout in the top panel with corner nut pockets — the display is *clamped under* the aperture. No window, no bezel insert. |
| Part count | 14. Why: fabrication limits and serviceability — panels are each smaller than the printer bed (biggest: `Top Cover` 138×156 mm), and any panel can be reprinted after a connector change. `FullAssembly.stl` documents the target stack. |
| Print orientation | STLs ship in **assembly orientation** (`Top Cover` mesh floats at zmin=34.6 with 45% down-facing area — obviously not a print pose); `Underside.stl` is coincidentally print-ready (2.5 mm plate, 42% bed). Orientation decisions are delegated to the maker — the opposite philosophy of the SeedSigner 3MFs. |
| Assembly order (from geometry: perimeter hole grids + panel overlap) | Frame panels (sides into top/bottom front+back rails) → internals on their supports (Pi bracket, screen under top-panel cutout) → `Top Cover` on → underside + feet last. |
| 3 distinctive decisions | (1) `FullAssembly.stl` — the **assembled state shipped as a printable artifact** so builders can inspect fit before printing 14 parts. (2) `Rpi SUPPORT` — a board-specific **mid-frame bracket** printed as part of the set. (3) The **multi-process fork family**: the printed case, the aluminum case, the lasercut case and the steel case coexist in one repo with shared dimensions — panelization chosen so the design survives a fab-method upgrade. |

---

## 2. Distilled Table

| Design | Retention | Ports | Screen | Parts (prints + HW) | Print pose (evidence) | Assembly order |
|---|---|---|---|---|---|---|
| Specter Snap Case | scanner: 2 reused self-screws; boards: friction sandwich; halves: printed snaps | per-port cutouts + designed cable channels; open board edge | printed bezel aperture, bare glass | 3 + 2 reused screws | all flat; 14–31% bed, ≤0.3 cm² shelves | scanner→screws→cables through channels→snap shells |
| Specter Alternative | M3 screws into kit standoffs (12→12.7 mm swap) + flex-slide capture | headphone-jack cutout = alignment key; two independent rear panels | tall open frame aperture | 6 + 8 M3 + kit spacers | body standing (8% bed, side walls vertical); panels flat 2 mm | button→board slides in→screws→camera stabilizer→top panel→bottom panel |
| Specter BB v1→v2 | M2.5 standoff sandwich | per-port cutouts; v2 = 27% narrower + SD access | bezel in 7 mm upper | 2 + 12 M2.5 | flat, 25–31% bed, ~0 shelves | standoffs→stack→screw |
| SeedSigner Orange Pill | M2.5 standoff sandwich | per-port; SD needs disassembly | bezel | 2 FDM + 2 SLA + 12 M2.5 | flat, 15–17% bed, 0 shelves | standoffs→stack→screw |
| SeedSigner Open Pill | pure friction, zero hardware | open (data port accessible) | bezel | **1 + 0** | flat, 12% bed, ~0 shelves | fold board in, snap |
| SS Open Pill Mini w/ Coverplate | friction + lid | **data port deliberately blocked** | bezel under lid | 4 + 0 (TPU/PLA thumbstick variants) | flat, ~0 shelves | stack→buttons→lid |
| SS Orange Pill Mini | snap-fit top/bottom | data port blocked | bezel | 2 shells + 3 TPU controls | ships **pre-oriented 3MF**, MMU-split (5 volumes), supports=0 | board→bottom→snap top |
| SS Rugged Pill | snap-fit | blocked, with `_4SeedHammer` variant to reopen | bezel | 2 + 3 TPU controls (+MMU 3MFs) | **printed on its side** (6–7% bed; snaps in XY plane; shell arches self-support) | board→bottom→snap top |
| SS Look Screws Pill | screws *as aesthetic* (8 visible) + friction pressPad | open | bezel | 4 (3-on-sprue buttons + pressPad) + 12 M2.5 | flat, 12–31% bed | risers→board→buttons→top |
| SS Push Case | press-fit sandwich, zero screws | blocked (HDMI too) | recessed pocket + raised lip formed by the face | 4 + 1 **solder jig** + 40 pins | ships pre-oriented 3MF, supports=0, 0.15 mm layers, 4-perimeter fine zone | jig→solder header→camera→back on (align camera)→buttons in (upside down)→front→thumbstick |
| Zynthian Big | screws + nut pockets + printed Pi bracket | per-connector holes in flat panels + vent grille | top-panel through-cutout, display under-mounted | 14 + screws (+ FullAssembly.stl) | STLs in assembly orientation — user reorients | panels→internals on brackets→cover→underside→feet |

---

## 3. What Human Designs Do That Naive Generators Don't

1. **Ports are a security/product decision, not a mechanical one.** The
   SeedSigner lineage *converges on closing the data USB port* (and even HDMI),
   shipping a differently-named variant STL (`RuggedPillBottom_4SeedHammer.stl`)
   for the one use case that needs it open. A naive generator cuts a hole for
   every connector the board has; humans delete ports on purpose and version
   the exception.

2. **Support-free geometry is a hard constraint, proven by shipped slice
   config.** Every published 3MF has `support_material = 0`; measured
   down-facing area above the bed is ~0 cm² for the flat-printed designs. The
   Rugged Pill goes as far as printing the whole device **on its side** so
   snap cantilevers lay in the XY plane (strong) instead of along Z
   (delamination) while the rounded shell acts as its own 45° support. Naive
   pipelines orient for minimum height or maximum bed contact; humans orient
   for **layer direction at the snap features**.

3. **Friction is calibrated and documented, including its failure modes.**
   "The prints are quite tight… check that the prints do not exert pressure on
   any hardware components" (snapcase); "DO NOT PANIC! It's done on purpose to
   create friction" (look_screws pressPad undersize); "prints must be accurate
   in order to fit tightly without screws… in worst case damage the hardware"
   (pushcase). Humans treat interference fits as *tuned parameters tied to a
   printer + board revision*, and they publish the calibration envelope
   (Prusa MK3S + late-2022 specter parts; MK3S + early-2024 hardware).

4. **Fastener ecosystems are reused, not invented.** Scavenging the scanner's
   own screws; swapping the devkit's 12 mm nylon spacers for the shield kit's
   12.7 mm ones mid-assembly; the identical M2.5 BOM (4×10 F-F, 4×6, 4×12)
   across Orange/Simple/BB designs so one hardware order builds any of them.
   Generators specify abstract "4× M3×8"; humans anchor to fasteners the user
   already owns or can buy once.

5. **The print set includes manufacturing jigs.** Push Case ships
   `Soldering Support - Push Case - SeedSigner.stl` — a fixture that holds the
   display + Pi Zero stack while you solder the 40-pin header. The enclosure
   kit is treated as *tooling for assembling the product*, not just the
   product's skin.

6. **Cable and camera management is first-class geometry.** Printed cable
   channels (snapcase Scanner part), a camera *stabilizer* collar that
   re-mounts the stock camera to kill ribbon flop (Specter Alternative), and
   an assembly step where the camera is aligned by tool inside its printed
   holder *before* the back is pressed on (pushcase). Naive enclosures cut a
   camera hole and let the cable do whatever.

7. **Part count follows philosophy, and the lineage *minimizes* it.**
   Orange Pill (2 shells + 12 fasteners + resin controls) → Open Pill
   (1 part, 0 hardware) → snap-fit minis (2 shells, 0 hardware) → Push Case
   (4 + jig, 0 screws). The BOM is a design axis with published tradeoff
   tables (SD removable? port accessible? comfortable controls?). When humans
   add parts (Specter Alternative's 6, Zynthian's 14), each part buys
   *independent serviceability* (separate rear panels, per-connector panels
   reprintable after a connector change).

8. **Screen treatment is always "bare glass + printed bezel geometry" —
   never a window, never a gasket.** Recessed pocket with a raised lip formed
   by the face itself (pushcase — the recess also seats the display
   mechanically), rounded-corner apertures sized to hide the display's edges
   (Specter 3d_case photos), or a through-cutout with nut pockets for
   under-mounting (zynthian). Nobody in this study prints a transparent
   window or designs a lens gasket — the display *is* the window.

9. **Buttons are separate, material-split parts with printed travel
   geometry.** TPU 95A caps (or SLA resin in early designs) riding through
   shaped openings, sometimes three caps on one sprue (`ButtonsConnected.stl`),
   with A/B variants (thumbstick vs trackball, PLA vs TPU) shipped for the
   user to *choose feel*. Naive generators emboss the shell.

10. **They publish orientation + slice settings inside the artifact.**
    Pre-oriented 3MFs with embedded PrusaSlicer configs (layer 0.15, supports
    off, perimeters 2–4, zone-specific solid layers), MMU color-split volumes
    in the same file, and even slicer-bug workarounds in the README ("Bambu
    Studio drops layers on the buttons — use PrusaSlicer"). The deliverable is
    a *print job*, not a mesh. (Zynthian's assembly-orientation STLs are the
    counter-example that proves the point — the modern designs moved away
    from it.)

11. **Hardware-revision coupling is explicit.** Enclosures are calibrated to
    board revisions ("Specter hardware from late 2022", "Pi Zero without
    pre-soldered GPIO pins required"), old revisions stay in-tree
    (`BBv1` + `BBv2` both shipped), and READMEs warn that newer/older donor
    hardware may not fit. A generator assumes the board model; humans version
    the *donor kit*.

12. **Community lineage compounds.** Look-Screws' README: "built on top of
    giants (@gobrrrme and @blackcoffee)". Designs fork, inherit chassis
    geometry, and re-work one axis (aesthetic screws, a DPAD topper, a
    knurled-nut thumbstick hack standardized as DIN 466). The knowledge that
    survives is *what to change next* — SD access, port blocking, thumb
    comfort — visible as a clean revision chain across nine READMEs.

### The one-line summary

A naive generator wraps a board in a box with holes; the humans in these repos
design **an assembly process** — jigs, cable channels, calibrated friction,
scavenged fasteners, snap layers oriented for strength, deliberately deleted
ports — and the enclosure is merely the artifact that process ships in.
