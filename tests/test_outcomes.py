import pytest

from outcomes import (
    OUTCOME_MEASURES,
    design_claim_strength,
    measurement_coverage,
    measures_by_domain,
    multilevel_model_spec,
    outcome_domains,
)


def test_outcome_domains_and_measure_lookup():
    domains = outcome_domains()
    assert "relational" in domains
    assert "accessibility" in domains
    assert len(OUTCOME_MEASURES) >= 6
    assert measures_by_domain("relational")[0].key == "relationship_quality"
    with pytest.raises(ValueError):
        measures_by_domain("unknown")


def test_multilevel_model_spec_is_reproducible():
    spec = multilevel_model_spec("shared_meaning")
    assert spec.dependent_variable == "shared_meaning"
    assert "temporal_mode" in spec.fixed_effects
    assert "dyad_id" in spec.random_effects
    assert "shared_meaning ~" in spec.formula
    with pytest.raises(ValueError):
        multilevel_model_spec("unknown")


def test_design_claim_strength_and_measurement_coverage():
    assert design_claim_strength(10, randomized=False, longitudinal=False) == "descriptive"
    assert design_claim_strength(25, randomized=False, longitudinal=False) == "associational"
    assert design_claim_strength(45, randomized=True, longitudinal=False) == "comparative"
    assert design_claim_strength(80, randomized=True, longitudinal=True) == "causal_candidate"
    with pytest.raises(ValueError):
        design_claim_strength(0, randomized=True, longitudinal=True)
    selected = {"relationship_quality", "flow", "access_success"}
    assert 0.0 < measurement_coverage(selected) < 1.0
    assert measurement_coverage(set()) == 0.0
