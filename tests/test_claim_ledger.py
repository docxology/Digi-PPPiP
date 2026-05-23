from claim_ledger import claim_domain_counts, claim_ids, claim_records, missing_claim_sources
from figures import CLAIM_LEDGER_LABEL_MAX_CHARS, claim_ledger_display_label
from source_quality import CLAIM_STRENGTH_LEVELS


def test_claim_ledger_has_stable_unique_ids_and_boundaries():
    records = claim_records()
    ids = claim_ids()
    domains = {record.claim_domain for record in records}
    assert len(records) >= 12
    assert len(ids) == len(set(ids))
    assert {
        "neuroergonomic_burden",
        "phenomenological_presence",
        "relational_coregulation",
        "long_distance_place_usefulness",
        "systems_governance",
    } <= domains
    assert all(record.evidence_keys for record in records)
    assert all(record.max_strength in CLAIM_STRENGTH_LEVELS for record in records)
    assert all(record.next_evidence for record in records)


def test_claim_domain_counts_are_deterministic():
    counts = claim_domain_counts()
    assert counts["digital_intimacy"] >= 2
    assert counts["active_inference"] == 1
    assert counts["neuroergonomic_burden"] == 1
    assert counts["phenomenological_presence"] == 1
    assert counts["relational_coregulation"] == 1
    assert counts["long_distance_place_usefulness"] == 1
    assert counts["systems_governance"] == 1
    assert list(counts) == sorted(counts)


def test_claim_ledger_figure_labels_fit_single_rows():
    labels = [claim_ledger_display_label(record.claim_id) for record in claim_records()]

    assert len(labels) == len(set(labels))
    assert all("\n" not in label for label in labels)
    assert all(len(label) <= CLAIM_LEDGER_LABEL_MAX_CHARS for label in labels)


def test_recent_scholarship_is_mapped_to_relevant_claim_domains():
    records_by_domain = {record.claim_domain: record for record in claim_records()}

    assert {
        "butler2012coregulation",
        "timmons2015physiologicallinkage",
        "paley2022familycoregulation",
    } <= set(records_by_domain["relational_coregulation"].evidence_keys)
    assert "lombard1997presence" in records_by_domain["phenomenological_presence"].evidence_keys
    assert {
        "mcveighschultz2015couple",
        "wenhart2025relatedness",
        "jiang2025ipillowpal",
    } <= set(records_by_domain["long_distance_place_usefulness"].evidence_keys)


def test_systems_governance_claim_has_boundary_and_ethics_sources():
    records_by_domain = {record.claim_domain: record for record in claim_records()}
    sources = set(records_by_domain["systems_governance"].evidence_keys)

    assert {"friston2010fep", "ramstead2020two"} <= sources
    assert {"nissenbaum2011contextualprivacy", "shilton2012values"} <= sources
    assert {"hhs2025cfr46", "wma2024helsinki", "hoffmann2014tidier"} <= sources


def test_missing_claim_sources_reports_absent_keys():
    all_keys = {key for record in claim_records() for key in record.evidence_keys}
    assert missing_claim_sources(all_keys) == ()
    missing = missing_claim_sources(all_keys - {"ragan2016provenance"})
    assert missing == ("ragan2016provenance",)
