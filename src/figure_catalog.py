"""Typed figure contract catalog for DigiPPPiP.

The rendering workflow stays in ``src/figures.py``. This covered module owns the
meaning-bearing figure contract: labels, filenames, sections, claim status,
method-source lineage, accessibility descriptions, and placement.
"""

from __future__ import annotations

from dataclasses import dataclass


FIGURE_CLAIM_STATUSES: frozenset[str] = frozenset(
    {"conceptual", "protocol", "audit", "analytic_simulation", "empirical_placeholder"}
)
FIGURE_PLACEMENTS: frozenset[str] = frozenset({"main", "supplemental"})


@dataclass(frozen=True)
class FigureSpec:
    """One governed manuscript figure contract."""

    label: str
    filename: str
    generator: str
    section: str
    claim_status: str
    method_source_family: str
    accessibility_description: str
    placement: str = "main"


FIGURE_SPECS: tuple[FigureSpec, ...] = (
    FigureSpec(
        "fig:evolution_timeline",
        "evolution_timeline.png",
        "generate_evolution_timeline",
        "introduction",
        "conceptual",
        "research_through_design",
        "Timeline showing the staged conceptual expansion from paper PPPiP to digital, cyberphysical, "
        "neuroergonomic, narrative, and place-responsive DigiPPPiP research commitments.",
    ),
    FigureSpec(
        "fig:conceptual_ecology",
        "conceptual_ecology.png",
        "generate_conceptual_ecology",
        "introduction",
        "conceptual",
        "shared_workspace",
        "Ecology diagram with partners, shared canvas artifacts, event logs, devices, and situated contexts "
        "arranged to show mutual agency through a persistent drawing surface.",
    ),
    FigureSpec(
        "fig:cyberphysical_spectrum",
        "cyberphysical_spectrum.png",
        "generate_cyberphysical_spectrum",
        "cyberphysical",
        "conceptual",
        "shared_workspace",
        "Line-and-area spectrum comparing haptic richness, persistence, geographic reach, and instrumentation "
        "across physical, digital, hybrid, AR, VR, and asynchronous modes.",
    ),
    FigureSpec(
        "fig:cpss_architecture",
        "cpss_architecture.png",
        "generate_cpss_architecture",
        "cyberphysical",
        "conceptual",
        "shared_workspace",
        "System-architecture diagram separating the human-human drawing kernel, instrumentation support, "
        "computed modeling lens, optional AI branch, and publication-governance evidence boundary.",
    ),
    FigureSpec(
        "fig:dyadic_task_matrix",
        "dyadic_task_matrix.png",
        "generate_dyadic_task_matrix",
        "temporal",
        "protocol",
        "shared_workspace",
        "High-contrast matrix of dyadic role structures and temporal-spatial modes, with text labels, cell scores, "
        "and caution bands representing conceptual mutual-responsiveness demand for study planning.",
    ),
    FigureSpec(
        "fig:interaction_timeline",
        "interaction_timeline.png",
        "generate_interaction_timeline",
        "temporal",
        "protocol",
        "visualization_reproducibility",
        "Layered session timeline that separates strokes, pauses, speech, partner turns, repairs, replay windows, "
        "and consent or control events so the visible drawing and analyzable event log remain distinct.",
    ),
    FigureSpec(
        "fig:parallel_sequential_patterns",
        "parallel_sequential_patterns.png",
        "generate_parallel_sequential_patterns",
        "temporal",
        "analytic_simulation",
        "visualization_reproducibility",
        "Raster-style event comparison showing overlapping parallel drawing, alternating turn-taking, and "
        "delayed asynchronous contribution patterns.",
    ),
    FigureSpec(
        "fig:taxonomy_matrix",
        "taxonomy_matrix.png",
        "generate_taxonomy_matrix",
        "taxonomy",
        "conceptual",
        "visualization_reproducibility",
        "Three-by-three temporal-spatial taxonomy with labelled study-condition cells, affordance scores, and "
        "accessibility-aware outlines for comparing synchronous, turn-based, and persistent modes.",
    ),
    FigureSpec(
        "fig:event_logging_schema",
        "event_logging_schema.png",
        "generate_event_logging_schema",
        "methods_protocol",
        "protocol",
        "visualization_reproducibility",
        "Data-flow diagram linking human marks, event rows, derived summaries, model diagnostics, rendered "
        "figures, governance ledgers, and template publication artifacts.",
    ),
    FigureSpec(
        "fig:active_inference_mapping",
        "active_inference_mapping.png",
        "generate_active_inference_mapping",
        "formalisms_appendix",
        "conceptual",
        "visualization_reproducibility",
        "Mapping diagram connecting DigiPPPiP events to active-inference latent states, observations, policies, "
        "and partner-conditioned belief updates.",
    ),
    FigureSpec(
        "fig:active_inference_loop",
        "active_inference_loop.png",
        "generate_active_inference_loop",
        "formalisms_appendix",
        "analytic_simulation",
        "visualization_reproducibility",
        "Two-line free-energy trajectory comparing coupled and decoupled toy dyadic sessions under deterministic "
        "model settings.",
    ),
    FigureSpec(
        "fig:network_analysis_pipeline",
        "network_analysis_pipeline.png",
        "generate_network_analysis_pipeline",
        "formalisms_appendix",
        "protocol",
        "visualization_reproducibility",
        "Pipeline diagram from event-aligned drawing data through synchronized signals, graph construction, "
        "curvature, entropy, and interpretation gates.",
    ),
    FigureSpec(
        "fig:ibs_phases",
        "ibs_phases.png",
        "generate_ibs_phase_plot",
        "temporal",
        "analytic_simulation",
        "visualization_reproducibility",
        "Four-phase conceptual inter-brain-synchrony curve labeled initiation, exploration, convergence, and "
        "completion.",
    ),
    FigureSpec(
        "fig:accessibility_audit_radar",
        "accessibility_audit_radar.png",
        "generate_accessibility_audit_radar",
        "methods_protocol",
        "audit",
        "accessible_visual_media",
        "Radar chart showing documented capability coverage across input flexibility, perceptual feedback, "
        "privacy agency, cognitive load, and partner mediation.",
    ),
    FigureSpec(
        "fig:geometric_hyperscanning",
        "geometric_hyperscanning.png",
        "generate_geometric_hyperscanning_plot",
        "formalisms_appendix",
        "analytic_simulation",
        "visualization_reproducibility",
        "Curvature and entropy diagnostic plot for a synthetic inter-brain network, with transition events marked "
        "as candidate hypotheses rather than findings.",
    ),
    FigureSpec(
        "fig:hyperscanning_alignment",
        "hyperscanning_alignment.png",
        "generate_hyperscanning_alignment",
        "formalisms_appendix",
        "empirical_placeholder",
        "visualization_reproducibility",
        "Alignment diagram showing where future physiology, drawing events, artifact correction, and permutation "
        "controls would enter an empirical hyperscanning study.",
    ),
    FigureSpec(
        "fig:source_quality_map",
        "source_quality_map.png",
        "generate_source_quality_map",
        "methods_protocol",
        "audit",
        "visualization_reproducibility",
        "Source-quality map assigning source classes to conservative claim-strength ceilings with visible source "
        "tier labels, warning notes, and upgrade gates for manuscript use.",
    ),
    FigureSpec(
        "fig:claim_boundary_matrix",
        "claim_boundary_matrix.png",
        "generate_claim_boundary_matrix",
        "methods_protocol",
        "audit",
        "privacy_values",
        "Claim-boundary matrix using text, cell state, bar-like claim ceilings, and right-panel evidence gates to "
        "show maximum defensible claim strength for each recurring DigiPPPiP domain.",
    ),
    FigureSpec(
        "fig:claim_ledger_matrix",
        "claim_ledger_matrix.png",
        "generate_claim_ledger_matrix",
        "methods_protocol",
        "audit",
        "privacy_values",
        "Claim-ledger matrix linking stable manuscript claim families to evidence-key counts, current claim ceiling, "
        "and next evidence gate with high-density but labelled audit rows.",
    ),
    FigureSpec(
        "fig:source_verification_readiness",
        "source_verification_readiness.png",
        "generate_source_verification_readiness",
        "methods_protocol",
        "audit",
        "visualization_reproducibility",
        "High-contrast readiness dashboard with governed citekey coverage, priority-source refresh pressure, "
        "official and reporting anchors, source tiers, recheck triggers, and visible missing-record status.",
    ),
    FigureSpec(
        "fig:study_readiness_matrix",
        "study_readiness_matrix.png",
        "generate_study_readiness_matrix",
        "methods_protocol",
        "protocol",
        "privacy_values",
        "High-density governance matrix showing participant rights, protocol obligations, source-anchor counts, "
        "dyadic scope, conflict rules, remote-therapy cautions, and optional AI-branch separation with text labels.",
    ),
    FigureSpec(
        "fig:narrative_information",
        "narrative_information.png",
        "generate_narrative_information_plot",
        "formalisms_appendix",
        "analytic_simulation",
        "visualization_reproducibility",
        "Two-panel narrative-information diagnostic showing surprisal peaks and motif convergence in a synthetic "
        "stroke sequence.",
    ),
    FigureSpec(
        "fig:multilevel_outcome_model",
        "multilevel_outcome_model.png",
        "generate_multilevel_outcome_model",
        "methods_protocol",
        "empirical_placeholder",
        "visualization_reproducibility",
        "Multilevel outcome model placeholder showing where dyad, participant, temporal mode, access condition, "
        "and repeated sessions would enter future empirical analyses.",
    ),
    FigureSpec(
        "fig:epistemic_arc",
        "epistemic_arc.png",
        "generate_epistemic_arc_plot",
        "formalisms_appendix",
        "analytic_simulation",
        "visualization_reproducibility",
        "Expected-information-gain and order-change curves with an annotated peak that marks a conceptual "
        "curiosity or insight moment.",
    ),
    FigureSpec(
        "fig:neuroergonomics_flow",
        "neuroergonomics_flow.png",
        "generate_neuroergonomics_flow_plot",
        "neuroergonomics",
        "analytic_simulation",
        "visualization_reproducibility",
        "Neuroergonomic diagnostic surface combining flow-state regions, interruption cost, and attention "
        "allocation trade-offs.",
    ),
    FigureSpec(
        "fig:accessibility_features_overview",
        "accessibility_features_overview.png",
        "generate_accessibility_features_overview",
        "accessibility",
        "protocol",
        "accessible_visual_media",
        "Feature map connecting input options, feedback channels, cognitive-load controls, and privacy agency to "
        "participatory validation with disabled partners.",
    ),
    FigureSpec(
        "fig:evidence_synthesis",
        "evidence_synthesis.png",
        "generate_evidence_synthesis_plot",
        "introduction",
        "conceptual",
        "visualization_reproducibility",
        "Bipartite evidence graph linking foundational PPPiP source domains to DigiPPPiP dimensions with line "
        "weight, source counts, and lineage labels to keep conceptual support distinct from validation.",
    ),
    FigureSpec(
        "fig:relational_microplaces",
        "relational_microplaces.png",
        "generate_relational_microplaces",
        "place",
        "conceptual",
        "privacy_values",
        "Digital placemaking map showing recurring micro-place contexts feeding a persistent shared drawing "
        "artifact.",
    ),
    FigureSpec(
        "fig:framework_template",
        "framework_template.png",
        "generate_framework_template",
        "integrative",
        "conceptual",
        "research_through_design",
        "Reusable visual grammar template that distinguishes actors, artifacts, signals, contexts, diagnostics, "
        "evidence maps, caveats, non-color encodings, and long-description obligations.",
    ),
    FigureSpec(
        "fig:figure_generation_pipeline",
        "figure_generation_pipeline.png",
        "generate_figure_generation_pipeline",
        "methods_protocol",
        "audit",
        "research_through_design",
        "Figure-generation pipeline showing the artifact chain, quality-gate chain, claim-status stamp, and "
        "aesthetic/accessibility discipline from claim scope through render validation.",
    ),
    FigureSpec(
        "fig:method_source_bridge",
        "method_source_bridge.png",
        "generate_method_source_bridge",
        "methods_protocol",
        "audit",
        "research_through_design",
        "Source-to-method bridge connecting scholarly source families to composition archetypes, citekeys, accessible "
        "visualization sources, and quality gates in a dense labelled audit table.",
    ),
    FigureSpec(
        "fig:visual_encoding_matrix",
        "visual_encoding_matrix.png",
        "generate_visual_encoding_matrix",
        "methods_protocol",
        "audit",
        "visualization_reproducibility",
        "Visual encoding matrix mapping semantic roles to palette keys, non-color channels, hierarchy rules, contrast "
        "checks, and accessibility guardrails used consistently across generated figures.",
    ),
    FigureSpec(
        "fig:figure_method_audit",
        "figure_method_audit.png",
        "generate_figure_method_audit",
        "methods_protocol",
        "audit",
        "accessible_visual_media",
        "Bar-style figure-method audit showing which deterministic, registry, caption, source, accessibility, "
        "reference, and claim-status gates are required.",
    ),
    FigureSpec(
        "fig:validation_ladder",
        "validation_ladder.png",
        "generate_validation_ladder",
        "methods_protocol",
        "protocol",
        "privacy_values",
        "Validation ladder showing feasibility, meaning, access, comparative outcomes, and physiology stages with "
        "minimum controls for claim escalation.",
    ),
    FigureSpec(
        "fig:research_agenda",
        "research_agenda.png",
        "generate_research_agenda_plot",
        "agenda",
        "protocol",
        "research_through_design",
        "Research-priority map comparing conceptual feasibility and research value across staged DigiPPPiP agenda "
        "items.",
    ),
    FigureSpec(
        "fig:webapp_main_canvas",
        "webapp_main_canvas.png",
        "generate_webapp_main_canvas",
        "methods_protocol",
        "conceptual",
        "shared_workspace",
        "Screenshot of the running DigiPPPiP web canvas in dark theme showing freehand strokes, the active user "
        "moniker, partner-waiting status, tool palette, and the simulated coupled-dynamics panel.",
    ),
    FigureSpec(
        "fig:webapp_metrics_dashboard",
        "webapp_metrics_dashboard.png",
        "generate_webapp_metrics_dashboard",
        "methods_protocol",
        "conceptual",
        "research_through_design",
        "Close-up of the Coupled Dynamics dashboard showing simulated Variational Free Energy, Inter-Brain "
        "Synchrony, and Narrative Entropy values with progress bars and a disclaimer that values are not measured "
        "clinical data.",
    ),
    FigureSpec(
        "fig:webapp_light_theme",
        "webapp_light_theme.png",
        "generate_webapp_light_theme",
        "methods_protocol",
        "conceptual",
        "accessible_visual_media",
        "Screenshot of the DigiPPPiP web canvas in the light theme, showing the same collaborative drawing layout "
        "with visible strokes and controls on a light background.",
    ),
    FigureSpec(
        "fig:webapp_theme_settings",
        "webapp_theme_settings.png",
        "generate_webapp_theme_settings",
        "methods_protocol",
        "conceptual",
        "accessible_visual_media",
        "Screenshot of the DigiPPPiP theme and canvas-background settings in the light theme with a plain white "
        "canvas, illustrating configurable visual contrast and accessibility options.",
    ),
)


