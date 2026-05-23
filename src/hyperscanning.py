"""Inter-brain synchrony and geometric hyperscanning.

Operationalizes Sections 3 & 4: a modular inter-brain-synchrony (IBS) time
series segmented into four session phases, Forman–Ricci curvature of the
inter-brain network, and curvature entropy as an affective-phase-transition
proxy. Pure (numpy + stdlib); Forman–Ricci uses the closed form for unweighted
simple graphs, so no graph library is required.

Conceptual model only — not an empirical hyperscanning measurement.
"""

from __future__ import annotations

import numpy as np

PHASES: tuple[str, ...] = ("initiation", "elaboration", "convergence", "completion")
# Phase fractions of the session and the IBS plateau each phase entrains to.
_PHASE_FRACTIONS = (0.20, 0.35, 0.30, 0.15)
_PHASE_LEVELS = {"initiation": 0.30, "elaboration": 0.55, "convergence": 0.85, "completion": 0.65}


def _phase_lengths(steps: int) -> list[int]:
    lengths = [int(round(f * steps)) for f in _PHASE_FRACTIONS[:-1]]
    lengths.append(steps - sum(lengths))  # last phase absorbs the remainder
    return lengths


def simulate_ibs_phases(steps: int = 120, seed: int = 0) -> dict[str, np.ndarray]:
    """Simulate a phase-segmented inter-brain-synchrony time series.

    Returns:
        ``{"ibs": ndarray[steps], "phase": ndarray[steps] of str}``. Phase
        block lengths sum exactly to ``steps``; mean IBS rises from
        ``initiation`` to ``convergence``.

    Raises:
        ValueError: if ``steps <= 0``.
    """
    if steps <= 0:
        raise ValueError("steps must be positive")
    # A single shared offset is added to every phase plateau, so inter-phase
    # mean differences are seed-invariant and EXACT (the offset cancels):
    # mean(convergence) - mean(initiation) == 0.85 - 0.30 == 0.55, never flaky.
    offset = 0.01 * float(np.random.default_rng(seed).random())
    lengths = _phase_lengths(steps)
    ibs = np.zeros(steps, dtype=float)
    phase = np.empty(steps, dtype=object)
    idx = 0
    for name, length in zip(PHASES, lengths):
        ibs[idx : idx + length] = _PHASE_LEVELS[name] + offset
        phase[idx : idx + length] = name
        idx += length
    return {"ibs": ibs, "phase": phase.astype(str)}


def _validate_adjacency(adj: np.ndarray) -> np.ndarray:
    a = np.asarray(adj, dtype=float)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError(f"adjacency must be square, got shape {a.shape}")
    if not np.allclose(a, a.T):
        raise ValueError("adjacency must be symmetric (undirected graph)")
    return a


def forman_ricci_curvature(adj: np.ndarray) -> np.ndarray:
    """Forman–Ricci curvature per undirected edge of an unweighted graph.

    For a simple unweighted graph the closed form is
    ``Fr(uv) = 4 - deg(u) - deg(v)``. Edges are enumerated in ascending
    ``(i, j)`` order with ``i < j`` and ``adj[i, j] != 0``.

    Raises:
        ValueError: if *adj* is not square or not symmetric.
    """
    a = _validate_adjacency(adj)
    degrees = (a != 0).sum(axis=1)
    curv: list[float] = []
    n = a.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if a[i, j] != 0:
                curv.append(4.0 - degrees[i] - degrees[j])
    return np.asarray(curv, dtype=float)


def curvature_entropy(curvatures: np.ndarray) -> float:
    """Shannon entropy (bits) of the curvature value distribution.

    Zero for a single-valued vector; non-negative in general. An empty input
    yields 0.0 (no information).
    """
    curv = np.asarray(curvatures, dtype=float)
    if curv.size == 0:
        return 0.0
    _, counts = np.unique(curv, return_counts=True)
    probs = counts / counts.sum()
    return float(-np.sum(probs * np.log2(probs)))


def detect_phase_transitions(entropy_series: np.ndarray, threshold: float) -> np.ndarray:
    """Indices ``i`` where ``|series[i] - series[i-1]| > threshold``.

    Returns an empty array on a constant series and ≥1 index on a step series.

    Raises:
        ValueError: if ``threshold < 0``.
    """
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    series = np.asarray(entropy_series, dtype=float)
    if series.size < 2:
        return np.asarray([], dtype=int)
    deltas = np.abs(np.diff(series))
    return np.where(deltas > threshold)[0] + 1


def inter_brain_network(t: int, n: int = 8, seed: int = 0) -> np.ndarray:
    """Deterministic symmetric 0/1 inter-brain adjacency at session step ``t``.

    Edge density tracks a session-phase signal (denser mid-session, sparser at
    the ends), so curvature → :func:`curvature_entropy` over a sweep of ``t``
    yields a non-trivial affective-phase-transition proxy. Deterministic given
    ``(t, n, seed)``; zero diagonal.

    Raises:
        ValueError: if ``n < 2``.
    """
    if n < 2:
        raise ValueError("n must be at least 2")
    rng = np.random.default_rng(seed)
    base = rng.random((n, n))
    base = np.triu(base, 1)
    base = base + base.T
    density = 0.25 + 0.45 * np.sin(np.pi * (t % 20) / 20.0) ** 2
    adj = (base < density).astype(float)
    np.fill_diagonal(adj, 0.0)
    return np.asarray(adj, dtype=float)
