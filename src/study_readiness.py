"""Study-readiness and dyadic governance contracts for DigiPPPiP."""

from __future__ import annotations

from dataclasses import asdict, dataclass


HUMAN_SUBJECTS_KEYS: frozenset[str] = frozenset({"hhs2025cfr46", "wma2024helsinki"})
REPORTING_KEYS: frozenset[str] = frozenset({"hoffmann2014tidier", "eysenbach2011consortehealth"})
AI_GOVERNANCE_KEYS: frozenset[str] = frozenset(
    {
        "liu2020consortai",
        "cruzrivera2020spiritai",
        "nist2023airmf",
        "europeanunion2024aiact",
        "hancock2020aimediatedcommunication",
        "malfacini2025companionai",
        "tang2023medicalaiethics",
    }
)
REQUIRED_STUDY_CASE_KEYS: frozenset[str] = frozenset(
    {
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
    }
)


@dataclass(frozen=True)
class StudyReadinessCase:
    """One protocol governance case that must be decided before participant work."""

    key: str
    label: str
    applicability: str
    participant_right: str
    protocol_requirement: str
    source_keys: tuple[str, ...]


@dataclass(frozen=True)
class StudyReadinessCheck:
    """One study-readiness audit check."""

    key: str
    label: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class StudyReadinessAudit:
    """Audit report for protocol readiness."""

    score: float
    missing_cases: tuple[str, ...]
    checks: tuple[StudyReadinessCheck, ...]


@dataclass(frozen=True)
class StudyReadinessMatrixRow:
    """Renderable protocol-readiness row used by governance figures."""

    key: str
    label: str
    applicability: str
    partner_scope: str
    rights_defined: bool
    protocol_defined: bool
    source_anchor_count: int
    conflict_rule: str
    ai_scope: str


