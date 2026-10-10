"""enclosure-forge stage signatures (DSPy).

Each stage of the board->case pipeline that involves judgment is declared
here as a typed Signature with explicit field descriptions — the contract
optimizers tune. Deterministic stages (extraction, boolean validation,
export) are plain tools (see tools.py) called from program.py.

Best practices applied (dspy docs + production writeups, 2026-10):
- instructions in the docstring state the TASK LAW, not formatting;
- output fields carry validation hooks in their descriptions
  (provenance classes, citation requirements);
- stages stay small and independently gradeable.
"""

import dspy


class Orient(dspy.Signature):
    """Derive the device orientation convention from the board repo's own
    documentation. A user-facing feature placed without this convention is
    a semantic regression even when every boolean check passes (the
    portrait-window bug, lesson 6). Never assume orientation from
    geometric convenience.

    Cite the exact doc path or image that anchors each claim.
    """

    board_context: str = dspy.InputField(
        desc="README/docs excerpts + extracted geometry summary "
             "(outline, connector positions, tallest parts)")
    orientation_convention: str = dspy.OutputField(
        desc="how the device is held: which edge is 'bottom', where "
             "connectors mate from, what the user sees; every claim "
             "followed by [citation: path]")
    user_facing_features: str = dspy.OutputField(
        desc="openings/windows the user interacts with, each mapped "
             "through the orientation convention")


class Envelopes(dspy.Signature):
    """Decide the keep-out and service envelope set from measured
    geometry. Every envelope must name the solids or docs it derives
    from; hand-typed envelopes are allowed only for what solids cannot
    know (plug bodies, swap sweeps, pigtail loops).
    """

    extracted_geometry: str = dspy.InputField(
        desc="analysis/*.json summary: component bboxes + heights, "
             "holes, connector positions")
    orientation: str = dspy.InputField(desc="the Orient stage output")
    envelope_plan: str = dspy.OutputField(
        desc="list: name, zone (u/v/z), provenance class "
             "(derived_kicad/manufacturer_doc/enclosure_design_decision), "
             "and which boolean check will enforce it")
    elimination_notes: str = dspy.OutputField(
        desc="placement options rejected by probe, with the numbers that "
             "killed them (flush-vs-bay class reasoning)")


class Parameters(dspy.Signature):
    """Author the parameter module. Board dimensions LOAD from
    analysis/*.json; the only literals are design decisions, each tagged
    (provenance classes: extracted/derived/manufacturer_doc/
    conservative_assumption/enclosure_design_decision). No magic numbers
    in builders.
    """

    envelope_plan: str = dspy.InputField()
    board_json_summary: str = dspy.InputField()
    parameters_py: str = dspy.OutputField(
        desc="complete parameters.py source: measured values loaded from "
             "JSON, design literals with provenance-tag comments")


class DebugPatch(dspy.Signature):
    """Given failed boolean checks, decide the next geometry patch.
    Read the failure VOLUMES and names: they locate the collision.
    Prefer the minimal change that fixes the named check; re-derive
    placement transforms from the plane that CONTACTS the support
    feature (lesson 12)."""

    failed_checks: str = dspy.InputField(
        desc="names + values from interference_report.json")
    geometry_context: str = dspy.InputField(
        desc="current parameter values + builder structure summary")
    patch: str = dspy.OutputField(
        desc="exact parameter/geometry change with rationale, or "
             "'GATE: check spec wrong' if the check itself is mistaken "
             "(must justify)")
