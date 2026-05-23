from figure_methods import (
    aesthetic_grammar_rules,
    aesthetic_palette,
    caption_contract_items,
    composition_archetypes,
    contrast_ratio,
    contrast_requirements,
    figure_audit_criteria,
    figure_generation_stages,
    figure_method_counts,
    figure_method_source_families,
    figure_method_source_keys,
    figure_method_score,
    visual_encoding_channels,
)


def test_figure_generation_stages_are_ordered_and_gated():
    stages = figure_generation_stages()
    keys = [stage.key for stage in stages]
    assert keys == [
        "claim_scope",
        "method_lineage",
        "tested_primitive",
        "visual_encoding",
        "deterministic_render",
        "registry",
        "caption_reference",
        "accessibility_description",
        "render_validation",
    ]
    assert len(keys) == len(set(keys))
    assert all(stage.artifact and stage.quality_gate for stage in stages)
    assert all(0.0 <= stage.score <= 1.0 for stage in stages)


def test_figure_audit_criteria_are_complete_and_scored():
    criteria = figure_audit_criteria()
    keys = {criterion.key for criterion in criteria}
    assert {
        "deterministic_inputs",
        "registry_entry",
        "caption_contract",
        "claim_boundary",
        "source_alignment",
        "method_lineage",
        "accessibility_text",
        "legend_axis_integrity",
        "aesthetic_accessibility",
        "text_fit_readability",
        "render_resolution",
        "auto_numbered_refs",
        "claim_status_visible",
    } == keys
    assert all(criterion.status == "required" for criterion in criteria)
    assert all(0.0 <= criterion.score <= 1.0 for criterion in criteria)
    assert figure_method_score() == 1.0


def test_visual_encoding_channels_cover_semantic_roles():
    channels = visual_encoding_channels()
    roles = {channel.role for channel in channels}
    assert roles == {"actors", "artifacts", "signals", "contexts", "evidence", "models", "caveats"}
    assert all(channel.semantic_target and channel.visual_channel and channel.guardrail for channel in channels)


def test_aesthetic_grammar_has_palette_non_color_channels_and_accessibility_constraints():
    palette = aesthetic_palette()
    rules = aesthetic_grammar_rules()
    roles = {channel.role for channel in visual_encoding_channels()}

    assert {rule.role for rule in rules} == roles
    assert all(rule.palette_key in palette for rule in rules)
    assert all(rule.color_hex == palette[rule.palette_key] for rule in rules)
    assert all(rule.non_color_channel and rule.accessibility_constraint for rule in rules)
    assert all(rule.intensity_level in {"medium", "high"} for rule in rules)
    assert all("color alone" not in rule.accessibility_constraint.lower() for rule in rules)


def test_composition_archetypes_cover_method_source_families():
    archetypes = composition_archetypes()
    families = figure_method_source_families()

    assert {archetype.source_family for archetype in archetypes} == {family.key for family in families}
    assert all(archetype.archetype and archetype.layout_rule for archetype in archetypes)
    assert all(archetype.annotation_density in {"moderate", "dense"} for archetype in archetypes)
    assert all(archetype.accessibility_constraint for archetype in archetypes)


def test_contrast_requirements_are_explicit_and_met():
    requirements = contrast_requirements()

    assert {requirement.key for requirement in requirements} == {
        "body_text",
        "matrix_cell_label",
        "blue_badge",
        "green_badge",
        "caveat_badge",
    }
    assert all(requirement.non_color_backup for requirement in requirements)
    assert all(
        contrast_ratio(requirement.foreground, requirement.background) >= requirement.minimum_ratio
        for requirement in requirements
    )


def test_caption_contract_matches_manuscript_needs():
    items = caption_contract_items()
    joined = " ".join(items)
    assert "encodes" in joined
    assert "code module or data source" in joined
    assert "method lineage" in joined
    assert "manuscript argument" in joined
    assert "marks, axes, or panels" in joined
    assert "conceptual, protocol, audit, analytic simulation, or empirical placeholder" in joined
    assert "caveat" in joined
    assert "future evidence" in joined


def test_figure_method_source_families_are_mapped_to_citekeys():
    families = figure_method_source_families()
    keys = {family.key for family in families}
    source_keys = figure_method_source_keys()
    assert keys == {
        "shared_workspace",
        "research_through_design",
        "visualization_reproducibility",
        "accessible_visual_media",
        "privacy_values",
    }
    assert all(family.source_keys for family in families)
    assert all(family.method_role and family.quality_gate for family in families)
    assert "zimmerman2007rtd" in source_keys
    assert "lundgard2022accessible" in source_keys
    assert {"w3c2024altdecisiontree", "crameri2020colour"} <= source_keys
    assert {"oittinen2025videodrawing", "elavsky2024datanavigator", "jones2024customization"} <= source_keys


def test_figure_method_counts_are_single_source():
    counts = figure_method_counts()
    assert counts == {
        "generation_stages": len(figure_generation_stages()),
        "audit_criteria": len(figure_audit_criteria()),
        "visual_roles": len(visual_encoding_channels()),
        "aesthetic_roles": len(aesthetic_grammar_rules()),
        "composition_archetypes": len(composition_archetypes()),
        "contrast_requirements": len(contrast_requirements()),
        "method_source_families": len(figure_method_source_families()),
        "caption_contract_items": len(caption_contract_items()),
    }
