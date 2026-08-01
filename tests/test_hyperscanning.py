import numpy as np
import pytest

from hyperscanning import (
    curvature_entropy,
    detect_phase_transitions,
    forman_ricci_curvature,
    inter_brain_network,
    simulate_ibs_phases,
)


def test_ibs_phases_cover_requested_steps_and_converge_higher():
    session = simulate_ibs_phases(steps=121, seed=4)
    ibs = session["ibs"]
    phase = session["phase"]
    assert len(ibs) == 121
    assert len(phase) == 121
    assert ibs[phase == "convergence"].mean() > ibs[phase == "initiation"].mean()


def test_forman_ricci_path_graph_closed_form():
    path = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)
    np.testing.assert_array_equal(forman_ricci_curvature(path), np.array([1.0, 1.0]))


def test_adjacency_validation():
    with pytest.raises(ValueError):
        forman_ricci_curvature(np.ones((2, 3)))
    with pytest.raises(ValueError):
        forman_ricci_curvature(np.array([[0, 1], [0, 0]], dtype=float))


def test_curvature_entropy_and_transitions():
    assert curvature_entropy(np.array([1, 1, 1])) == 0.0
    assert curvature_entropy(np.array([1, 2, 2, 3])) > 0.0
    assert detect_phase_transitions(np.ones(5), 0.1).size == 0
    assert detect_phase_transitions(np.array([0, 0, 1, 1]), 0.5).tolist() == [2]


def test_inter_brain_network_feeds_curvature_entropy():
    adj = inter_brain_network(3, n=8, seed=0)
    assert adj.shape == (8, 8)
    np.testing.assert_allclose(adj, adj.T)
    assert curvature_entropy(forman_ricci_curvature(adj)) >= 0.0


def test_hyperscanning_edge_cases_raise_or_short_circuit():
    with pytest.raises(ValueError):
        simulate_ibs_phases(steps=0)
    with pytest.raises(ValueError):
        inter_brain_network(1, n=1)
    with pytest.raises(ValueError):
        detect_phase_transitions(np.ones(3), threshold=-1)
    # Empty curvature vector -> 0.0 bits; short series -> no transitions.
    assert curvature_entropy(np.asarray([])) == 0.0
    assert detect_phase_transitions(np.ones(1), 0.1).size == 0
