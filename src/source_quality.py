"""Source-quality and claim-strength utilities for DigiPPPiP."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceQuality:
    """Quality classification for one bibliography entry."""

    key: str
    source_type: str
    claim_strength: str
    warning: str


@dataclass(frozen=True)
class ClaimBoundary:
    """Evidence boundary for one recurring DigiPPPiP claim domain."""

    domain: str
    label: str
    allowed_strength: str
    required_evidence: str
    warning: str
    score: int


@dataclass(frozen=True)
class ValidationStage:
    """Empirical stage required before stronger framework claims are made."""

    stage: str
    claim_unlocked: str
    required_design: str
    required_controls: str
    score: int


TYPE_STRENGTH: dict[str, tuple[str, str]] = {
    "peer_reviewed_article": ("moderate", "Use for scoped empirical or review claims."),
    "book": ("theoretical", "Use for conceptual framing, not outcome estimates."),
    "preprint": ("provisional", "Flag as preprint and avoid settled-evidence language."),
    "conference_or_report": ("limited", "Use for methods or examples, not broad claims."),
    "misc": ("unknown", "Verify before relying on this source."),
}

CLAIM_STRENGTH_LEVELS: tuple[str, ...] = (
    "conceptual",
    "descriptive",
    "associational",
    "comparative",
    "causal_or_clinical",
)

CLAIM_BOUNDARIES: tuple[ClaimBoundary, ...] = (
    ClaimBoundary(
        "therapeutic_efficacy",
        "therapy",
        "comparative",
        "controlled clinical or arts-therapy study with prespecified outcomes",
        "Do not claim treatment or clinical efficacy without trials.",
        3,
    ),
    ClaimBoundary(
        "synchrony_causality",
        "synchrony",
        "associational",
        "event-locked dyadic data with artifact correction and permutation controls",
        "Treat synchrony as a correlate unless causal design supports more.",
        2,
    ),
    ClaimBoundary(
        "active_inference",
        "active inference",
        "conceptual",
        "parameterized model, observable predictions, and failed-baseline checks",
        "Present active inference as a model frame, not proof of mechanism.",
        0,
    ),
    ClaimBoundary(
        "accessibility",
        "access",
        "descriptive",
        "participatory evaluation with disabled partners and documented accommodations",
        "Do not claim universal access without participatory validation.",
        1,
    ),
    ClaimBoundary(
        "placemaking",
        "place",
        "descriptive",
        "situated longitudinal reports plus comparison with non-place prompts",
        "Keep place claims at micro-scale unless community data exist.",
        1,
    ),
    ClaimBoundary(
        "digital_intimacy",
        "intimacy",
        "associational",
        "longitudinal dyadic outcomes with matched shared-activity controls",
        "Avoid relationship-improvement claims without longitudinal dyadic data.",
        2,
    ),
    ClaimBoundary(
        "neuroergonomic_burden",
        "neuroergonomic burden",
        "descriptive",
        "task-load, interruption, and optional physiology data with artifact controls",
        "Do not convert attention-load framing into neural or workload evidence without participant data.",
        1,
    ),
    ClaimBoundary(
        "phenomenological_presence",
        "presence",
        "descriptive",
        "interviews or validated presence measures tied to concrete interaction conditions",
        "Treat presence as reported experience, not proof that mediation preserves embodiment.",
        1,
    ),
    ClaimBoundary(
        "relational_coregulation",
        "co-regulation",
        "descriptive",
        "dyadic interaction traces plus emotional, physiological, and participant-report linkage measures",
        "Frame co-regulation as a study target until relational dynamics and linkage context are directly observed.",
        1,
    ),
    ClaimBoundary(
        "long_distance_place_usefulness",
        "distance and place",
        "descriptive",
        "longitudinal remote-use comparison with place-responsive prompts, relatedness technologies, and simpler routines",
        "Do not claim remote usefulness or place attachment without dyad-specific uptake and comparison data.",
        1,
    ),
    ClaimBoundary(
        "ai_mediation",
        "AI mediation",
        "descriptive",
        "logs and interviews showing AI supports rather than replaces partner agency",
        "Treat AI as an assistive mediator unless partner agency is preserved.",
        1,
    ),
    ClaimBoundary(
        "privacy_persistence",
        "privacy",
        "descriptive",
        "consent, deletion, replay, export, and audit records tested with participants",
        "Persistent archives require privacy controls before shared-memory claims.",
        1,
    ),
    ClaimBoundary(
        "systems_governance",
        "systems governance",
        "descriptive",
        "explicit boundary, feedback, causal, ethics, and reversibility gates before escalation",
        "Do not let systems language imply control, safety, or efficacy without direct evidence.",
        1,
    ),
    ClaimBoundary(
        "design_research_artifacts",
        "design research",
        "descriptive",
        "research-through-design artifacts with documented lineage, reader-facing audit, and replaceable data path",
        "Generated diagrams are method artifacts, not empirical evidence, until deployment or participant data exist.",
        1,
    ),
)

VALIDATION_LADDER: tuple[ValidationStage, ...] = (
    ValidationStage(
        "feasibility",
        "participants can complete and understand the task",
        "instrumented pilot with consent, latency, and event-log checks",
        "completion, dropout, usability, and adverse-event review",
        0,
    ),
    ValidationStage(
        "meaning",
        "partners describe the canvas as shared and relational",
        "interviews plus artifact elicitation after repeated sessions",
        "ordinary shared drawing and solo art-making comparisons",
        1,
    ),
    ValidationStage(
        "access",
        "accommodations expand agency for specified participants",
        "participatory accessibility study with disabled partners",
        "capability audit, accommodation logs, and social-accessibility review",
        2,
    ),
    ValidationStage(
        "comparative outcomes",
        "DigiPPPiP differs from matched shared activities",
        "randomized or counterbalanced dyadic study",
        "video chat, shared game, shared media, and ordinary drawing controls",
        3,
    ),
    ValidationStage(
        "physiology",
        "optional neural or bodily signals track defined events",
        "hyperscanning or physiology protocol with event synchronization",
        "motion, physiology, shared-stimulus, and permutation controls",
        4,
    ),
)


def classify_entry_type(entry: str) -> str:
    """Classify a BibTeX entry into a conservative source type."""
    head = entry.split("{", 1)[0].strip().lower()
    lower = entry.lower()
    if head in {"@book", "@inbook", "@incollection"}:
        return "book"
    if "arxiv" in lower:
        return "preprint"
    if head in {"@inproceedings", "@proceedings"}:
        return "conference_or_report"
    if head == "@article" and "journal" in lower:
        return "peer_reviewed_article"
    return "misc"


def extract_bib_key(entry: str) -> str:
    """Extract the BibTeX key from one entry."""
    match = re.search(r"@\w+\{([^,\s]+)", entry)
    if not match:
        raise ValueError("entry does not contain a BibTeX key")
    return match.group(1)


def classify_bib_entry(entry: str) -> SourceQuality:
    """Return conservative quality metadata for one BibTeX entry."""
    source_type = classify_entry_type(entry)
    strength, warning = TYPE_STRENGTH[source_type]
    return SourceQuality(
        key=extract_bib_key(entry),
        source_type=source_type,
        claim_strength=strength,
        warning=warning,
    )


def parse_bib_entries(bib_text: str) -> tuple[str, ...]:
    """Split a BibTeX file into entries without attempting full BibTeX parsing."""
    entries = re.findall(r"@\w+\{.*?(?=\n@|\Z)", bib_text, flags=re.DOTALL)
    return tuple(entry.strip() for entry in entries if entry.strip())


def source_quality_table(bib_text: str) -> tuple[SourceQuality, ...]:
    """Classify all BibTeX entries in a file."""
    return tuple(classify_bib_entry(entry) for entry in parse_bib_entries(bib_text))


def claim_boundaries() -> tuple[ClaimBoundary, ...]:
    """Return the conservative claim-boundary table."""
    return CLAIM_BOUNDARIES


def claim_boundary(domain: str) -> ClaimBoundary:
    """Return the evidence boundary for one claim domain."""
    for boundary in CLAIM_BOUNDARIES:
        if boundary.domain == domain:
            return boundary
    raise ValueError(f"unknown claim domain: {domain!r}")


def validation_ladder() -> tuple[ValidationStage, ...]:
    """Return the staged validation ladder from feasibility to physiology."""
    return VALIDATION_LADDER


def overclaim_warning(claim_type: str) -> str:
    """Return the warning text for a recurring DigiPPPiP overclaim risk."""
    return claim_boundary(claim_type).warning
