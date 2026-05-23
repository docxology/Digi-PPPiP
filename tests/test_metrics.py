from figure_catalog import figure_count
from metrics import compute_all_metrics


def test_metrics_pin_closed_form_counts_and_directional_controls():
    metrics = compute_all_metrics()
    assert metrics["NUM_MODALITIES"] == 9
    assert metrics["NUM_TEMPORAL_MODES"] == 3
    assert metrics["NUM_SPATIAL_CONFIGS"] == 3
    assert metrics["NUM_EVIDENCE_DOMAINS"] == 5
    assert metrics["NUM_EVIDENCE_DIMENSIONS"] >= 10
    assert metrics["EVIDENCE_COVERAGE_PCT"] == 100.0
    assert metrics["NUM_EVENT_LOG_FIELDS"] == 6
    assert metrics["EVENT_LOG_MEAN_INTERVAL_S"] == 4.0
    assert metrics["EVENT_LOG_TURN_BALANCE"] == 1.0
    assert metrics["NUM_OUTCOME_MEASURES"] >= 6
    assert metrics["NUM_OUTCOME_DOMAINS"] >= 6
    assert metrics["DEFAULT_DESIGN_STRENGTH_SCORE"] == 4
    assert metrics["NUM_ACCESSIBILITY_CRITERIA"] == 5
    assert metrics["ACCESSIBILITY_AUDIT_SCORE"] == 1.0
    assert metrics["NUM_SOURCE_QUALITY_TYPES"] == 5
    assert metrics["NUM_CLAIM_BOUNDARY_DOMAINS"] == 14
    assert metrics["NUM_VALIDATION_LADDER_STAGES"] == 5
    assert metrics["NUM_SYSTEM_BOUNDARY_ELEMENTS"] == 6
    assert metrics["NUM_FEEDBACK_LOOPS"] == 5
    assert metrics["NUM_CAUSAL_ASSUMPTIONS"] == 5
    assert metrics["NUM_ETHICS_GATES"] == 5
    assert metrics["SYSTEM_GOVERNANCE_SCORE"] == 1.0
    assert metrics["NUM_FIGURE_METHOD_STAGES"] == 9
    assert metrics["NUM_FIGURE_AUDIT_CRITERIA"] == 13
    assert metrics["NUM_VISUAL_ENCODING_ROLES"] == 7
    assert metrics["NUM_FIGURE_METHOD_SOURCE_FAMILIES"] == 5
    assert metrics["NUM_CAPTION_CONTRACT_ITEMS"] == 8
    assert metrics["FIGURE_METHOD_SCORE"] == 1.0
    assert metrics["NUM_FIGURES"] == figure_count()
    assert figure_count() >= 33
    assert metrics["IBS_GAIN"] == 0.55
    assert metrics["COUPLED_FE_FINAL"] < metrics["DECOUPLED_FE_FINAL"]
    assert metrics["FE_REDUCTION_ABS"] > 0.0


def test_metrics_are_deterministic_for_fixed_config():
    config = {"random_seed": 2, "session_steps": 40, "dyadic_steps": 20}
    assert compute_all_metrics(config) == compute_all_metrics(config)
