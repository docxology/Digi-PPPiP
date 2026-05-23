"""Active-inference account of aesthetic experience (the epistemic arc).

Operationalizes the felt arc of a DigiPPPiP session
as curiosity → epistemic action → "aha". Expected information gain rises then
falls (a single interior peak); ``order_change_balance`` formalizes the
Wundt-curve trade-off between order and novelty. Pure (numpy + stdlib).
"""

from __future__ import annotations

import numpy as np


def epistemic_arc(steps: int, curiosity: float = 1.0, precision: float = 0.6) -> np.ndarray:
    """Expected-information-gain trajectory over a session of ``steps`` marks.

    ``EIG(t) = curiosity · t · exp(-precision · t)`` for ``t = 1 … steps`` — a
    gamma-shaped curve with a single interior maximum near ``t = 1/precision``
    (curiosity, epistemic action, then the resolving "aha").

    Raises:
        ValueError: if ``steps < 1`` or ``curiosity``/``precision`` ≤ 0.
    """
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if curiosity <= 0 or precision <= 0:
        raise ValueError("curiosity and precision must be positive")
    t = np.arange(1, steps + 1, dtype=float)
    return np.asarray(curiosity * t * np.exp(-precision * t), dtype=float)


def aha_magnitude(arc: np.ndarray) -> float:
    """Peak expected-information-gain minus the opening baseline (``≥ 0``)."""
    a = np.asarray(arc, dtype=float)
    if a.size == 0:
        raise ValueError("arc must be non-empty")
    return float(a.max() - a[0])


def peak_step(arc: np.ndarray) -> int:
    """Index of the "aha" — the arc's maximum."""
    a = np.asarray(arc, dtype=float)
    if a.size == 0:
        raise ValueError("arc must be non-empty")
    return int(np.argmax(a))


def order_change_balance(order: float, change: float) -> float:
    """Wundt-curve balance ``1 - |order - change|`` in ``[0, 1]``.

    Maximized (``= 1``) at the documented balance point ``order == change`` —
    the controlled-novelty sweet spot the framework places at the centre of
    PPPiP's relational value.

    Raises:
        ValueError: if ``order`` or ``change`` is outside ``[0, 1]``.
    """
    if not (0.0 <= order <= 1.0) or not (0.0 <= change <= 1.0):
        raise ValueError("order and change must be in [0, 1]")
    return float(1.0 - abs(order - change))