STUDY_READINESS_CASES: tuple[StudyReadinessCase, ...] = (
    StudyReadinessCase(
        "dyadic_consent",
        "dyadic consent",
        "default_human_human",
        "Both partners consent separately; one partner's agreement never stands in for the other.",
        "Consent form and intake script record partner-specific consent, archive permission, and contact limits.",
        ("hhs2025cfr46", "wma2024helsinki", "kassam2023digitalconsent"),
    ),
    StudyReadinessCase(
        "deletion",
        "deletion control",
        "default_human_human",
        "Each partner can request deletion of identifiable archive material before analysis lock.",
        "Protocol names who can delete, what is deleted, when deletion closes, and how derived data are handled.",
        ("hhs2025cfr46", "nissenbaum2011contextualprivacy", "petronio2020cpm", "pendse2024consentforward"),
    ),
    StudyReadinessCase(
        "export",
        "export control",
        "default_human_human",
        "Participants can receive their own drawings and approved shared artifacts in a usable format.",
        "Export workflow separates personal copies, shared copies, de-identified research data, and public examples.",
        ("hhs2025cfr46", "dourish2006collectiveprivacy", "shilton2012values", "kassam2023digitalconsent"),
    ),
    StudyReadinessCase(
        "replay",
        "replay control",
        "default_human_human",
        "Participants are told when stroke replay exists and can decline replay use beyond the session.",
        "Replay logs require explicit permission, purpose limits, access logs, and redaction before presentation.",
        (
            "hhs2025cfr46",
            "nissenbaum2011contextualprivacy",
            "dourish2006collectiveprivacy",
            "lebaron2025remoteviz",
        ),
    ),
    StudyReadinessCase(
        "redaction",
        "redaction",
        "default_human_human",
        "Participants can flag names, symbols, locations, or sensitive marks for masking before sharing.",
        "Redaction procedure preserves audit trails while removing identifying or partner-sensitive content.",
        ("hhs2025cfr46", "petronio2020cpm", "wma2024helsinki"),
    ),
    StudyReadinessCase(
        "withdrawal",
        "withdrawal",
        "default_human_human",
        "Either partner can withdraw from future participation without penalty or partner permission.",
        "Withdrawal script explains what happens to collected, de-identified, exported, and jointly authored data.",
        ("hhs2025cfr46", "wma2024helsinki"),
    ),
    StudyReadinessCase(
        "adverse_event",
        "adverse event",
        "default_human_human",
        "Participants know how to pause, stop, or report distress, conflict, or privacy discomfort.",
        "Protocol defines adverse-event triage, escalation contacts, stopping rules, and follow-up documentation.",
        ("hhs2025cfr46", "wma2024helsinki"),
    ),
    StudyReadinessCase(
        "data_retention",
        "data retention",
        "default_human_human",
        "Participants are told how long raw marks, replay logs, exports, and analysis tables are retained.",
        "Retention schedule distinguishes raw identifiable files, de-identified tables, derived metrics, and figures.",
        ("hhs2025cfr46", "hoffmann2014tidier"),
    ),
    StudyReadinessCase(
        "one_partner_disagrees",
        "one partner disagrees",
        "default_human_human",
        "If partners disagree about saving, replay, export, or publication, the stricter privacy choice governs.",
        "Dyadic conflict rule defaults to non-retention or de-identification unless both partners approve sharing.",
        ("dourish2006collectiveprivacy", "petronio2020cpm", "shilton2012values"),
    ),
    StudyReadinessCase(
        "intervention_description",
        "intervention description",
        "default_human_human",
        "Participants and reviewers can see what the drawing activity asks people to do.",
        "TIDieR-style description records materials, procedures, session dose, tailoring, modifications, and fidelity.",
        ("hoffmann2014tidier", "eysenbach2011consortehealth", "benmessaoud2023dyadicmodule"),
    ),
    StudyReadinessCase(
        "ai_branch_governance",
        "AI branch governance",
        "optional_ai_branch",
        "AI support is optional, disclosed, rejectable, reversible, and never described as a partner.",
        (
            "Optional AI studies require a separate arm, risk-management log, CONSORT-AI/SPIRIT-AI fields, "
            "and EU AI Act check."
        ),
        (
            "liu2020consortai",
            "cruzrivera2020spiritai",
            "nist2023airmf",
            "europeanunion2024aiact",
            "hancock2020aimediatedcommunication",
            "malfacini2025companionai",
            "tang2023medicalaiethics",
        ),
    ),
    StudyReadinessCase(
        "prisma_boundary",
        "PRISMA boundary",
        "conditional_not_active",
        "Participants are not affected because the current manuscript does not make a systematic-review claim.",
        "Activate PRISMA only if the evidence synthesis is redesigned as a systematic review.",
        (),
    ),
)


def study_readiness_cases() -> tuple[StudyReadinessCase, ...]:
    """Return the ordered study-readiness case table."""
    return STUDY_READINESS_CASES


def study_readiness_source_keys() -> set[str]:
    """Return all citekeys used by active study-readiness cases."""
    keys: set[str] = set()
    for case in STUDY_READINESS_CASES:
        keys.update(case.source_keys)
    return keys


def _partner_scope(case: StudyReadinessCase) -> str:
    if case.key == "dyadic_consent":
        return "both_partners"
    if case.key in {"deletion", "export", "replay", "redaction", "data_retention", "one_partner_disagrees"}:
        return "shared_archive"
    if case.key in {"withdrawal", "adverse_event"}:
        return "either_partner"
    if case.key == "ai_branch_governance":
        return "optional_ai_branch"
    if case.key == "intervention_description":
        return "participants_and_reviewers"
    return "conditional_review"


def _conflict_rule(case: StudyReadinessCase) -> str:
    if case.key == "one_partner_disagrees":
        return "stricter_privacy_choice"
    if case.key == "withdrawal":
        return "withdrawal_without_partner_permission"
    if case.key == "adverse_event":
        return "pause_stop_or_report"
    return "not_applicable"


def _ai_scope(case: StudyReadinessCase) -> str:
    if case.key == "ai_branch_governance":
        return "optional_separate_branch"
    if case.applicability == "conditional_not_active":
        return "not_active"
    return "not_applicable"


