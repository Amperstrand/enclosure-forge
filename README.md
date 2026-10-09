# enclosure-forge

An AI-assisted (agentic) framework for going from a **board design file**
(manufacturer STEP/DXF or a KiCad project) to a **validated, printable
enclosure/carrier** — with a set of prompts, gates, and lessons instead of
hand-run rituals.

Two completed targets prove the pipeline end-to-end:

| Target | Front-end | Result |
|---|---|---|
| [`lilygo-a7670-simhat-carrier`](https://github.com/Amperstrand/lilygo-a7670-simhat-carrier) | manufacturer STEP/DXF | dual-board carrier, 35+28 boolean checks in CI, printed (v0.3 feedback folded in), photo-baked renders on Pages |
| [`nucula-enclosure`](https://github.com/Amperstrand/nucula-enclosure) | KiCad `.kicad_pcb` | OLED/keyboard enclosure family V0–V3, 57 boolean checks in CI |

Both target repos keep **only their own project-specific traps** in their
AGENTS.md; the general method lives here.

## How to consume

1. **As an OpenCode/agent skill**: clone this repo into your skills
   directory (e.g. `~/.agents/skills/enclosure-forge/`). `SKILL.md` is the
   entry point; it routes each stage to the reference files.
2. **As pure context**: hand an agent `SKILL.md` +
   `references/prompts.md` and let it execute stage by stage; the prompts
   are self-contained and copy-paste runnable.
3. **As a checklist**: each stage has an explicit exit gate. A stage
   without a green gate is not done — including "the renders look fine".

## Pipeline in one breath

```
board repo (rev pinned) ─► measure (STEP/DXF | KiCad) ─► analysis/*.json
  ─► orient (device semantics from board docs, NOT convenience)
  ─► envelopes (keep-outs, mating, removal kinematics)
  ─► parameters.py (provenance-tagged) ─► builders + coupon
  ─► boolean validation gate ─► honest renders + artifact proofs
  ─► coupon print ─► fold measurements back ─► lessons upstream (here)
```

The pass gate is always the same: **zero unexpected common volume against
the real reference geometry, machine-readably reported.** Renders are
never evidence; booleans decide, renders explain.

## Repository layout

```
SKILL.md                  the skill body: stages, gates, routing
references/prompts.md     the prompt library (P1..P12), stage-keyed
references/lessons.md     cross-project failure catalog, stage-tagged
references/validation.md  the boolean gate doctrine + check taxonomy
references/toolchain.md   cadquery/OCC/playwright/CI environment traps
references/frontends.md   measurement front-ends: STEP/DXF vs KiCad
references/boards.md      target gallery + what each target proved
experiments/              prompt-set A/B harness (manifest + eval schema;
                          dspy-based optimizer is the planned evolution)
templates/                parameters/validate/build/render scaffolds
```

## Improvement loop (why `experiments/` exists)

Every enclosure run produces machine-readable evidence
(`analysis/interference_report.json`, iteration counts, timings). The
intended loop:

1. Log each run as an `experiments/runs/*.json` manifest (see
   `experiments/eval-schema.json`).
2. A/B prompt-set variants on the same board; compare
   *iterations-to-green*, *final failure count*, *wall time*, and
   eventually *physical print outcome*.
3. Promote winning prompt edits back into `references/prompts.md` with a
   changelog line — the library is versioned data, not prose.
4. Planned: drive the same loop with [dspy](https://dspy.ai) — prompt
   stages as signed modules, validation reports as the metric signal for
   a teleprompter-style optimizer. Two targets is a corpus, not a
   statistic; the harness comes first, the optimizer second.

## Status

v0 — corpus of 2 targets, prompt library battle-tested across both,
A/B harness specified but not yet automated. A third target is the
trigger to harden `experiments/` into the automated loop.
