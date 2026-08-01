from pathlib import Path
import re

from claim_ledger import claim_source_keys
from evidence import citation_keys
from figure_methods import figure_method_source_keys
from source_verification import (
    CURRENT_CHECK_DATE,
    OFFICIAL_SOURCE_KEYS,
    build_source_verification_records,
    manuscript_citation_keys,
    missing_verification_records,
    prioritized_verification_keys,
    source_verification_required_keys,
    source_verification_audit,
    source_verification_summary,
)
from study_readiness import study_readiness_source_keys
from systems_governance import systems_governance_source_keys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NEW_SCHOLARSHIP_KEYS = {
    "butler2012coregulation",
    "timmons2015physiologicallinkage",
    "paley2022familycoregulation",
    "lombard1997presence",
    "mcveighschultz2015couple",
    "wenhart2025relatedness",
    "jiang2025ipillowpal",
    "oittinen2025videodrawing",
    "yoon2025phygital",
    "blair2024remoteddp",
    "malfacini2025companionai",
    "elavsky2024datanavigator",
    "jones2024customization",
}
FORMALISM_SCHOLARSHIP_KEYS = {
    "parr2022activeinference",
    "dacosta2020discrete",
    "friston2023simpler",
}


def _bib_text() -> str:
    return (PROJECT_ROOT / "manuscript" / "references.bib").read_text()


def _bib_keys() -> set[str]:
    return set(re.findall(r"@\w+\{([^,]+),", _bib_text()))


def test_source_verification_records_cover_governed_citekeys():
    required = source_verification_required_keys(PROJECT_ROOT / "manuscript")
    manuscript_only_guarded = manuscript_citation_keys(PROJECT_ROOT / "manuscript") - (
        claim_source_keys()
        | citation_keys()
        | figure_method_source_keys()
        | study_readiness_source_keys()
        | systems_governance_source_keys()
    )
    records = build_source_verification_records(_bib_text())
    record_keys = {record.citekey for record in records}

    assert required <= _bib_keys()
    assert {"veisserie2020thinking"} <= manuscript_only_guarded
    assert "ramstead2020two" not in manuscript_only_guarded
    assert manuscript_only_guarded <= required
    assert missing_verification_records(required, records) == ()
    assert required <= record_keys
    assert all(record.checked_as_of == CURRENT_CHECK_DATE for record in records)
    assert all(record.locator.startswith(("https://doi.org/", "https://", "http://")) for record in records)
    assert all(record.verification_url.startswith(("https://doi.org/", "https://", "http://")) for record in records)
    assert all(record.title for record in records)
    assert all(record.author for record in records)
    assert all(record.year for record in records)
    assert all(record.venue for record in records)
    assert all(record.locator_status == "local_derived" for record in records)
    assert all(record.metadata_source == "local_bibtex" for record in records)
    assert all(record.source_tier for record in records)
    assert all(record.claim_family for record in records)
    assert all(record.manuscript_location for record in records)
    assert all(record.recheck_trigger for record in records)


def test_source_verification_required_keys_include_fixture_manuscript_citations(tmp_path):
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir()
    (manuscript_dir / "00_fixture.md").write_text(
        "Local citation [@fixtureonly; @mikhailova2018pppip] and cross refs [@fig:skip; @sec:skip]."
    )

    assert manuscript_citation_keys(manuscript_dir) == {"fixtureonly", "mikhailova2018pppip"}
    assert "fixtureonly" in source_verification_required_keys(manuscript_dir)


def test_source_verification_prioritizes_recent_preprint_ai_digital_health_and_governance_sources():
    prioritized = prioritized_verification_keys(_bib_text())

    assert OFFICIAL_SOURCE_KEYS <= prioritized
    assert {"azhari2025online", "won2026venus", "hinrichs2025geometric"} <= prioritized
    assert {"kernova2025relationship", "reitere2024telehealth", "canelas2025placemaking"} <= prioritized
    assert NEW_SCHOLARSHIP_KEYS <= prioritized
    assert {"pendse2024consentforward", "lebaron2025remoteviz", "hancock2020aimediatedcommunication"} <= prioritized
    assert {"hhs2025cfr46", "wma2024helsinki", "nist2023airmf", "europeanunion2024aiact"} <= prioritized
    assert systems_governance_source_keys() <= prioritized


def test_new_scholarship_keys_are_bibliographic_verified_and_governed():
    governed = claim_source_keys() | citation_keys() | figure_method_source_keys() | study_readiness_source_keys()
    records = build_source_verification_records(_bib_text())
    record_by_key = {record.citekey: record for record in records}

    assert NEW_SCHOLARSHIP_KEYS <= _bib_keys()
    assert NEW_SCHOLARSHIP_KEYS <= governed
    assert NEW_SCHOLARSHIP_KEYS <= set(record_by_key)
    for key in NEW_SCHOLARSHIP_KEYS:
        record = record_by_key[key]
        assert record.locator.startswith("https://doi.org/")
        assert record.claim_family != "bibliography"
        assert record.manuscript_location != "references"
        assert record.recheck_trigger == "before_submission_or_annual_refresh"


