# Manuscript Syntax Reference (Digi-PPPiP)

Project overlay on the repository-wide manuscript semantics. Documents the
Digi-PPPiP figure registry, equation labels, section labels, and the
double-brace variable-token contract. Pandoc syntax only -- never raw LaTeX
citation or reference macros in Markdown.

## Citation Syntax (Pandoc)

```markdown
[@mikhailova2018pppip]                 <!-- single -->
[@friston2010fep; @hinrichs2025geometric]   <!-- multiple -->
@mikhailova2018pppip showed that ...   <!-- narrative -->
```

All citation keys must exist in [`references.bib`](references.bib).
Before adding a citekey, verify the title, author list, year, venue, and DOI or
stable URL against a resolver or primary metadata page. Search and Perplexity
results are discovery leads, not bibliography authority.

## Equation label registry

| Label | Equation | Source file |
|---|---|---|
| `{#eq:vfe}` | Gaussian variational free energy | `18_formalisms_appendix.md` |
| `{#eq:posterior}` | Precision-weighted posterior mean | `18_formalisms_appendix.md` |
| `{#eq:forman_ricci}` | $\mathrm{Fr}(uv)=4-\deg u-\deg v$ | `18_formalisms_appendix.md` |
| `{#eq:shannon}` | Stroke-sequence Shannon entropy | `18_formalisms_appendix.md` |
| `{#eq:epistemic_arc}` | Expected-information-gain arc | `18_formalisms_appendix.md` |

## Table label registry

| Label | Table | Source file |
|---|---|---|
| `{#tbl:taxonomy_modes}` | Temporal-spatial DigiPPPiP modality grid | `10_taxonomy.md` |

## Figure label registry

The canonical figure registry is `src/figure_catalog.py`. It stores the typed
figure spec for each row below: label, PNG filename, generator, manuscript
section, claim status, method-source family, accessibility description, and
main/supplemental placement. Figure generation writes matching long-description
sidecars under `output/figures/long_descriptions/`.

| Label | PNG filename | Generator in `src/figures.py` |
|---|---|---|
| `{#fig:evolution_timeline}` | `output/figures/evolution_timeline.png` | `generate_evolution_timeline()` |
| `{#fig:conceptual_ecology}` | `output/figures/conceptual_ecology.png` | `generate_conceptual_ecology()` |
| `{#fig:cyberphysical_spectrum}` | `output/figures/cyberphysical_spectrum.png` | `generate_cyberphysical_spectrum()` |
| `{#fig:cpss_architecture}` | `output/figures/cpss_architecture.png` | `generate_cpss_architecture()` |
| `{#fig:dyadic_task_matrix}` | `output/figures/dyadic_task_matrix.png` | `generate_dyadic_task_matrix()` |
| `{#fig:interaction_timeline}` | `output/figures/interaction_timeline.png` | `generate_interaction_timeline()` |
| `{#fig:parallel_sequential_patterns}` | `output/figures/parallel_sequential_patterns.png` | `generate_parallel_sequential_patterns()` |
| `{#fig:taxonomy_matrix}` | `output/figures/taxonomy_matrix.png` | `generate_taxonomy_matrix()` |
| `{#fig:event_logging_schema}` | `output/figures/event_logging_schema.png` | `generate_event_logging_schema()` |
| `{#fig:active_inference_mapping}` | `output/figures/active_inference_mapping.png` | `generate_active_inference_mapping()` |
| `{#fig:active_inference_loop}` | `output/figures/active_inference_loop.png` | `generate_active_inference_loop()` |
| `{#fig:network_analysis_pipeline}` | `output/figures/network_analysis_pipeline.png` | `generate_network_analysis_pipeline()` |
| `{#fig:ibs_phases}` | `output/figures/ibs_phases.png` | `generate_ibs_phase_plot()` |
| `{#fig:accessibility_audit_radar}` | `output/figures/accessibility_audit_radar.png` | `generate_accessibility_audit_radar()` |
| `{#fig:geometric_hyperscanning}` | `output/figures/geometric_hyperscanning.png` | `generate_geometric_hyperscanning_plot()` |
| `{#fig:hyperscanning_alignment}` | `output/figures/hyperscanning_alignment.png` | `generate_hyperscanning_alignment()` |
| `{#fig:source_quality_map}` | `output/figures/source_quality_map.png` | `generate_source_quality_map()` |
| `{#fig:claim_boundary_matrix}` | `output/figures/claim_boundary_matrix.png` | `generate_claim_boundary_matrix()` |
| `{#fig:claim_ledger_matrix}` | `output/figures/claim_ledger_matrix.png` | `generate_claim_ledger_matrix()` |
| `{#fig:source_verification_readiness}` | `output/figures/source_verification_readiness.png` | `generate_source_verification_readiness()` |
| `{#fig:study_readiness_matrix}` | `output/figures/study_readiness_matrix.png` | `generate_study_readiness_matrix()` |
| `{#fig:narrative_information}` | `output/figures/narrative_information.png` | `generate_narrative_information_plot()` |
| `{#fig:multilevel_outcome_model}` | `output/figures/multilevel_outcome_model.png` | `generate_multilevel_outcome_model()` |
| `{#fig:epistemic_arc}` | `output/figures/epistemic_arc.png` | `generate_epistemic_arc_plot()` |
| `{#fig:neuroergonomics_flow}` | `output/figures/neuroergonomics_flow.png` | `generate_neuroergonomics_flow_plot()` |
| `{#fig:accessibility_features_overview}` | `output/figures/accessibility_features_overview.png` | `generate_accessibility_features_overview()` |
| `{#fig:evidence_synthesis}` | `output/figures/evidence_synthesis.png` | `generate_evidence_synthesis_plot()` |
| `{#fig:relational_microplaces}` | `output/figures/relational_microplaces.png` | `generate_relational_microplaces()` |
| `{#fig:framework_template}` | `output/figures/framework_template.png` | `generate_framework_template()` |
| `{#fig:figure_generation_pipeline}` | `output/figures/figure_generation_pipeline.png` | `generate_figure_generation_pipeline()` |
| `{#fig:method_source_bridge}` | `output/figures/method_source_bridge.png` | `generate_method_source_bridge()` |
| `{#fig:visual_encoding_matrix}` | `output/figures/visual_encoding_matrix.png` | `generate_visual_encoding_matrix()` |
| `{#fig:figure_method_audit}` | `output/figures/figure_method_audit.png` | `generate_figure_method_audit()` |
| `{#fig:validation_ladder}` | `output/figures/validation_ladder.png` | `generate_validation_ladder()` |
| `{#fig:research_agenda}` | `output/figures/research_agenda.png` | `generate_research_agenda_plot()` |
| `{#fig:webapp_main_canvas}` | `output/figures/webapp_main_canvas.png` | `generate_webapp_main_canvas()` |
| `{#fig:webapp_metrics_dashboard}` | `output/figures/webapp_metrics_dashboard.png` | `generate_webapp_metrics_dashboard()` |
| `{#fig:webapp_light_theme}` | `output/figures/webapp_light_theme.png` | `generate_webapp_light_theme()` |
| `{#fig:webapp_theme_settings}` | `output/figures/webapp_theme_settings.png` | `generate_webapp_theme_settings()` |

