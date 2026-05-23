"""Accessibility audit primitives for DigiPPPiP."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AccessibilityCriterion:
    """One accessibility criterion with required implementation capabilities."""

    key: str
    domain: str
    label: str
    required_capabilities: frozenset[str]
    weight: float = 1.0


@dataclass(frozen=True)
class AccessibilityAudit:
    """Weighted accessibility audit result."""

    score: float
    passed: tuple[str, ...]
    missing: tuple[str, ...]


CRITERIA: tuple[AccessibilityCriterion, ...] = (
    AccessibilityCriterion(
        "multimodal_input",
        "input",
        "multiple input channels",
        frozenset({"stylus", "touch", "keyboard", "switch", "voice"}),
        1.2,
    ),
    AccessibilityCriterion(
        "perceptual_feedback",
        "feedback",
        "multiple feedback channels",
        frozenset({"high_contrast", "audio_description", "haptic_feedback"}),
        1.0,
    ),
    AccessibilityCriterion(
        "plain_language",
        "cognition",
        "plain-language controls",
        frozenset({"plain_language", "low_distraction_mode"}),
        0.8,
    ),
    AccessibilityCriterion(
        "consent_archive",
        "privacy",
        "consentful archive controls",
        frozenset({"save_consent", "delete_control", "replay_control"}),
        1.3,
    ),
    AccessibilityCriterion(
        "partner_mediation",
        "relational",
        "partner-mediated contribution",
        frozenset({"assisted_drawing", "role_switching"}),
        0.9,
    ),
)


NEED_TO_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "low_vision": ("high_contrast", "audio_description"),
    "motor_variability": ("switch", "voice", "assisted_drawing"),
    "cognitive_load": ("plain_language", "low_distraction_mode"),
    "privacy_concern": ("save_consent", "delete_control", "replay_control"),
}


def criterion_score(criterion: AccessibilityCriterion, capabilities: set[str]) -> float:
    """Return fractional support for one criterion in ``[0, 1]``."""
    if not criterion.required_capabilities:
        return 1.0
    matched = criterion.required_capabilities & capabilities
    return len(matched) / len(criterion.required_capabilities)


def audit_capabilities(capabilities: set[str]) -> AccessibilityAudit:
    """Audit implementation capabilities against the project criteria."""
    if not capabilities:
        return AccessibilityAudit(score=0.0, passed=(), missing=tuple(c.key for c in CRITERIA))
    weighted_total = sum(criterion.weight for criterion in CRITERIA)
    weighted_score = 0.0
    passed: list[str] = []
    missing: list[str] = []
    for criterion in CRITERIA:
        score = criterion_score(criterion, capabilities)
        weighted_score += criterion.weight * score
        if score >= 1.0:
            passed.append(criterion.key)
        else:
            missing.append(criterion.key)
    return AccessibilityAudit(
        score=float(weighted_score / weighted_total),
        passed=tuple(passed),
        missing=tuple(missing),
    )


def accommodation_plan(needs: set[str]) -> tuple[str, ...]:
    """Map participant needs to implementation capabilities.

    Raises:
        ValueError: if an unknown need is requested.
    """
    unknown = needs - set(NEED_TO_CAPABILITIES)
    if unknown:
        raise ValueError(f"unknown accessibility need(s): {sorted(unknown)}")
    capabilities: set[str] = set()
    for need in needs:
        capabilities.update(NEED_TO_CAPABILITIES[need])
    return tuple(sorted(capabilities))


def domain_scores(capabilities: set[str]) -> dict[str, float]:
    """Return criterion support averaged by accessibility domain."""
    scores: dict[str, list[float]] = {}
    for criterion in CRITERIA:
        scores.setdefault(criterion.domain, []).append(criterion_score(criterion, capabilities))
    return {
        domain: sum(values) / len(values)
        for domain, values in sorted(scores.items())
    }
