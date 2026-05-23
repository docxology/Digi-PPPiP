"""Outcome-measure primitives for DigiPPPiP study design."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OutcomeMeasure:
    """One candidate outcome measure and its evidentiary role."""

    key: str
    domain: str
    label: str
    instrument: str
    claim_level: str


@dataclass(frozen=True)
class OutcomeModel:
    """A reproducible mixed-model design descriptor."""

    dependent_variable: str
    fixed_effects: tuple[str, ...]
    random_effects: tuple[str, ...]
    formula: str


OUTCOME_MEASURES: tuple[OutcomeMeasure, ...] = (
    OutcomeMeasure(
        "relationship_quality",
        "relational",
        "relationship quality",
        "brief dyadic relationship questionnaire",
        "hypothesis",
    ),
    OutcomeMeasure(
        "shared_meaning",
        "narrative",
        "shared meaning",
        "post-session co-meaning rating",
        "hypothesis",
    ),
    OutcomeMeasure(
        "flow",
        "neuroergonomic",
        "flow",
        "challenge-skill flow scale",
        "design_rationale",
    ),
    OutcomeMeasure(
        "inter_brain_synchrony",
        "neurophysiological",
        "inter-brain synchrony",
        "fNIRS or EEG hyperscanning metric",
        "correlate",
    ),
    OutcomeMeasure(
        "access_success",
        "accessibility",
        "access success",
        "participant-defined task completion and comfort",
        "design_rationale",
    ),
    OutcomeMeasure(
        "place_attachment",
        "place",
        "place attachment",
        "place-responsive prompt comparison",
        "hypothesis",
    ),
)


def outcome_domains() -> tuple[str, ...]:
    """Return sorted unique outcome domains."""
    return tuple(sorted({measure.domain for measure in OUTCOME_MEASURES}))


def measures_by_domain(domain: str) -> tuple[OutcomeMeasure, ...]:
    """Return all measures in *domain*.

    Raises:
        ValueError: if no measure uses the requested domain.
    """
    matches = tuple(measure for measure in OUTCOME_MEASURES if measure.domain == domain)
    if not matches:
        raise ValueError(f"unknown outcome domain: {domain!r}")
    return matches


def multilevel_model_spec(dependent_variable: str = "shared_meaning") -> OutcomeModel:
    """Return the default mixed-model specification for staged studies."""
    known = {measure.key for measure in OUTCOME_MEASURES}
    if dependent_variable not in known:
        raise ValueError(f"unknown dependent variable: {dependent_variable!r}")
    fixed = ("temporal_mode", "spatial_config", "session_phase", "access_condition")
    random = ("dyad_id", "participant_id")
    formula = (
        f"{dependent_variable} ~ temporal_mode * spatial_config + session_phase "
        "+ access_condition + (1 | dyad_id) + (1 | participant_id)"
    )
    return OutcomeModel(
        dependent_variable=dependent_variable,
        fixed_effects=fixed,
        random_effects=random,
        formula=formula,
    )


def design_claim_strength(sample_size: int, randomized: bool, longitudinal: bool) -> str:
    """Classify the strongest claim supported by a planned study design."""
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if randomized and longitudinal and sample_size >= 80:
        return "causal_candidate"
    if randomized and sample_size >= 40:
        return "comparative"
    if sample_size >= 20:
        return "associational"
    return "descriptive"


def measurement_coverage(selected_keys: set[str]) -> float:
    """Return the fraction of outcome domains represented by *selected_keys*."""
    if not selected_keys:
        return 0.0
    selected_domains = {
        measure.domain for measure in OUTCOME_MEASURES if measure.key in selected_keys
    }
    return len(selected_domains) / len(outcome_domains())