def study_readiness_matrix_rows(
    cases: tuple[StudyReadinessCase, ...] = STUDY_READINESS_CASES,
) -> tuple[StudyReadinessMatrixRow, ...]:
    """Return renderable rows for the study-readiness governance matrix."""
    return tuple(
        StudyReadinessMatrixRow(
            key=case.key,
            label=case.label,
            applicability=case.applicability,
            partner_scope=_partner_scope(case),
            rights_defined=bool(case.participant_right),
            protocol_defined=bool(case.protocol_requirement),
            source_anchor_count=len(case.source_keys),
            conflict_rule=_conflict_rule(case),
            ai_scope=_ai_scope(case),
        )
        for case in cases
    )


def audit_study_readiness(cases: tuple[StudyReadinessCase, ...]) -> StudyReadinessAudit:
    """Audit study-readiness cases for required governance coverage."""
    keys = {case.key for case in cases}
    missing = tuple(sorted(REQUIRED_STUDY_CASE_KEYS - keys))
    active_cases = tuple(case for case in cases if case.applicability != "conditional_not_active")
    ai_cases = tuple(case for case in active_cases if case.applicability == "optional_ai_branch")
    ai_keys: set[str] = set()
    for case in ai_cases:
        ai_keys.update(case.source_keys)
    checks = (
        StudyReadinessCheck(
            "required_cases",
            "all required study-readiness cases are present",
            not missing,
            f"{len(REQUIRED_STUDY_CASE_KEYS - set(missing))}/{len(REQUIRED_STUDY_CASE_KEYS)} covered",
        ),
        StudyReadinessCheck(
            "dyadic_edge_cases",
            "dyadic archive-control edge cases are explicit",
            {"deletion", "export", "replay", "redaction", "one_partner_disagrees"} <= keys,
            "deletion/export/replay/redaction/disagreement",
        ),
        StudyReadinessCheck(
            "participant_rights",
            "active cases state participant-facing rights",
            all(case.participant_right for case in active_cases),
            "participant_right populated",
        ),
        StudyReadinessCheck(
            "protocol_requirements",
            "active cases state protocol requirements",
            all(case.protocol_requirement for case in active_cases),
            "protocol_requirement populated",
        ),
        StudyReadinessCheck(
            "source_anchors",
            "active cases cite source anchors",
            all(case.source_keys for case in active_cases),
            "source_keys populated",
        ),
        StudyReadinessCheck(
            "ai_branch_governance",
            "optional AI branch cites reporting and risk-governance anchors",
            bool(ai_cases) and AI_GOVERNANCE_KEYS <= ai_keys,
            ",".join(sorted(AI_GOVERNANCE_KEYS)),
        ),
    )
    return StudyReadinessAudit(
        score=sum(check.passed for check in checks) / len(checks),
        missing_cases=missing,
        checks=checks,
    )


def participant_brief() -> str:
    """Return a plain-language participant-facing study brief."""
    return (
        "You and your partner would be invited to make marks on a shared drawing surface while the study records "
        "basic timing, tool, and archive-control events. The study is about how shared drawing can be designed and "
        "studied; it is not treatment and it is not a test of your relationship. You can pause or stop a session, "
        "withdraw from future sessions, ask questions, report discomfort, and request review of saved material. "
        "Archive controls are part of the protocol: you can ask about saving, replay, export, redaction, and delete "
        "options before data are locked for analysis. If one partner wants more sharing and the other partner wants "
        "less, the stricter privacy choice governs. Any AI-assisted version is a separate optional branch; AI prompts "
        "must be disclosed, rejectable, reversible, and governed separately from the human-human study."
    )


def audit_to_dict(audit: StudyReadinessAudit) -> dict[str, object]:
    """Return a JSON-serializable study-readiness audit."""
    return {
        "score": audit.score,
        "missing_cases": list(audit.missing_cases),
        "checks": [asdict(check) for check in audit.checks],
    }


def cases_to_dicts(cases: tuple[StudyReadinessCase, ...]) -> list[dict[str, object]]:
    """Return JSON-serializable study-readiness cases."""
    return [asdict(case) for case in cases]