def test_formalism_scholarship_keys_are_bibliographic_verified_and_governed():
    governed = claim_source_keys() | citation_keys()
    records = build_source_verification_records(_bib_text())
    record_by_key = {record.citekey: record for record in records}

    assert FORMALISM_SCHOLARSHIP_KEYS <= _bib_keys()
    assert FORMALISM_SCHOLARSHIP_KEYS <= governed
    assert FORMALISM_SCHOLARSHIP_KEYS <= set(record_by_key)
    for key in FORMALISM_SCHOLARSHIP_KEYS:
        record = record_by_key[key]
        assert record.locator.startswith("https://doi.org/")
        assert record.claim_family != "bibliography"
        assert record.manuscript_location != "references"


def test_systems_governance_sources_are_required_and_governed():
    required = source_verification_required_keys(PROJECT_ROOT / "manuscript")
    records = build_source_verification_records(_bib_text())
    record_by_key = {record.citekey: record for record in records}

    assert systems_governance_source_keys() <= required
    for key in systems_governance_source_keys():
        assert key in record_by_key
        assert "systems-governance" in record_by_key[key].claim_family
        assert "systems_governance" in record_by_key[key].manuscript_location


def test_source_verification_audit_fails_missing_records_deterministically():
    records = build_source_verification_records(_bib_text())
    required = {"mikhailova2018pppip", "missing_key"}
    audit = source_verification_audit(required, records)

    assert audit.score < 1.0
    assert audit.missing_records == ("missing_key",)
    audit_to_map = {check.key: check.passed for check in audit.checks}
    assert audit_to_map["coverage"] is False


def test_source_verification_audit_fails_required_records_with_incomplete_metadata():
    records = build_source_verification_records(_bib_text())
    original = next(record for record in records if record.citekey == "mikhailova2018pppip")
    incomplete = type(original)(
        **{
            **original.__dict__,
            "title": "",
            "venue": "",
            "metadata_source": "",
        }
    )
    patched_records = tuple(incomplete if record.citekey == original.citekey else record for record in records)
    audit = source_verification_audit({"mikhailova2018pppip"}, patched_records)

    assert audit.score < 1.0
    audit_to_map = {check.key: check.passed for check in audit.checks}
    assert audit_to_map["bibliographic_metadata"] is False
    assert audit_to_map["metadata_directness"] is False


def test_source_verification_summary_supports_readiness_figure_contract():
    required = source_verification_required_keys(PROJECT_ROOT / "manuscript")
    records = build_source_verification_records(_bib_text())
    summary = source_verification_summary(required, records, _bib_text())

    assert summary.required_records == len(required)
    assert summary.covered_required_records == len(required)
    assert summary.missing_records == 0
    assert summary.priority_records >= len(OFFICIAL_SOURCE_KEYS)
    assert summary.official_records >= len(OFFICIAL_SOURCE_KEYS)
    assert summary.reporting_records >= 4
    assert summary.tier_counts["official_primary"] >= len(OFFICIAL_SOURCE_KEYS)
    assert summary.recheck_trigger_counts["before_submission_or_annual_refresh"] >= 1


def test_parse_bib_entries_is_brace_aware_and_handles_at_in_fields():
    from source_verification import _field, parse_bib_entries

    bib = (
        "@article{nested,\n"
        "  author = {Smith, {J}. A. and Doe, Jane},\n"
        "  title = {A {Structured} Study},\n"
        "  note = {Correspondence at @example.com and {grouped} tokens},\n"
        "  year = {2020}\n"
        "}\n"
        "@book{second,\n"
        "  author = {Public, John},\n"
        "  title = {Another Book},\n"
        "  publisher = {ACME Press}\n"
        "}\n"
    )
    parsed = parse_bib_entries(bib)
    # The @ in the note field must not truncate the first entry.
    assert set(parsed) == {"nested", "second"}
    assert "Correspondence at @example.com" in parsed["nested"]
    assert _field(parsed["nested"], "author") == "Smith, {J}. A. and Doe, Jane"
    assert _field(parsed["nested"], "title") == "A {Structured} Study"
    assert _field(parsed["nested"], "note") == "Correspondence at @example.com and {grouped} tokens"
    assert _field(parsed["second"], "publisher") == "ACME Press"


def test_field_handles_quoted_and_absent_fields():
    from source_verification import _field

    entry = '@article{key,\n  title   = "A quoted title",\n  year    = {2021},\n}\n'
    assert _field(entry, "title") == "A quoted title"
    assert _field(entry, "year") == "2021"
    assert _field(entry, "absent_field") == ""
