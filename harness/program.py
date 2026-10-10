"""BoardToCase — the enclosure-forge pipeline as a DSPy program.

Modes:
- lm:      requires a configured dspy LM; stages execute as LM calls.
- record:  operator-in-the-loop — the runner (run_board.py) executes
           stages manually/with tools and records (inputs, outputs) as
           JSONL traces. Those traces are exactly what BootstrapFewShot
           consumes once an LM is configured: record mode IS trainset
           generation.

The deterministic stages (S1 extract, S6 build+validate) run as plain
tools regardless of mode; optimizers only tune the four LM stages
(signatures.py). This mirrors the dspy production guidance of
optimizing the judgment sub-program, not the deterministic scaffolding.
"""

from __future__ import annotations

import dspy

from harness.signatures import DebugPatch, Envelopes, Orient, Parameters


class BoardToCase(dspy.Module):
    def __init__(self):
        self.orient = dspy.ChainOfThought(Orient)
        self.envelopes = dspy.ChainOfThought(Envelopes)
        self.parameters = dspy.Predict(Parameters)
        self.debug = dspy.ChainOfThought(DebugPatch)

    def forward(self, board_context: str, board_json_summary: str):
        orientation = self.orient(board_context=board_context)
        env = self.envelopes(extracted_geometry=board_json_summary,
                             orientation=orientation.orientation_convention)
        params = self.parameters(envelope_plan=env.envelope_plan,
                                 board_json_summary=board_json_summary)
        return dspy.Prediction(
            orientation=orientation.orientation_convention,
            features=orientation.user_facing_features,
            envelopes=env.envelope_plan,
            eliminations=env.elimination_notes,
            parameters_py=params.parameters_py,
        )

    def debug_step(self, failed_checks: str, geometry_context: str):
        return self.debug(failed_checks=failed_checks,
                          geometry_context=geometry_context)
