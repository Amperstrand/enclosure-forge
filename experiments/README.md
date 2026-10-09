# experiments — prompt-set A/B and the improvement loop

Every enclosure run is an experiment. The evidence is already
machine-readable (`analysis/interference_report.json`,
`testing_status.json`); this directory makes runs comparable.

## Run manifests

Log each full run as `runs/<date>-<board>-<promptset>.json` following
`eval-schema.json`. Minimum viable comparison across two runs of the
SAME board with DIFFERENT prompt sets:

| Metric | Source |
|---|---|
| iterations_to_green | count of validate runs until 0 failed |
| checks_failed_last | interference_report.json |
| wall_clock_minutes | run timestamps (S0→S6, S6→S8 separately) |
| semantic_regressions | bugs like the portrait window: green booleans, wrong device semantics — must be recorded HONESTLY (they are the metric the optimizer cannot see) |
| physical_outcome | coupon decisions, print feedback class |

## Procedure (v0, manual)

1. Fork the prompt library (`references/prompts.md`) into a variant with
   an id (e.g. `P-v0` vs `P-orient-early`).
2. Run the pipeline on the same board rev with each variant; log both
   manifests.
3. Compare metrics; promote the winner into `references/prompts.md` with
   a changelog line.

## dspy evolution (planned)

The next step is to drive the same loop with
[dspy](https://dspy.ai): each stage prompt becomes a signed `dspy.Module`
(`StageSignature: board_context -> stage_output`), and a
teleprompter-style optimizer (BootstrapFewShot → MIPROv2 as traces
accumulate) proposes prompt variants, using as metrics:

- hard signal: `iterations_to_green`, `checks_failed_last` from the
  validation reports (already JSON);
- soft signal: LLMeval-judged gate satisfaction per stage exit criteria;

with the constraint that **semantic_regressions veto a variant** (the
optimizer optimizing booleans while shipping rotated screens is exactly
the failure this metric exists to catch).

Two targets is a corpus, not a statistic — keep A/B manual until target
#3, then automate.
