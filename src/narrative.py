"""Narrative information theory over a DigiPPPiP stroke sequence.

Operationalizes a drawing session as a symbol sequence (stroke
classes); Shannon entropy, per-symbol surprisal, pivotal moments, a
convergence index, and a rising/twist/resolution arc characterize it as a
narrative artifact. Pure (numpy + stdlib).
"""

from __future__ import annotations

from collections import Counter

import numpy as np


def _counts(seq: list[int]) -> tuple[np.ndarray, dict[int, float]]:
    if len(seq) == 0:
        raise ValueError("sequence must be non-empty")
    counter = Counter(seq)
    total = len(seq)
    probs = {sym: c / total for sym, c in counter.items()}
    return np.array([probs[s] for s in seq], dtype=float), probs


def stroke_entropy(seq: list[int]) -> float:
    """Shannon entropy (bits) of the stroke-symbol distribution.

    ``0`` for a constant sequence; ``log2(k)`` for a uniform alphabet of size
    ``k``.

    Raises:
        ValueError: if *seq* is empty.
    """
    _, probs = _counts(list(seq))
    p = np.array(list(probs.values()), dtype=float)
    return float(-np.sum(p * np.log2(p)))


def surprisal(seq: list[int]) -> np.ndarray:
    """Per-symbol surprisal ``-log2 p(symbol)``; length equals ``len(seq)``.

    Raises:
        ValueError: if *seq* is empty.
    """
    p_each, _ = _counts(list(seq))
    return np.asarray(-np.log2(p_each), dtype=float)


def pivotal_moments(seq: list[int], z: float = 1.0) -> np.ndarray:
    """Indices whose surprisal z-score exceeds ``z`` (the plot-twist proxy).

    A sequence with uniform surprisal (zero std) has no pivotal moments.

    Raises:
        ValueError: if *seq* is empty.
    """
    s = surprisal(seq)
    std = s.std()
    if std == 0:
        return np.asarray([], dtype=int)
    zscores = (s - s.mean()) / std
    return np.where(zscores > z)[0]


def convergence_index(seq: list[int], window: int = 10) -> np.ndarray:
    """Per-window convergence ``1 - H_window / log2(alphabet)``.

    Monotone-nondecreasing whenever windowed entropy is non-increasing (the
    session converges on a shared motif). Returns one value per full window.

    Raises:
        ValueError: if *seq* is empty or ``window < 1``.
    """
    s = list(seq)
    if len(s) == 0:
        raise ValueError("sequence must be non-empty")
    if window < 1:
        raise ValueError("window must be >= 1")
    alphabet = len(set(s))
    h_max = np.log2(alphabet) if alphabet > 1 else 1.0
    out: list[float] = []
    for start in range(0, len(s) - window + 1, window):
        block = s[start : start + window]
        out.append(1.0 - stroke_entropy(block) / h_max)
    return np.asarray(out, dtype=float)


def narrative_arc(seq: list[int]) -> dict[str, tuple[int, int]]:
    """Rising / twist / resolution segment boundaries covering the sequence.

    The twist is the global surprisal peak; ``rising`` spans the prefix up to
    it, ``resolution`` the suffix after it. Segments tile ``[0, len(seq)-1]``.

    Raises:
        ValueError: if *seq* is empty.
    """
    s = surprisal(seq)
    n = len(s)
    twist = int(np.argmax(s))
    return {
        "rising": (0, twist),
        "twist": (twist, twist),
        "resolution": (twist, n - 1),
    }
