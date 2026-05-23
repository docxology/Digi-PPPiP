import numpy as np
import pytest

from narrative import convergence_index, narrative_arc, pivotal_moments, stroke_entropy, surprisal


def test_entropy_constant_and_uniform_cases():
    assert stroke_entropy([1, 1, 1]) == 0.0
    assert np.isclose(stroke_entropy([0, 1, 2, 3]), np.log2(4))


def test_surprisal_and_pivotal_moments():
    sequence = [0] * 10 + [1]
    s = surprisal(sequence)
    assert len(s) == len(sequence)
    assert pivotal_moments(sequence, z=1.0).tolist() == [10]


def test_convergence_index_monotone_when_entropy_declines():
    sequence = [0, 1, 2, 3, 0, 1, 0, 1, 0, 0, 0, 0]
    index = convergence_index(sequence, window=4)
    assert np.all(np.diff(index) >= 0)


def test_narrative_arc_covers_sequence():
    arc = narrative_arc([0, 0, 0, 1, 0])
    assert arc["rising"][0] == 0
    assert arc["resolution"][1] == 4
    assert arc["twist"][0] == arc["twist"][1]


def test_empty_inputs_raise():
    for fn in (stroke_entropy, surprisal, pivotal_moments, convergence_index, narrative_arc):
        with pytest.raises(ValueError):
            fn([])
