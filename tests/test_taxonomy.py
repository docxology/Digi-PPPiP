import numpy as np
import pytest

import figures
from taxonomy import AFFORDANCES, SpatialConfig, TemporalMode, build_taxonomy, recommend_modality, taxonomy_matrix


def test_taxonomy_is_three_by_three_with_unique_cells():
    modalities = build_taxonomy()
    assert len(TemporalMode) == 3
    assert len(SpatialConfig) == 3
    assert len(modalities) == 9
    assert len({(m.temporal, m.spatial) for m in modalities}) == 9


def test_affordance_scores_are_bounded():
    for modality in build_taxonomy():
        assert set(modality.affordances) == set(AFFORDANCES)
        assert all(0.0 <= score <= 1.0 for score in modality.affordances.values())


def test_recommend_modality_is_deterministic_argmax():
    weights = {"geographic_reach": 1.0, "reflective_pacing": 0.8}
    first = recommend_modality(weights)
    second = recommend_modality(weights)
    assert first == second
    assert first.name == "Persistent canvas (Miro/Mural)"


def test_recommend_modality_rejects_unknown_key():
    with pytest.raises(ValueError):
        recommend_modality({"unknown": 1.0})


def test_taxonomy_matrix_shape_and_validation():
    matrix = taxonomy_matrix("neural_synchrony")
    assert matrix.shape == (3, 3)
    assert np.isclose(matrix.max(), 0.95)
    with pytest.raises(ValueError):
        taxonomy_matrix("not_an_affordance")


def test_taxonomy_cell_labels_wrap_within_matrix_bounds():
    for modality in build_taxonomy():
        lines = figures.taxonomy_cell_label_lines(modality.name)
        assert 1 <= len(lines) <= 3
        assert all(line.strip() for line in lines)
        assert all(len(line) <= 20 for line in lines)
        assert "\n".join(lines).count("+") == modality.name.count("+")
