from pathlib import Path
import re

import numpy as np

from evidence import (
    adjacency,
    build_evidence_graph,
    citation_keys,
    domain_dimension_edges,
    evidence_coverage,
    is_acyclic,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _bib_keys() -> set[str]:
    text = (PROJECT_ROOT / "manuscript" / "references.bib").read_text()
    return set(re.findall(r"@\w+\{([^,]+),", text))


def test_evidence_graph_shape_and_coverage():
    graph = build_evidence_graph()
    assert len(graph["domains"]) == 5
    assert len(graph["dimensions"]) >= 10
    assert "systems_governance" in graph["dimensions"]
    assert 0.0 <= evidence_coverage() <= 1.0
    assert evidence_coverage() == 1.0


def test_edges_have_declared_endpoints_and_graph_is_acyclic():
    graph = build_evidence_graph()
    nodes = set(graph["nodes"])
    assert all(src in nodes and dst in nodes for src, dst in domain_dimension_edges())
    assert is_acyclic()


def test_evidence_citations_exist_in_bibliography():
    assert citation_keys() <= _bib_keys()


def test_adjacency_is_square_symmetric():
    matrix = adjacency()
    assert matrix.shape[0] == matrix.shape[1]
    np.testing.assert_allclose(matrix, matrix.T)
