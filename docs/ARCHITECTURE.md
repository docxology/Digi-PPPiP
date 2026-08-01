# Digi-PPPiP Architecture

This document maps `src/` to the manuscript, explains the data flow that turns
tested primitives into rendered prose, and describes the governance layers.

## Layer model

```
 src/ (pure tested primitives)
   └── metrics.py          SINGLE numeric authority (covered, tested)
         └── figures.py    rendering workflow ONLY (coverage-omitted)
              └── output/figures/*.png + figure_registry.json + artifact audit
   └── manuscript_outputs.py + manuscript_variables.py   {{TOKEN}} hydration
        └── output/data/*.json
 manuscript/  ← Pandoc chapters reference the generated tokens, figures, sources
```

Two hard rules keep this deterministic and auditable:

1. **Every manuscript-bound scalar is computed in `src/metrics.py`** from the
   tested primitive layer (`taxonomy`, `active_inference`, `hyperscanning`,
   etc.) and serialized to `output/data/digippppip_metrics.json`.
   `src/figures.py` never computes a scalar itself — its only contact with
   metrics is to call `metrics.compute_all_metrics()` and write the JSON.
2. **`src/figures.py` is intentionally coverage-omitted** (it renders PNGs and
   registries). The meaning-bearing figure contract lives in the *covered*,
   tested modules (`src/figure_catalog.py`, `src/figure_methods.py`) so that
   the semantics are enforced even though the plotting code is not.

## Module map

| Module | Responsibility | Governed by |
|---|---|---|
| `taxonomy.py` | 3×3 temporal–spatial modality grid + affordance scores | — |
| `active_inference.py` | Gaussian dyadic free-energy + belief updates | — |
| `hyperscanning.py` | inter-brain synchrony phases, Forman–Ricci curvature, entropy | — |
| `narrative.py` | stroke-sequence entropy, surprisal, pivotal moments, arc | — |
| `aesthetics.py` | active-inference epistemic arc ("aha" peak) | — |
| `neuroergonomics.py` | flow state, technoference cost, attention allocation | — |
| `session_events.py` | timestamped event validation + temporal classification | — |
| `outcomes.py` | outcome measures, multilevel model spec, claim strength | — |
| `accessibility.py` | criteria, capabilities, audit scoring | — |
| `source_quality.py` | source-class → claim-strength ceilings + overclaim warnings | `src/source_quality.py` |
| `claim_ledger.py` | source→claim records + upgrade gates | `src/claim_ledger.py` |
| `source_verification.py` | DOI/URL + metadata ledger + recheck triggers | `src/source_verification.py` |
| `study_readiness.py` | dyadic consent, archive-control, AI-branch gates | `src/study_readiness.py` |
| `systems_governance.py` | boundary, feedback, causal, ethics, reversal gates | `src/systems_governance.py` |
| `figure_methods.py` | figure stages, audit criteria, visual grammar, caption contract | `src/figure_methods.py` |
| `figure_catalog.py` | typed figure specs + long-description text | `src/figure_catalog.py` |
| `figure_artifact_audit.py` | artifact-level PNG / registry / reference checks | `src/figure_artifact_audit.py` |
| `evidence.py` | evidence-synthesis graph (domains → dimensions) | — |
| `metrics.py` | composes all of the above into the single metric authority | `tests/` |
| `figures.py` | rendering workflow (coverage-omitted) | `src/figure_catalog.py` |
| `manuscript_variables.py` | `{{TOKEN}}` hydrator | `tests/` |
| `manuscript_outputs.py` | render-preparation artifacts (ledgers, resolutions) | `tests/` |
| `provenance.py` | output hashes + generated-artifact inventory | `tests/` |

For details on the figure layer see [`FIGURES.md`](FIGURES.md); for the
data-provenance and scholarship layers see [`SCHOLARSHIP.md`](SCHOLARSHIP.md).

## Numeric-authority data flow

```
src/metrics.py
   └─ compute_all_metrics()  (deterministic given an experiment config)
        └─ output/data/digippppip_metrics.json
   src/manuscript_variables.py
   └─ generate_variables(require_metrics=True)
        └─ output/data/manuscript_variables.json
   manuscript/*.md  {{RESULT_*}} tokens
        └─ (template render) final PDF/HTML
```

`require_metrics=True` makes the hydrator fail instead of emitting `"N/A"` if a
result-derived token's artifact is missing, so stale or partial outputs cannot
silently leak placeholder values into a render.

## Governance layers

The project separates the **human–human drawing kernel** from optional,
governed branches (instrumentation, modeling, optional AI, physiology, place
context, clinical translation). Each branch carries an explicit feedback
signal, causal assumption, ethics gate, and reversal path before manuscript
language may strengthen. See [`../ISA.md`](../ISA.md) and
[`SCHOLARSHIP.md`](SCHOLARSHIP.md).
