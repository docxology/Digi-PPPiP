"""Claim ledger for DigiPPPiP manuscript governance."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimRecord:
    """One manuscript claim with bounded evidence support."""

    claim_id: str
    section: str
    claim_domain: str
    claim_text: str
    evidence_keys: tuple[str, ...]
    max_strength: str
    next_evidence: str


CLAIM_LEDGER: tuple[ClaimRecord, ...] = (
    ClaimRecord(
        "shared_drawing_relation",
        "introduction",
        "digital_intimacy",
        "Shared drawing can be framed as a relational act when marks preserve mutual agency.",
        ("mikhailova2018pppip", "snir2013joint", "hassenzahl2012love", "vetere2005mediating"),
        "descriptive",
        "dyadic interviews and matched shared-activity comparisons",
    ),
    ClaimRecord(
        "workspace_awareness",
        "cyberphysical",
        "privacy_persistence",
        "A digital canvas should expose partner activity at the granularity needed for response.",
        (
            "tang1991collaborativework",
            "ishii1993clearboard",
            "erickson2000socialtranslucence",
            "gutwin2002workspaceawareness",
            "scott2004territoriality",
        ),
        "descriptive",
        "instrumented usability sessions comparing awareness cues and privacy settings",
    ),
    ClaimRecord(
        "temporal_coordination",
        "temporal",
        "digital_intimacy",
        "Synchronous, alternating, and asynchronous drawing instantiate different coordination hypotheses.",
        ("sebanz2006joint", "olson2000distance", "clark1991grounding", "azhari2025online", "oittinen2025videodrawing"),
        "descriptive",
        "timestamped dyadic logs with qualitative reports of repair, anticipation, and re-entry",
    ),
    ClaimRecord(
        "active_inference_model",
        "active_inference",
        "active_inference",
        "Active inference is a formal modeling language for partner-conditioned mark interpretation.",
        (
            "friston2010fep",
            "friston2017process",
            "parr2022activeinference",
            "dacosta2020discrete",
            "friston2023simpler",
            "vasil2020communication",
            "bolis2024secondperson",
        ),
        "conceptual",
        "parameter fitting, model comparison, and failed-baseline checks against observed sessions",
    ),
    ClaimRecord(
        "digital_art_therapy_boundary",
        "health",
        "therapeutic_efficacy",
        "Digital and online art-therapy literature motivates design questions but not DigiPPPiP efficacy.",
        (
            "zubala2021digitalarttherapy",
            "reitere2024telehealth",
            "miller2020onlinearttherapy",
            "datlen2020whatsapp",
            "haywood2022hexagonal",
            "yoon2025phygital",
            "blair2024remoteddp",
        ),
        "descriptive",
        "controlled clinical or arts-therapy studies using the specific DigiPPPiP protocol",
    ),
    ClaimRecord(
        "neuroergonomic_burden_boundary",
        "neuroergonomics",
        "neuroergonomic_burden",
        "Neuroergonomic concepts can organize attention-load questions but do not prove DigiPPPiP burden.",
        (
            "ayaz2019neuroergonomics",
            "dehais2020grand",
            "moffat2024mobilefnirs",
            "csikszentmihalyi1989flow",
            "mcdaniel2016technoference",
        ),
        "descriptive",
        "task-load ratings, interruption logs, usability data, and optional physiology with artifact controls",
    ),
    ClaimRecord(
        "phenomenological_presence_boundary",
        "phenomenology",
        "phenomenological_presence",
        "Presence and embodiment are interpretive study targets until partners report mediated shared agency.",
        (
            "merleauponty2012phenomenology",
            "lombard1997presence",
            "biocca1997cyborg",
            "lee2004presence",
            "atuk2024bodiesonline",
            "oittinen2025videodrawing",
        ),
        "descriptive",
        "partner interviews or validated presence measures linked to specific mediated drawing conditions",
    ),
    ClaimRecord(
        "access_capability",
        "accessibility",
        "accessibility",
        "Access claims are capability claims until participatory validation with disabled partners occurs.",
        (
            "wobbrock2011ability",
            "w3c2023wcag22",
            "w3c2021coga",
            "shinohara2016socialaccess",
            "morris2016pictures",
            "branham2015collaborativeaccess",
            "elavsky2024datanavigator",
            "jones2024customization",
        ),
        "descriptive",
        "participatory accessibility study with accommodation logs and social-accessibility outcomes",
    ),
    ClaimRecord(
        "relational_coregulation_boundary",
        "relational_aesthetics",
        "relational_coregulation",
        "Relational-aesthetic and arts-therapy sources justify studying co-regulation, not asserting it.",
        (
            "bourriaud2002relational",
            "bishop2004antagonism",
            "snir2013joint",
            "butler2012coregulation",
            "timmons2015physiologicallinkage",
            "paley2022familycoregulation",
            "vaisvaser2024neurodynamics",
            "kaimal2016cortisol",
            "yoon2025phygital",
        ),
        "descriptive",
        "dyadic traces, artifact elicitation, and affect or repair measures from repeated sessions",
    ),
    ClaimRecord(
        "place_micropractice",
        "place",
        "placemaking",
        "Place-responsive drawing can be studied as a recurring relational micro-place practice.",
        ("lewicka2011place", "dourish2006respace", "gordon2011netlocality", "canelas2025placemaking"),
        "descriptive",
        "longitudinal place-prompt study comparing place and non-place drawing prompts",
    ),
    ClaimRecord(
        "long_distance_place_boundary",
        "place",
        "long_distance_place_usefulness",
        "Remote and place-responsive modes are useful hypotheses only where dyads show uptake and need.",
        (
            "olson2000distance",
            "neustaedter2012intimacy",
            "mcveighschultz2015couple",
            "wenhart2025relatedness",
            "jiang2025ipillowpal",
            "dourish2006respace",
            "lewicka2011place",
            "gordon2011netlocality",
            "canelas2025placemaking",
        ),
        "descriptive",
        "long-distance dyad study comparing place-responsive prompts with simpler remote shared activities",
    ),
    ClaimRecord(
        "figure_provenance",
        "methods",
        "design_research_artifacts",
        "Generated figures should preserve provenance from claim, source, code, artifact, and render gate.",
        (
            "zimmerman2007rtd",
            "gaver2012expectrtd",
            "gaver2012annotated",
            "dalsgaard2012documentation",
            "ragan2016provenance",
            "bostock2011d3",
            "satyanarayan2017vegalite",
            "heer2012interactive",
            "rule2019jupyter",
            "stodden2014reproducible",
        ),
        "descriptive",
        "artifact-level provenance audit across manuscript, figure registry, generated files, and render logs",
    ),
    ClaimRecord(
        "dyadic_privacy_governance",
        "health",
        "privacy_persistence",
        "Persistent dyadic canvases require negotiated privacy and values governance, not one-person consent.",
        (
            "nissenbaum2011contextualprivacy",
            "dourish2006collectiveprivacy",
            "petronio2020cpm",
            "shilton2012values",
            "kassam2023digitalconsent",
            "pendse2024consentforward",
        ),
        "descriptive",
        "participant-tested export, deletion, replay, redaction, and authorship governance workflows",
    ),
    ClaimRecord(
        "systems_boundary_governance",
        "methods",
        "systems_governance",
        "DigiPPPiP keeps the human-human mark loop as the kernel and treats AI, physiology, place context, and clinical translation as governed branches.",
        (
            "friston2010fep",
            "ramstead2020two",
            "nissenbaum2011contextualprivacy",
            "shilton2012values",
            "hhs2025cfr46",
            "wma2024helsinki",
            "hoffmann2014tidier",
        ),
        "descriptive",
        "implemented boundary, feedback, ethics, and reversal checks tested in participant-facing protocols",
    ),
    ClaimRecord(
        "lightweight_intimacy",
        "discussion",
        "digital_intimacy",
        "Small intentional digital gestures can be meaningful when embedded in strong-tie practice.",
        (
            "kaye2006clicked",
            "hassenzahl2012love",
            "neustaedter2012intimacy",
            "vetere2005mediating",
            "mcveighschultz2015couple",
            "wenhart2025relatedness",
            "jiang2025ipillowpal",
            "wilson2024dyadichealth",
            "benmessaoud2023dyadicmodule",
            "blair2024remoteddp",
        ),
        "descriptive",
        "longitudinal dyadic outcomes comparing drawing traces with other low-bandwidth rituals",
    ),
    ClaimRecord(
        "ai_relationship_boundary",
        "discussion",
        "ai_mediation",
        "AI-supported drawing must remain an optional mediated branch rather than a partner substitute.",
        (
            "hancock2020aimediatedcommunication",
            "won2026venus",
            "malfacini2025companionai",
            "amershi2019humanai",
            "deterding2017mixedinitiative",
        ),
        "descriptive",
        "preregistered human-human versus optional AI-mediated comparison with agency and replacement-risk measures",
    ),
)


def claim_records() -> tuple[ClaimRecord, ...]:
    """Return the ordered manuscript claim ledger."""
    return CLAIM_LEDGER


def claim_ids() -> tuple[str, ...]:
    """Return stable claim identifiers."""
    return tuple(record.claim_id for record in CLAIM_LEDGER)


def claim_source_keys() -> set[str]:
    """Return every citekey used by the claim ledger."""
    keys: set[str] = set()
    for record in CLAIM_LEDGER:
        keys.update(record.evidence_keys)
    return keys


def claim_domain_counts() -> dict[str, int]:
    """Count claim-ledger records by claim domain."""
    counts: dict[str, int] = {}
    for record in CLAIM_LEDGER:
        counts[record.claim_domain] = counts.get(record.claim_domain, 0) + 1
    return dict(sorted(counts.items()))


def missing_claim_sources(available_keys: set[str]) -> tuple[str, ...]:
    """Return claim-ledger citekeys absent from the available bibliography."""
    return tuple(sorted(claim_source_keys() - available_keys))
