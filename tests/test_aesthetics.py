import numpy as np
import pytest

from aesthetics import aha_magnitude, epistemic_arc, order_change_balance, peak_step


def test_epistemic_arc_is_single_peaked_and_deterministic():
    a = epistemic_arc(20, curiosity=1.0, precision=0.3)
    b = epistemic_arc(20, curiosity=1.0, precision=0.3)
    np.testing.assert_allclose(a, b, atol=1e-12)
    peak = peak_step(a)
    assert 0 < peak < len(a) - 1
    assert np.all(np.diff(a[: peak + 1]) >= 0)
    assert np.all(np.diff(a[peak:]) <= 0)


def test_aha_magnitude_and_order_change_balance():
    arc = epistemic_arc(20)
    assert aha_magnitude(arc) >= 0.0
    assert order_change_balance(0.5, 0.5) == 1.0
    assert order_change_balance(0.0, 1.0) == 0.0


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        epistemic_arc(0)
    with pytest.raises(ValueError):
        epistemic_arc(5, curiosity=-1)
    with pytest.raises(ValueError):
        aha_magnitude(np.array([]))
    with pytest.raises(ValueError):
        order_change_balance(-0.1, 0.5)
