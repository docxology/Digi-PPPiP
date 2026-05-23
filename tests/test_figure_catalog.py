from figure_catalog import (
    FIGURE_CLAIM_STATUSES,
    FIGURE_PLACEMENTS,
    FigureSpec,
    figure_count,
    figure_generator_names,
    figure_long_description_map,
    figure_specs,
    missing_figure_specs,
)
from figure_methods import figure_method_source_families


def test_figure_specs_cover_all_generators_with_typed_contracts():
    specs = figure_specs()
    generators = figure_generator_names()

    assert figure_count() == 35
    assert len(specs) == figure_count()
    assert all(isinstance(spec, FigureSpec) for spec in specs)
    assert tuple(spec.generator for spec in specs) == generators
    assert not missing_figure_specs(generators)
    assert len({spec.label for spec in specs}) == figure_count()
    assert len({spec.filename for spec in specs}) == figure_count()
    assert len({spec.generator for spec in specs}) == figure_count()
    assert all(spec.label.startswith("fig:") for spec in specs)
    assert all(spec.filename.endswith(".png") for spec in specs)
    assert all(spec.section for spec in specs)
    assert all(spec.accessibility_description for spec in specs)
    assert all(spec.claim_status in FIGURE_CLAIM_STATUSES for spec in specs)
    assert all(spec.placement in FIGURE_PLACEMENTS for spec in specs)


def test_figure_specs_use_split_claim_statuses_and_method_source_families():
    specs = figure_specs()
    statuses = {spec.claim_status for spec in specs}
    source_families = {family.key for family in figure_method_source_families()}

    assert statuses == {
        "conceptual",
        "protocol",
        "audit",
        "analytic_simulation",
        "empirical_placeholder",
    }
    assert {spec.method_source_family for spec in specs} <= source_families
    assert {"main"} <= {spec.placement for spec in specs}
    assert {"fig:source_verification_readiness", "fig:study_readiness_matrix"} <= {
        spec.label for spec in specs
    }


def test_architecture_and_data_flow_figures_expose_governed_boundaries():
    specs = {spec.label: spec for spec in figure_specs()}

    architecture = specs["fig:cpss_architecture"].accessibility_description
    event_flow = specs["fig:event_logging_schema"].accessibility_description

    assert "human-human drawing kernel" in architecture
    assert "optional AI branch" in architecture
    assert "publication-governance evidence boundary" in architecture
    assert "human marks" in event_flow
    assert "model diagnostics" in event_flow
    assert "template publication artifacts" in event_flow


def test_figure_long_description_map_has_one_sidecar_per_spec():
    descriptions = figure_long_description_map()

    assert set(descriptions) == {spec.filename for spec in figure_specs()}
    assert all("Long description" in text for text in descriptions.values())
    assert all("Generator:" in text for text in descriptions.values())
    assert all("Claim status:" in text for text in descriptions.values())
    assert all("Method-source family:" in text for text in descriptions.values())
    assert all("Reading order:" in text for text in descriptions.values())
    assert all("Caveat:" in text for text in descriptions.values())
    assert all("Evidence boundary:" in text for text in descriptions.values())
