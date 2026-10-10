# DSPy design — compiling the enclosure pipeline

Researched 2026-10-10 (dspy docs/zread + production writeups + the
board-to-enclosure tool landscape). This file is the build plan for the
optimizer layer; `README.md` in this directory keeps the manual A/B loop
that runs until this lands.

## Why our pipeline is unusually DSPy-ready

DSPy's hardest problem is the metric — most users must invent an
LLM-as-judge. We already have an objective, machine-readable one:

- **Hard signal (no judge):** `analysis/interference_report.json` —
  checks passed, iterations-to-green, unexpected-volume values. Zero
  unexpected mm³ against real reference solids is binary and
  ground-truthed. (The swiftwand OpenSCAD experiment and the
  prompts-as-code paper both flag judge overfitting on code tasks;
  boolean volumes are immune.)
- **Trajectory signal:** iteration count, wall time, stage rework —
  metric-aware traces reward efficient pipelines, not just passing ones.
- **Veto signal:** semantic regressions (the portrait-window class:
  booleans green, device semantics wrong). Any candidate that trips a
  known regression class is rejected regardless of score — the optimizer
  must not learn to game the gate.

## Module decomposition

Stages become `dspy.Module`s; deterministic stages (extractors, validate,
build) are plain Python inside `forward()` — optimizers only tune the LM
calls. Signatures:

- `S1 PlanMeasure(frontend, board_context) -> extraction_plan` (which
  sources, which cross-checks, hole-inventory strategy)
- `S2 Orient(board_docs) -> orientation_convention + citation`
- `S3 Envelopes(analysis_json, orientation) -> keepout_plan,
  mating_envelope_decisions, removal_kinematics`
- `S4 Params(analysis_json, decisions) -> parameters.py` (provenance
  contract enforced by lint, not by the LM)
- `S5 DebugLoop(failed_checks, geometry_context) -> next_patch` —
  the validate→fix loop; the highest-value optimization target
- `S6..S8` mostly deterministic (build/validate/render) with small LM
  edges (close-up framing, artifact-proof selection)
- `S9 LessonsSync(session_diff) -> lesson edits` (upstream to this repo)

## Metric

```python
def enclosure_metric(example, pred, trace=None):
    report = run_validation(pred.repo_dir)          # deterministic
    checks = report.passed / report.total
    iters  = 1.0 / max(1, report.iterations)
    veto   = semantic_regressions(pred) == []       # orient-truth check
    score  = checks * 0.7 + iters * 0.3
    return (score if veto else 0.0, trace is not None)
```

Cost note: every candidate evaluation runs real CAD booleans (seconds on
a 20-core box, minutes locally). Mitigations: run compilation against
the remote build box; cache stage-identical re-evaluations; bootstrap
first (cheap), optimize instructions second.

## Optimizer ladder (in order)

1. **BootstrapFewShot** — run the manual pipeline on 3-5 new boards
   (trainset generation, below); successful stage traces become demos.
   Zero new infrastructure: manifests + transcripts already capture
   traces.
2. **SIMBA** on the two weakest stages (measured by stage rework rate —
   historically S3 envelopes and S5 debug loop). SIMBA is proven on
   tool-use agents (35% → 60% on ToolHop-style tasks, dspy tutorial).
3. **GEPA/MIPROv2** only if SIMBA stalls and we have ≥8 boards —
   reflective prompt evolution needs the data volume to justify it.

## Trainset: boards as data

Each new board run = one example (inputs: board repo + docs; outputs:
validated enclosure repo + manifest). Candidate boards (public KiCad,
diverse shapes/connectors/mounting):

- Hanqaqa/Easyduino (UNO/Nano/ESP32/Pico/Bluepill — 8+ boards, CERN-OHL)
- alpelectronix/RP2040-ESP32C3 (LCD + battery + µSD — feature-dense)
- TobleMiner/ESP32-Devkit-Type-C (devkit classic)
- PartialScience/Custom-RP2040-Dev-Board (minimal, has STEP + an
  enclosure to compare against)

Held-out testset: one board never used in compilation. Promote via the
`experiments/` changelog only.

## Honest limits (what DSPy will not do)

- It tunes prompts/demos per stage; it does not invent new geometry
  strategies (bay-vs-flush-cutout elimination reasoning stays ours,
  distills into lessons + prompts for the LM to reuse).
- Two boards is a corpus, not a statistic — no compilation before ~5.
- Formatting brittleness on small LMs: keep the stage LM a strong one;
  the deterministic scaffolding carries the weak-model path.
- The veto list must grow with every semantic bug we catch, or the
  optimizer will rediscover the bugs we already paid for.

## Landscape (where this sits, 2026-10)

| Tool | Shape | Validation | Optimization |
|---|---|---|---|
| TurboCase | KiCad→OpenSCAD template | none (geometry assumptions in metadata) | — |
| boxgen-skills | 3-skill Claude pipeline | OpenSCAD CLI render-or-fix, 5 iterations | — |
| SpeakCAD (commercial) | AI parametric, board-first | Fit Check printer calibration | closed |
| zapim (zoo/KCL) | preset boards + solver | offline mock-exec before engine | AI-edit via iteration API |
| tscircuit create-fdm-enclosure | typed solver library | fit validation of apertures | — |
| MeshCue Forge | MCP NL→spec→all artifacts | DRC stage | — |
| **enclosure-forge** | staged agentic pipeline, measured-first | **boolean gate vs real reference solids** | **DSPy compile on the gate metric** |

Nobody in this landscape validates against real reference solids with
zero-volume pass gates — which is exactly what makes our pipeline
compilable: the objective function is already machine-readable.
Borrow-list from the scan: zapim's wiring-routed-into-case, SpeakCAD's
printer-calibration loop (our coupon doctrine, productized), tscircuit's
component interaction axes (already our connectors.py pattern).
