import pytest

from source_quality import (
    CLAIM_STRENGTH_LEVELS,
    claim_boundaries,
    claim_boundary,
    classify_bib_entry,
    classify_entry_type,
    overclaim_warning,
    parse_bib_entries,
    source_quality_table,
    validation_ladder,
)


def test_source_quality_classifies_entry_types():
    article = "@article{a, title={A}, journal={Journal}, year={2026}}"
    book = "@book{b, title={B}, publisher={Press}, year={2026}}"
    chapter = "@incollection{d, title={D}, booktitle={Book}, year={2026}}"
    preprint = "@article{c, title={C}, journal={arXiv preprint arXiv:1}, year={2026}}"
    assert classify_entry_type(article) == "peer_reviewed_article"
    assert classify_entry_type(book) == "book"
    assert classify_entry_type(chapter) == "book"
    assert classify_entry_type(preprint) == "preprint"


def test_source_quality_table_extracts_keys_and_warnings():
    bib = "\n".join(
        [
            "@article{a, title={A}, journal={Journal}, year={2026}}",
            "@book{b, title={B}, publisher={Press}, year={2026}}",
        ]
    )
    entries = parse_bib_entries(bib)
    assert len(entries) == 2
    qualities = source_quality_table(bib)
    assert [quality.key for quality in qualities] == ["a", "b"]
    assert qualities[0].claim_strength == "moderate"
    assert classify_bib_entry(entries[1]).source_type == "book"


def test_overclaim_warnings_are_conservative():
    assert "clinical efficacy" in overclaim_warning("therapeutic_efficacy")
    assert "correlate" in overclaim_warning("synchrony_causality")
    assert "partner agency" in overclaim_warning("ai_mediation")
    with pytest.raises(ValueError):
        overclaim_warning("unknown")


def test_claim_boundaries_map_domains_to_evidence_requirements():
    boundaries = claim_boundaries()
    domains = {boundary.domain for boundary in boundaries}
    assert {
        "therapeutic_efficacy",
        "synchrony_causality",
        "active_inference",
        "accessibility",
        "placemaking",
        "digital_intimacy",
        "neuroergonomic_burden",
        "phenomenological_presence",
        "relational_coregulation",
        "long_distance_place_usefulness",
        "ai_mediation",
        "privacy_persistence",
        "systems_governance",
        "design_research_artifacts",
    } <= domains
    assert all(boundary.allowed_strength in CLAIM_STRENGTH_LEVELS for boundary in boundaries)
    assert claim_boundary("accessibility").score < claim_boundary("therapeutic_efficacy").score
    assert claim_boundary("neuroergonomic_burden").allowed_strength == "descriptive"
    assert claim_boundary("phenomenological_presence").allowed_strength == "descriptive"
    assert claim_boundary("relational_coregulation").allowed_strength == "descriptive"
    assert claim_boundary("long_distance_place_usefulness").allowed_strength == "descriptive"
    assert claim_boundary("systems_governance").allowed_strength == "descriptive"
    assert "reversibility" in claim_boundary("systems_governance").required_evidence


def test_validation_ladder_is_ordered_from_feasibility_to_optional_physiology():
    stages = validation_ladder()
    assert [stage.score for stage in stages] == sorted(stage.score for stage in stages)
    assert stages[0].stage == "feasibility"
    assert stages[-1].stage == "physiology"
    assert "permutation controls" in stages[-1].required_controls
