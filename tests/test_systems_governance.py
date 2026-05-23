from pathlib import Path
import re

from systems_governance import (
    causal_assumptions,
    data_flow_stages,
    ethics_gates,
    feedback_loops,
    governance_score,
    governance_summary,
    system_architecture_lanes,
    system_boundary_elements,
    systems_governance_source_keys,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _bib_keys() -> set[str]:
    text = (PROJECT_ROOT / "manuscript" / "references.bib").read_text()
    return set(re.findall(r"@\w+\{([^,]+),", text))


def test_systems_governance_records_are_complete_and_source_backed():
    records = (*system_boundary_elements(), *feedback_loops(), *causal_assumptions(), *ethics_gates())

    assert len(records) >= 20
    assert governance_score() == 1.0
    assert systems_governance_source_keys() <= _bib_keys()
    assert all(record.source_keys for record in records)
    assert all(not key.endswith("_governance") for key in systems_governance_source_keys())


def test_system_boundary_keeps_optional_branches_outside_kernel():
    boundaries = {record.key: record for record in system_boundary_elements()}

    assert boundaries["human_human_kernel"].boundary_status == "inside_kernel"
    assert boundaries["ai_assistance"].boundary_status == "optional_branch"
    assert boundaries["physiology"].boundary_status == "optional_branch"
    assert boundaries["clinical_translation"].boundary_status == "out_of_scope_until_review"
    assert "precise location" in boundaries["place_context"].rationale
    assert "reviewed protocol" in boundaries["clinical_translation"].governance_gate


def test_feedback_and_causal_records_preserve_falsification_and_reversibility():
    loops = {record.key: record for record in feedback_loops()}
    assumptions = {record.key: record for record in causal_assumptions()}

    assert {record.loop_type for record in loops.values()} == {"balancing", "reinforcing"}
    assert "Delete" in loops["privacy_boundary"].reversibility_gate
    assert "Downgrade" in loops["evidence_escalation"].reversibility_gate
    assert "matched controls" in assumptions["marks_to_relatedness"].falsifier
    assert "artifact correction" in assumptions["physiology_to_coregulation"].falsifier


def test_ethics_gates_and_summary_are_deterministic():
    gates = {record.key: record for record in ethics_gates()}
    summary = governance_summary()

    assert summary == {
        "system_boundary_elements": 6,
        "feedback_loops": 5,
        "causal_assumptions": 5,
        "ethics_gates": 5,
    }
    assert "separately" in gates["separate_consent"].participant_right
    assert "stricter dyadic choice" in gates["archive_control"].reversal_rule
    assert "opt-out" in gates["optional_ai_branch"].protocol_artifact


def test_system_architecture_lanes_keep_ai_outside_default_kernel():
    lanes = {lane.key: lane for lane in system_architecture_lanes()}

    assert tuple(lanes) == (
        "human_human_loop",
        "instrumentation_support",
        "modeling_layer",
        "optional_ai_branch",
        "publication_governance",
    )
    assert lanes["human_human_loop"].boundary_status == "inside kernel"
    assert "shared surface" in lanes["human_human_loop"].components
    assert lanes["optional_ai_branch"].boundary_status == "outside default"
    assert "rejectable" in lanes["optional_ai_branch"].governance_gate
    assert "separable from partner authorship" in lanes["optional_ai_branch"].governance_gate
    assert "render scan" in lanes["publication_governance"].components


def test_data_flow_stages_distinguish_observed_computed_and_rendered_artifacts():
    stages = data_flow_stages()

    assert tuple(stage.key for stage in stages) == (
        "capture",
        "separate",
        "transform",
        "model",
        "render",
        "govern",
        "publish",
    )
    assert {stage.data_status for stage in stages} == {
        "observed",
        "derived",
        "computed",
        "rendered",
        "governed",
        "published",
    }
    assert "human marks" in stages[0].artifact
    assert "hidden drafts" in stages[0].governance_gate
    assert "hypotheses" in stages[3].governance_gate
    assert "unresolved-reference checks" in stages[-1].governance_gate
