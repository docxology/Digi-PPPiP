from study_readiness import (
    AI_GOVERNANCE_KEYS,
    REQUIRED_STUDY_CASE_KEYS,
    audit_study_readiness,
    participant_brief,
    study_readiness_cases,
    study_readiness_matrix_rows,
    study_readiness_source_keys,
)


def test_study_readiness_cases_cover_dyadic_protocol_rights():
    cases = study_readiness_cases()
    keys = {case.key for case in cases}

    assert REQUIRED_STUDY_CASE_KEYS <= keys
    assert {
        "dyadic_consent",
        "deletion",
        "export",
        "replay",
        "redaction",
        "withdrawal",
        "adverse_event",
        "data_retention",
        "one_partner_disagrees",
        "ai_branch_governance",
    } <= keys
    assert all(case.protocol_requirement for case in cases)
    assert all(case.participant_right for case in cases)
    assert all(case.source_keys for case in cases if case.applicability != "conditional_not_active")


def test_study_readiness_audit_checks_required_cases_and_ai_branch():
    audit = audit_study_readiness(study_readiness_cases())
    checks = {check.key: check.passed for check in audit.checks}

    assert audit.score == 1.0
    assert checks["required_cases"] is True
    assert checks["dyadic_edge_cases"] is True
    assert checks["participant_rights"] is True
    assert checks["ai_branch_governance"] is True
    assert AI_GOVERNANCE_KEYS <= study_readiness_source_keys()


def test_study_readiness_audit_fails_when_one_partner_disagrees_case_is_missing():
    cases = tuple(case for case in study_readiness_cases() if case.key != "one_partner_disagrees")
    audit = audit_study_readiness(cases)
    checks = {check.key: check.passed for check in audit.checks}

    assert audit.score < 1.0
    assert checks["required_cases"] is False
    assert "one_partner_disagrees" in audit.missing_cases


def test_participant_brief_is_plain_language_and_names_archive_controls():
    brief = participant_brief()
    lowered = brief.lower()

    assert "you and your partner" in lowered
    assert "delete" in lowered
    assert "export" in lowered
    assert "replay" in lowered
    assert "withdraw" in lowered
    assert "one partner" in lowered
    assert "ai" in lowered


def test_study_readiness_matrix_rows_expose_renderable_protocol_controls():
    rows = study_readiness_matrix_rows()
    row_by_key = {row.key: row for row in rows}

    assert REQUIRED_STUDY_CASE_KEYS <= set(row_by_key)
    assert row_by_key["dyadic_consent"].partner_scope == "both_partners"
    assert row_by_key["one_partner_disagrees"].conflict_rule == "stricter_privacy_choice"
    assert row_by_key["ai_branch_governance"].ai_scope == "optional_separate_branch"
    assert all(row.rights_defined for row in rows if row.applicability != "conditional_not_active")
    assert all(row.protocol_defined for row in rows if row.applicability != "conditional_not_active")
    assert all(row.source_anchor_count > 0 for row in rows if row.applicability != "conditional_not_active")
