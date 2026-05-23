"""DigiPPPiP temporal–spatial modality taxonomy.

Operationalizes a 3 (temporal) × 3 (spatial) grid of nine practice modalities,
each scored on seven relational affordances. Pure (numpy + stdlib); no
matplotlib, no infrastructure imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np

AFFORDANCES: tuple[str, ...] = (
    "neural_synchrony",
    "reflective_pacing",
    "haptic_richness",
    "geographic_reach",
    "accessibility",
    "place_grounding",
    "narrative_memory",
)


class TemporalMode(Enum):
    """Temporal structure of a DigiPPPiP session."""

    SYNCHRONOUS = "synchronous"
    SEMISYNCHRONOUS = "semisynchronous"
    ASYNCHRONOUS = "asynchronous"


class SpatialConfig(Enum):
    """Spatial configuration of a DigiPPPiP session."""

    CO_LOCATED_PHYSICAL = "co_located_physical"
    REMOTE_DIGITAL = "remote_digital"
    CYBERPHYSICAL_HYBRID = "cyberphysical_hybrid"


@dataclass(frozen=True)
class Modality:
    """One taxonomy cell: a (temporal, spatial) practice with affordance scores."""

    temporal: TemporalMode
    spatial: SpatialConfig
    name: str
    affordances: dict[str, float] = field(default_factory=dict)


# Affordance design (each in [0, 1]) follows the framework taxonomy prose:
#   synchronous  -> high neural synchrony; asynchronous -> reflective pacing &
#   narrative memory; co-located physical -> haptic richness & place grounding;
#   remote digital -> geographic reach & accessibility; cyberphysical hybrid ->
#   balanced, place-aware.
_T = TemporalMode
_S = SpatialConfig
# Each entry: (temporal, spatial) -> (name, 7-tuple of affordance scores in
# AFFORDANCES order). Scores in [0, 1].
_GRID: dict[tuple[TemporalMode, SpatialConfig], tuple[str, tuple[float, ...]]] = {
    (_T.SYNCHRONOUS, _S.CO_LOCATED_PHYSICAL): (
        "Original PPPiP", (0.95, 0.20, 0.95, 0.05, 0.45, 0.90, 0.55),
    ),
    (_T.SYNCHRONOUS, _S.REMOTE_DIGITAL): (
        "Video-call + shared canvas", (0.80, 0.25, 0.30, 0.95, 0.75, 0.25, 0.60),
    ),
    (_T.SYNCHRONOUS, _S.CYBERPHYSICAL_HYBRID): (
        "AR overlay on paper", (0.85, 0.30, 0.70, 0.70, 0.65, 0.70, 0.65),
    ),
    (_T.SEMISYNCHRONOUS, _S.CO_LOCATED_PHYSICAL): (
        "Turn-taking, same room", (0.70, 0.55, 0.90, 0.05, 0.50, 0.85, 0.70),
    ),
    (_T.SEMISYNCHRONOUS, _S.REMOTE_DIGITAL): (
        "Turn-taking shared canvas", (0.60, 0.65, 0.30, 0.90, 0.80, 0.30, 0.75),
    ),
    (_T.SEMISYNCHRONOUS, _S.CYBERPHYSICAL_HYBRID): (
        "Smart paper + live mirror", (0.65, 0.60, 0.65, 0.70, 0.70, 0.65, 0.75),
    ),
    (_T.ASYNCHRONOUS, _S.CO_LOCATED_PHYSICAL): (
        "Sequential physical artifact", (0.30, 0.85, 0.90, 0.10, 0.55, 0.85, 0.90),
    ),
    (_T.ASYNCHRONOUS, _S.REMOTE_DIGITAL): (
        "Persistent canvas (Miro/Mural)", (0.25, 0.95, 0.25, 0.95, 0.85, 0.35, 0.95),
    ),
    (_T.ASYNCHRONOUS, _S.CYBERPHYSICAL_HYBRID): (
        "Photographed/printed exchange", (0.30, 0.90, 0.65, 0.75, 0.75, 0.70, 0.90),
    ),
}


def build_taxonomy() -> list[Modality]:
    """Return the nine DigiPPPiP modalities (3 temporal × 3 spatial).

    Every affordance score is in ``[0, 1]``; (temporal, spatial) keys are unique.
    """
    modalities: list[Modality] = []
    for (temporal, spatial), (name, scores) in _GRID.items():
        affordances = dict(zip(AFFORDANCES, scores))
        modalities.append(Modality(temporal=temporal, spatial=spatial, name=name, affordances=affordances))
    return modalities


def recommend_modality(weights: dict[str, float]) -> Modality:
    """Return the modality maximizing the weighted-affordance utility.

    Args:
        weights: mapping from affordance name to a non-negative weight. Keys
            must be a subset of :data:`AFFORDANCES`.

    Raises:
        ValueError: if *weights* is empty or contains an unknown affordance key.
    """
    if not weights:
        raise ValueError("weights must be a non-empty mapping")
    unknown = set(weights) - set(AFFORDANCES)
    if unknown:
        raise ValueError(f"unknown affordance key(s): {sorted(unknown)}")

    best: Modality | None = None
    best_utility = -np.inf
    for modality in build_taxonomy():
        utility = sum(w * modality.affordances[k] for k, w in weights.items())
        if utility > best_utility:
            best_utility, best = utility, modality
    assert best is not None  # build_taxonomy() is non-empty
    return best


def taxonomy_matrix(affordance: str = "neural_synchrony") -> np.ndarray:
    """Return the 3×3 score matrix for *affordance* (rows temporal, cols spatial).

    Row order follows :class:`TemporalMode`; column order :class:`SpatialConfig`.

    Raises:
        ValueError: if *affordance* is not a known affordance name.
    """
    if affordance not in AFFORDANCES:
        raise ValueError(f"unknown affordance: {affordance!r}")
    temporals = list(TemporalMode)
    spatials = list(SpatialConfig)
    lookup = {(m.temporal, m.spatial): m for m in build_taxonomy()}
    matrix = np.zeros((len(temporals), len(spatials)), dtype=float)
    for i, t in enumerate(temporals):
        for j, s in enumerate(spatials):
            matrix[i, j] = lookup[(t, s)].affordances[affordance]
    return matrix