## Section label registry

| File | H1 | Label |
|---|---|---|
| `00_abstract.md` | Abstract | `{#sec:abstract}` |
| `01_introduction.md` | Introduction: From Shared Marks to Study-Ready Infrastructure | `{#sec:introduction}` |
| `02_cyberphysical_expansion.md` | Cyberphysical Substrate: Canvas, Body, Archive | `{#sec:cyberphysical}` |
| `03_temporal_architecture.md` | Temporal Coordination: Turns, Overlap, and Persistence | `{#sec:temporal}` |
| `04_active_inference.md` | Modeling Lens: Active Inference Without Mechanism Claims | `{#sec:active_inference}` |
| `05_neuroergonomics.md` | Neuroergonomic Burden and Shared Attention | `{#sec:neuroergonomics}` |
| `06_cyber_phenomenology.md` | Cyber-Phenomenology: Presence, Embodiment, and Mediation | `{#sec:phenomenology}` |
| `07_accessibility.md` | Accessible Shared Drawing: Capability Before Claim | `{#sec:accessibility}` |
| `08_relational_aesthetics.md` | Relational Aesthetics: Coauthored Marks and Social Form | `{#sec:relational_aesthetics}` |
| `09_place_based.md` | Place-Based Micropractice and Digital Placemaking | `{#sec:place}` |
| `10_taxonomy.md` | Temporal-Spatial Taxonomy for Study Design | `{#sec:taxonomy}` |
| `11_dyadic_digital_health.md` | Dyadic Digital Health: Consent, Relationship Boundaries, and AI Separation | `{#sec:health}` |
| `12_methods_protocol.md` | Methods Protocol: Governance, Provenance, and Validation | `{#sec:methods_protocol}` |
| `13_research_agenda.md` | Research Agenda: From Feasibility to Evidence | `{#sec:agenda}` |
| `14_integrative_model.md` | Integrative Model: The Human-Human DigiPPPiP Kernel | `{#sec:integrative}` |
| `15_discussion.md` | Discussion: Limits, Failure Modes, and Future Replacement | `{#sec:discussion}` |
| `16_casestudies.md` | Case Studies: Dementia Care as a Stress Test | `{#sec:casestudies}` |
| `17_conclusions.md` | Conclusions: Study-Ready Without Overclaiming | `{#sec:conclusions}` |
| `18_formalisms_appendix.md` | Appendix: Free-Energy and Active-Inference Formalisms | `{#sec:formalisms_appendix}` |
| `99_references.md` | References | `{#sec:references}` |

## Variable-token contract

Every double-brace UPPERCASE variable token used in any section file MUST be a
key returned by
`src/manuscript_variables.py::generate_variables`. Tokens are hydrated from
`manuscript/config.yaml` + `output/data/digippppip_metrics.json` (the latter
produced by the tested `src/metrics.py` primitive — never computed in
`src/figures.py`). `tests/test_integration_consistency.py` enforces this.

## Prose Conventions

- No "In summary" / "In conclusion" section-openers (RASP standard).
- Active voice; explicit file paths (`src/active_inference.py`, not "the module").
- One idea per paragraph; synthetic models captioned as conceptual, never empirical.
