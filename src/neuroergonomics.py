"""Neuroergonomics of DigiPPPiP: flow, technoference, attention.

Operationalizes the challenge-skill flow channel
(Csikszentmihalyi), a technoference cost that degrades shared attention with
interruptions, the gain from intentional enclosure (notification suppression),
and an attention-allocation simplex. Pure (numpy + stdlib).
"""

from __future__ import annotations

import math

import numpy as np


def flow_state(challenge: float, skill: float, margin: float = 0.15) -> str:
    """Classify the challenge–skill balance into the flow channel.

    Returns ``"anxiety"`` (challenge ≫ skill), ``"boredom"`` (skill ≫
    challenge), or ``"flow"`` (balanced within ``margin``).

    Raises:
        ValueError: if ``challenge``/``skill`` < 0 or ``margin`` < 0.
    """
    if challenge < 0 or skill < 0 or margin < 0:
        raise ValueError("challenge, skill, margin must be non-negative")
    if challenge - skill > margin:
        return "anxiety"
    if skill - challenge > margin:
        return "boredom"
    return "flow"


def technoference_cost(interruptions: int, lambda_: float = 0.35) -> float:
    """Relational-attention cost ``1 - exp(-λ·interruptions)`` in ``[0, 1)``.

    Strictly increasing in ``interruptions`` for ``λ > 0`` (each technology
    interruption erodes shared presence with diminishing marginal damage).

    Raises:
        ValueError: if ``interruptions`` < 0 or ``lambda_`` ≤ 0.
    """
    if interruptions < 0:
        raise ValueError("interruptions must be non-negative")
    if lambda_ <= 0:
        raise ValueError("lambda_ must be positive")
    return float(1.0 - math.exp(-lambda_ * interruptions))


def intentional_enclosure_gain(suppression: float, k: float = 3.0) -> float:
    """Recovered shared-attention gain from notification suppression.

    ``1 - exp(-k·suppression)`` for ``suppression ∈ [0, 1]`` — monotone
    increasing, in ``[0, 1)``.

    Raises:
        ValueError: if ``suppression`` ∉ ``[0, 1]`` or ``k`` ≤ 0.
    """
    if not (0.0 <= suppression <= 1.0):
        raise ValueError("suppression must be in [0, 1]")
    if k <= 0:
        raise ValueError("k must be positive")
    return float(1.0 - math.exp(-k * suppression))


def attention_allocation(weights: list[float] | None = None) -> np.ndarray:
    """Normalize non-negative attention weights onto the probability simplex.

    Default channels: [partner's marks, own marks, the shared canvas].

    Raises:
        ValueError: if any weight is negative or all weights are zero.
    """
    w = np.asarray([0.45, 0.20, 0.35] if weights is None else weights, dtype=float)
    if np.any(w < 0):
        raise ValueError("weights must be non-negative")
    total = w.sum()
    if total == 0:
        raise ValueError("weights must not be all zero")
    return np.asarray(w / total, dtype=float)
