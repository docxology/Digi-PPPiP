import numpy as np
import pytest

from active_inference import belief_update, posterior_mean, simulate_dyadic_session, variational_free_energy


def test_free_energy_is_minimized_at_posterior_mean():
    obs, prior, prior_prec, lik_prec = 1.5, 0.2, 1.0, 2.0
    opt = posterior_mean(obs, prior, prior_prec, lik_prec)
    f_opt = variational_free_energy(opt, obs, prior, prior_prec, lik_prec)
    f_left = variational_free_energy(opt - 1e-3, obs, prior, prior_prec, lik_prec)
    f_right = variational_free_energy(opt + 1e-3, obs, prior, prior_prec, lik_prec)
    assert f_opt < f_left
    assert f_opt < f_right


def test_belief_update_reduces_free_energy_and_moves_toward_observation():
    before = variational_free_energy(0.0, 1.0, 0.0, 1.0, 2.0)
    updated = belief_update(0.0, 1.0, 0.0, 1.0, 2.0, rate=1.0)
    after = variational_free_energy(updated, 1.0, 0.0, 1.0, 2.0)
    assert after < before
    assert 0.0 < updated < 1.0


def test_coupled_session_beats_decoupled_baseline():
    coupled = simulate_dyadic_session(coupled=True, seed=7)
    decoupled = simulate_dyadic_session(coupled=False, seed=7)
    assert coupled["free_energy"].shape == coupled["surprise"].shape
    assert coupled["free_energy"][-1] < decoupled["free_energy"][-1]


def test_session_is_deterministic_for_fixed_seed():
    a = simulate_dyadic_session(seed=3)
    b = simulate_dyadic_session(seed=3)
    np.testing.assert_allclose(a["free_energy"], b["free_energy"], atol=1e-12)
    np.testing.assert_allclose(a["surprise"], b["surprise"], atol=1e-12)


def test_invalid_parameters_raise():
    with pytest.raises(ValueError):
        simulate_dyadic_session(steps=0)
    with pytest.raises(ValueError):
        variational_free_energy(0.0, 1.0, 0.0, 0.0, 1.0)
    with pytest.raises(ValueError):
        belief_update(0.0, 1.0, 0.0, 1.0, 2.0, rate=2.0)