def figure_specs() -> tuple[FigureSpec, ...]:
    """Return the ordered figure specification registry."""
    return FIGURE_SPECS


def figure_generator_names() -> tuple[str, ...]:
    """Return the ordered generator names used by ``src/figures.py``."""
    return tuple(spec.generator for spec in FIGURE_SPECS)


FIGURE_GENERATOR_NAMES: tuple[str, ...] = figure_generator_names()


def figure_spec_by_generator(generator: str) -> FigureSpec:
    """Return the figure spec for a generator name."""
    for spec in FIGURE_SPECS:
        if spec.generator == generator:
            return spec
    raise KeyError(f"no figure spec registered for generator {generator!r}")


def figure_spec_by_filename(filename: str) -> FigureSpec:
    """Return the figure spec for a PNG filename."""
    for spec in FIGURE_SPECS:
        if spec.filename == filename:
            return spec
    raise KeyError(f"no figure spec registered for filename {filename!r}")


def missing_figure_specs(generators: tuple[str, ...]) -> tuple[str, ...]:
    """Return generator names without a typed figure spec."""
    known = set(figure_generator_names())
    return tuple(generator for generator in generators if generator not in known)


def figure_long_description_map() -> dict[str, str]:
    """Return long-description sidecar text keyed by PNG filename."""
    descriptions: dict[str, str] = {}
    for spec in FIGURE_SPECS:
        descriptions[spec.filename] = (
            f"# Long description: {spec.label}\n\n"
            f"{spec.accessibility_description}\n\n"
            f"Generator: `{spec.generator}`.\n"
            f"Claim status: {spec.claim_status}.\n"
            f"Manuscript section: {spec.section}.\n"
            f"Method-source family: {spec.method_source_family}.\n"
            f"Placement: {spec.placement}.\n"
            "Reading order: title and visible claim-status stamp first, then the main panel from left to right or "
            "top to bottom, then legends, callouts, and footer caveat.\n"
            "Caveat: the figure is conceptual, protocol, audit, analytic-simulation, or placeholder material "
            "according to the claim status; it is not participant outcome evidence unless explicitly stated.\n"
            "Evidence boundary: stronger claims require the future evidence named by the manuscript claim ledger "
            "and source-quality gates.\n"
        )
    return descriptions


def figure_count() -> int:
    """Return the number of registered manuscript figure generators."""
    return len(FIGURE_SPECS)
