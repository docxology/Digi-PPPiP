"""Systems-governance primitives for DigiPPPiP.

The records here make the HolisticSystems / FirstPrinciples layer executable:
what is inside the kernel, what stays optional, which loops are monitored, and
which gates prevent conceptual claims from becoming implied efficacy claims.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SystemBoundaryElement:
    """One element in or around the minimum DigiPPPiP system boundary."""

    key: str
    label: str
    boundary_status: str
    rationale: str
    governance_gate: str
    source_keys: tuple[str, ...]


@dataclass(frozen=True)
class FeedbackLoop:
    """One governed feedback loop that can stabilize or distort the dyad."""

    key: str
    loop_type: str
    signal: str
    governing_action: str
    failure_mode: str
    reversibility_gate: str
    source_keys: tuple[str, ...]


@dataclass(frozen=True)
class CausalAssumption:
    """One manuscript-level causal hypothesis kept below efficacy strength."""

    key: str
    assumed_link: str
    observable_probe: str
    falsifier: str
    upgrade_gate: str
    source_keys: tuple[str, ...]


@dataclass(frozen=True)
class EthicsGate:
    """One participant-facing ethics gate required before human-subjects work."""

    key: str
    label: str
    participant_right: str
    protocol_artifact: str
    reversal_rule: str
    source_keys: tuple[str, ...]


@dataclass(frozen=True)
class SystemArchitectureLane:
    """One visual lane in the system architecture boundary diagram."""

    key: str
    label: str
    boundary_status: str
    components: tuple[str, ...]
    governance_gate: str


@dataclass(frozen=True)
class DataFlowStage:
    """One governed step from partner action to publication artifact."""

    key: str
    label: str
    artifact: str
    data_status: str
    governance_gate: str


GovernanceRecord = SystemBoundaryElement | FeedbackLoop | CausalAssumption | EthicsGate


SYSTEM_BOUNDARY_ELEMENTS: tuple[SystemBoundaryElement, ...] = (
    SystemBoundaryElement(
        "human_human_kernel",
        "human-human drawing loop",
        "inside_kernel",
        "Two partners exchange perceivable marks while retaining agency over response and persistence.",
        "Both partners can perceive, respond, pause, and govern archive persistence.",
        ("friston2010fep", "ramstead2020two", "mikhailova2018pppip"),
    ),
    SystemBoundaryElement(
        "event_log",
        "event log and replay record",
        "support_boundary",
        "Logging is an audit substrate for time, action, replay, and analysis rather than the relationship itself.",
        "Logs name actor, action, channel, timestamp, and archive-control state before analysis.",
        ("hoffmann2014tidier", "eysenbach2011consortehealth", "hhs2025cfr46"),
    ),
    SystemBoundaryElement(
        "place_context",
        "place-responsive context",
        "optional_branch",
        "Place cues are study prompts or participant reports, not a requirement for precise location capture.",
        "Use coarse, consented cues and allow partners to decline place disclosure.",
        ("lewicka2011place", "dourish2006respace", "nissenbaum2011contextualprivacy"),
    ),
    SystemBoundaryElement(
        "physiology",
        "optional physiology",
        "optional_branch",
        "Physiology can test event-linked hypotheses only after feasibility, consent, and artifact controls.",
        "Separate physiology consent, signal-quality exclusion, and null-model reporting are required.",
        ("czeszumski2020hyperscanning", "hamilton2021hyperscanning", "hhs2025cfr46"),
    ),
    SystemBoundaryElement(
        "ai_assistance",
        "optional AI assistance",
        "optional_branch",
        "AI assistance is outside the human-human kernel unless it remains disclosed, rejectable, and reversible.",
        "AI suggestions must be optional, labelled, undoable, logged, and separable from partner authorship.",
        ("amershi2019humanai", "hancock2020aimediatedcommunication", "nist2023airmf"),
    ),
    SystemBoundaryElement(
        "clinical_translation",
        "clinical or therapeutic translation",
        "out_of_scope_until_review",
        "Clinical use is not part of the conceptual framework without reviewed intervention evidence.",
        "A reviewed protocol, intervention description, adverse-event route, and prespecified outcomes are required.",
        ("hhs2025cfr46", "wma2024helsinki", "hoffmann2014tidier"),
    ),
)


FEEDBACK_LOOPS: tuple[FeedbackLoop, ...] = (
    FeedbackLoop(
        "action_perception",
        "balancing",
        "partner marks, pauses, repairs, and responses",
        "Adapt the next mark or wait state to preserve mutual agency.",
        "The canvas becomes one-way broadcast or performance for the tool.",
        "Pause, undo, restart, or switch to a simpler shared activity.",
        ("friston2017process", "ramstead2020two", "vasil2020communication"),
    ),
    FeedbackLoop(
        "privacy_boundary",
        "balancing",
        "discomfort, redaction requests, archive disagreement, or export hesitation",
        "Apply the stricter privacy choice and make persistence choices visible.",
        "The persistent canvas is experienced as surveillance rather than shared memory.",
        "Delete, redact, de-identify, or withhold archive material before analysis lock.",
        ("nissenbaum2011contextualprivacy", "petronio2020cpm", "pendse2024consentforward"),
    ),
    FeedbackLoop(
        "access_adaptation",
        "balancing",
        "fatigue, sensory mismatch, input friction, or partner-mediated assistance needs",
        "Adjust input, feedback, pace, and accommodation settings during the session.",
        "Accessibility language hides added workload or partner dependency.",
        "Return to lower-burden settings and record accommodation changes.",
        ("wobbrock2011ability", "shinohara2016socialaccess", "w3c2023wcag22"),
    ),
    FeedbackLoop(
        "ai_intrusion",
        "balancing",
        "unwanted suggestions, authorship confusion, or reduced partner attention",
        "Disable, reject, revise, or undo AI output while preserving the human partner's mark.",
        "The system substitutes for the partner or authors the relational gesture.",
        "Separate AI and non-AI arms, audit suggestions, and let either partner opt out.",
        ("amershi2019humanai", "hancock2020aimediatedcommunication", "malfacini2025companionai"),
    ),
    FeedbackLoop(
        "evidence_escalation",
        "reinforcing",
        "completed feasibility, meaning, access, comparison, and physiology studies",
        "Upgrade claim strength only when direct evidence reaches the matching validation stage.",
        "Adjacent scholarship is mistaken for direct DigiPPPiP evidence.",
        "Downgrade claim language when controls, null models, or participant reports do not support it.",
        ("hoffmann2014tidier", "source_quality_governance", "claim_ledger_governance"),
    ),
)


CAUSAL_ASSUMPTIONS: tuple[CausalAssumption, ...] = (
    CausalAssumption(
        "marks_to_relatedness",
        "Shared marks may support felt connection when partners recognize each other's agency.",
        "Repeated-session interviews, event logs, and matched shared-activity controls.",
        "Partners report no shared agency or matched controls explain the same outcomes.",
        "Longitudinal dyadic comparison before relationship-improvement language.",
        ("hassenzahl2012love", "neustaedter2012intimacy", "wenhart2025relatedness"),
    ),
    CausalAssumption(
        "place_prompt_to_memory",
        "Place-responsive prompts may organize relational memory without requiring precise geolocation.",
        "Place and non-place prompt comparison with partner artifact elicitation.",
        "Place prompts do not change recall, meaning, or privacy acceptability.",
        "Longitudinal place-prompt study before place-attachment claims.",
        ("lewicka2011place", "dourish2006respace", "canelas2025placemaking"),
    ),
    CausalAssumption(
        "archive_to_shared_memory",
        "Persistent replay may become shared memory only if archive control remains dyadic.",
        "Consent logs, replay use, redaction requests, and participant reports of archive meaning.",
        "Participants describe replay as surveillance, conflict, or unwanted persistence.",
        "Archive-control usability and acceptability evidence before shared-memory claims.",
        ("nissenbaum2011contextualprivacy", "dourish2006collectiveprivacy", "petronio2020cpm"),
    ),
    CausalAssumption(
        "ai_to_attention",
        "AI support may help only if it redirects attention toward the partner rather than the system.",
        "Human-human versus optional AI-mediated arm with agency, authorship, and attention measures.",
        "AI output reduces co-authorship, increases replacement language, or becomes the interaction focus.",
        "Preregistered comparison before claiming AI improves the practice.",
        ("amershi2019humanai", "hancock2020aimediatedcommunication", "malfacini2025companionai"),
    ),
    CausalAssumption(
        "physiology_to_coregulation",
        "Physiological linkage may track event-level repair or co-regulation only after artifact controls.",
        "Event-synchronized physiological signals, exclusion windows, and participant-report linkage.",
        "Linkage disappears under artifact correction, shared-stimulus controls, or permutation tests.",
        "Dyadic physiological and behavioral evidence before co-regulation claims.",
        ("timmons2015physiologicallinkage", "butler2012coregulation", "hamilton2021hyperscanning"),
    ),
)


ETHICS_GATES: tuple[EthicsGate, ...] = (
    EthicsGate(
        "separate_consent",
        "separate dyadic consent",
        "Each partner consents separately and can withdraw without partner permission.",
        "Partner-specific consent, withdrawal, and contact-limit records.",
        "Stop future participation and route already collected data by the consent form.",
        ("hhs2025cfr46", "wma2024helsinki", "kassam2023digitalconsent"),
    ),
    EthicsGate(
        "archive_control",
        "archive control",
        "Participants know and control save, replay, export, deletion, and redaction options.",
        "Archive-control checklist and before-analysis-lock decision log.",
        "Delete, redact, export, or retain only according to the stricter dyadic choice.",
        ("nissenbaum2011contextualprivacy", "dourish2006collectiveprivacy", "pendse2024consentforward"),
    ),
    EthicsGate(
        "metadata_minimization",
        "metadata minimization",
        "Place and health-adjacent data are minimized to what the study question requires.",
        "Data dictionary separating raw marks, event logs, context cues, and derived metrics.",
        "Drop or coarsen unnecessary identifiers before analysis and publication.",
        ("nissenbaum2011contextualprivacy", "shilton2012values", "hhs2025cfr46"),
    ),
    EthicsGate(
        "adverse_event_route",
        "adverse-event route",
        "Participants can pause, stop, or report distress, conflict, or privacy discomfort.",
        "Stop rules, escalation contacts, and adverse-event documentation.",
        "Pause the session, separate partners if needed, and document follow-up.",
        ("hhs2025cfr46", "wma2024helsinki"),
    ),
    EthicsGate(
        "optional_ai_branch",
        "optional AI branch",
        "Either partner can refuse AI assistance without losing access to the human-human task.",
        "Separate AI-arm disclosure, risk log, input/output description, and opt-out route.",
        "Disable AI, remove AI-generated content, and preserve the non-AI comparison path.",
        ("liu2020consortai", "cruzrivera2020spiritai", "nist2023airmf", "europeanunion2024aiact"),
    ),
)


SYSTEM_ARCHITECTURE_LANES: tuple[SystemArchitectureLane, ...] = (
    SystemArchitectureLane(
        "human_human_loop",
        "human-human default",
        "inside kernel",
        ("partner A mark", "shared surface", "partner B response", "dyadic archive choice"),
        "both partners can pause, respond, undo, redact, delete, or simplify",
    ),
    SystemArchitectureLane(
        "instrumentation_support",
        "instrumentation support",
        "support boundary",
        ("event log", "timestamps", "replay state", "access settings"),
        "capture only consented actor, action, channel, timing, and archive-control state",
    ),
    SystemArchitectureLane(
        "modeling_layer",
        "modeling layer",
        "computed lens",
        ("active inference", "narrative info", "geometry", "outcome model"),
        "model outputs remain illustrative until fitted to observed sessions",
    ),
    SystemArchitectureLane(
        "optional_ai_branch",
        "optional AI branch",
        "outside default",
        ("suggestion", "rationale", "access support", "separate log"),
        "AI support must be labelled, rejectable, undoable, and separable from partner authorship",
    ),
    SystemArchitectureLane(
        "publication_governance",
        "publication governance",
        "evidence boundary",
        ("source ledger", "figure registry", "long desc.", "render scan"),
        "claims upgrade only after direct evidence, verified sources, and green render gates",
    ),
)


DATA_FLOW_STAGES: tuple[DataFlowStage, ...] = (
    DataFlowStage(
        "capture",
        "capture",
        "human marks, pauses, utterances, and archive choices",
        "observed",
        "record only consented event fields; keep hidden drafts and device telemetry out by default",
    ),
    DataFlowStage(
        "separate",
        "separate",
        "visible canvas, event log, replay record, and optional branch logs",
        "observed",
        "do not collapse the partner-facing artifact into the analysis table",
    ),
    DataFlowStage(
        "transform",
        "transform",
        "turn balance, intervals, access settings, and protocol summaries",
        "derived",
        "derive values from tested primitives and keep configuration explicit",
    ),
    DataFlowStage(
        "model",
        "model",
        "active-inference, narrative, geometric, and outcome-model diagnostics",
        "computed",
        "treat model outputs as hypotheses unless fitted to observed participant data",
    ),
    DataFlowStage(
        "render",
        "render",
        "figures, registry rows, long descriptions, and manuscript variables",
        "rendered",
        "every rendered claim object names its generator, caveat, and accessibility description",
    ),
    DataFlowStage(
        "govern",
        "govern",
        "claim ledger, source verification, study-readiness matrix, and artifact audit",
        "governed",
        "upgrade claim language only when source and study gates match the claim domain",
    ),
    DataFlowStage(
        "publish",
        "publish",
        "template PDF, HTML, slides, and unresolved-marker scan",
        "published",
        "ship only after prerender, render, test, and unresolved-reference checks pass",
    ),
)


def system_boundary_elements() -> tuple[SystemBoundaryElement, ...]:
    """Return the ordered system-boundary table."""
    return SYSTEM_BOUNDARY_ELEMENTS


def feedback_loops() -> tuple[FeedbackLoop, ...]:
    """Return governed feedback loops for the framework."""
    return FEEDBACK_LOOPS


def causal_assumptions() -> tuple[CausalAssumption, ...]:
    """Return causal hypotheses and falsification gates."""
    return CAUSAL_ASSUMPTIONS


def ethics_gates() -> tuple[EthicsGate, ...]:
    """Return participant-facing ethics gates."""
    return ETHICS_GATES


def system_architecture_lanes() -> tuple[SystemArchitectureLane, ...]:
    """Return architecture lanes for the system-boundary figure."""
    return SYSTEM_ARCHITECTURE_LANES


def data_flow_stages() -> tuple[DataFlowStage, ...]:
    """Return the ordered data-flow/provenance path for the protocol figure."""
    return DATA_FLOW_STAGES


def systems_governance_source_keys() -> set[str]:
    """Return citekeys used by systems-governance records.

    Internal governance pseudo-keys document project-local mechanisms and are
    intentionally excluded from bibliography/source-verification requirements.
    """
    keys: set[str] = set()
    for collection in (SYSTEM_BOUNDARY_ELEMENTS, FEEDBACK_LOOPS, CAUSAL_ASSUMPTIONS, ETHICS_GATES):
        for record in collection:
            keys.update(key for key in record.source_keys if not key.endswith("_governance"))
    return keys


def governance_summary() -> dict[str, int]:
    """Return deterministic counts for manuscript metrics."""
    return {
        "system_boundary_elements": len(SYSTEM_BOUNDARY_ELEMENTS),
        "feedback_loops": len(FEEDBACK_LOOPS),
        "causal_assumptions": len(CAUSAL_ASSUMPTIONS),
        "ethics_gates": len(ETHICS_GATES),
    }


def governance_score() -> float:
    """Return the fraction of governance records with gates and source anchors."""
    records: tuple[GovernanceRecord, ...] = (
        *SYSTEM_BOUNDARY_ELEMENTS,
        *FEEDBACK_LOOPS,
        *CAUSAL_ASSUMPTIONS,
        *ETHICS_GATES,
    )
    complete = 0
    for record in records:
        values = tuple(value for value in record.__dict__.values() if value != record.key)
        if all(values) and record.source_keys:
            complete += 1
    return complete / len(records)
