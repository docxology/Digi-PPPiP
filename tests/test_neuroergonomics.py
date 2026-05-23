import numpy as np
import pytest

from neuroergonomics import attention_allocation, flow_state, intentional_enclosure_gain, technoference_cost


def test_flow_state_boundaries():
    assert flow_state(0.8, 0.8) == "flow"
    assert flow_state(1.0, 0.5) == "anxiety"
    assert flow_state(0.4, 0.8) == "boredom"


def test_technoference_cost_is_increasing():
    costs = [technoference_cost(i) for i in range(5)]
    assert np.all(np.diff(costs) > 0)


def test_intentional_enclosure_gain_is_bounded_and_increasing():
    gains = [intentional_enclosure_gain(x) for x in (0.0, 0.5, 1.0)]
    assert all(0.0 <= g <= 1.0 for g in gains)
    assert gains[0] < gains[1] < gains[2]


def test_attention_allocation_is_simplex():
    weights = attention_allocation([1.0, 2.0, 3.0])
    assert np.all(weights >= 0.0)
    assert np.isclose(weights.sum(), 1.0)


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        flow_state(-1, 0)
    with pytest.raises(ValueError):
        technoference_cost(-1)
    with pytest.raises(ValueError):
        intentional_enclosure_gain(1.5)
    with pytest.raises(ValueError):
        attention_allocation([0, 0, 0])
