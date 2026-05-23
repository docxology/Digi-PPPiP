import pytest

from accessibility import (
    CRITERIA,
    accommodation_plan,
    audit_capabilities,
    criterion_score,
    domain_scores,
)


def test_accessibility_audit_scores_supported_capabilities():
    capabilities = {
        "stylus",
        "touch",
        "keyboard",
        "switch",
        "voice",
        "high_contrast",
        "audio_description",
        "haptic_feedback",
        "plain_language",
        "low_distraction_mode",
        "save_consent",
        "delete_control",
        "replay_control",
        "assisted_drawing",
        "role_switching",
    }
    audit = audit_capabilities(capabilities)
    assert audit.score == 1.0
    assert len(audit.passed) == len(CRITERIA)
    assert audit.missing == ()


def test_partial_accessibility_and_domain_scores():
    audit = audit_capabilities({"stylus", "high_contrast"})
    assert 0.0 < audit.score < 1.0
    assert audit.missing
    scores = domain_scores({"stylus", "high_contrast"})
    assert set(scores) >= {"input", "feedback", "privacy"}
    first = CRITERIA[0]
    assert criterion_score(first, {"stylus"}) == 0.2


def test_accommodation_plan_maps_needs():
    plan = accommodation_plan({"low_vision", "privacy_concern"})
    assert "audio_description" in plan
    assert "delete_control" in plan
    with pytest.raises(ValueError):
        accommodation_plan({"unknown_need"})
