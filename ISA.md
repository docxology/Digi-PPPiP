---
task: "Deep-review, harden, and publish Digi-PPPiP as standalone private repo docxology/Digi-PPPiP (sidecar to docxology/template)"
slug: 20260519-035901_digi-ppppip-manuscript-figures
project: Digi-PPPiP
effort: E4
effort_source: context-override
phase: complete
progress: 153/153 (build) + 28/28 (review+publish)
mode: interactive
started: 2026-05-19T03:59:01Z
updated: 2026-05-23T13:35:00Z
---

# ISA — Digi-PPPiP

> System of record for the **Digi-PPPiP** research project. The ideal state is a complete,
> private active-project artifact: a modular academic manuscript on *DigiPPPiP —
> Digital Partner Pen Play in Parallel* plus a composable, fully-tested
> figure-generation codebase that renders through the sibling template pipeline while
> remaining runnable as a standalone project.

## Problem

Earlier project state was a single long prose document with inline footnote
references. The current project is now modular and runnable, so the remaining risk is
contract drift: citation metadata can outrun DOI/title verification, figure generators can
silently diverge from `manuscript/config.yaml`, token hydration can leak placeholders into
rendered prose, and docs can preserve historical file numbering after the manuscript moves.
The ISA therefore tracks both the original buildout criteria and the continuing ideal:
tested primitives, reproducible figures, active render-mode fail-fast behavior,
Pandoc manuscript semantics, verified scholarship, and the 90% project test-coverage gate.
It also treats system boundaries, feedback loops, causal assumptions, ethics gates, and
reversal paths as executable governance rather than informal prose.

## Vision

A researcher opens this project root, runs the figure script and pytest,
and watches a conceptual paper become a *computational* one: every theoretical construct in
the framework has a tested primitive behind it and a publication-quality figure in front of
it. The taxonomy is not a static table but a scored data model; "coupled active inference"
is not a phrase but a free-energy trajectory you can re-run; "Forman–Ricci curvature as an
affective-phase proxy" is an actual curve with detected transitions. The euphoric surprise:
the framework's most hand-wavy ideas turn out to be the most precisely operationalizable.
The same manuscript and generated artifacts enter the
shared render pipeline as a sidecar under `docxology/template` (`template/projects/Digi-PPPiP`)
without changing the project-internal source tree.

## Out of Scope

No real fNIRS/EEG data acquisition, human-subjects work, or empirical validation — all
computational illustrations are explicitly synthetic, deterministic, and labelled as such.
No new pipeline infrastructure, no edits to the sibling template `infrastructure/` or root
`scripts/`. No git commit, staging, or push of the project unless the user explicitly
changes the confidentiality policy. No default LaTeX/PDF compilation while the project
is being edited standalone; template rendering is validated from a sibling
`docxology/template` checkout. No AI/LLM review or translation execution. No
mobile/AR/VR implementation — the cyberphysical modes are described and modeled, not
built. No reproduction of the original 2018 paper's content verbatim; DigiPPPiP cites it
as foundation.

## Principles

- **Scaffolding over cleverness.** Compliance with the established private-project shape beats
  novel structure; a researcher who knows the template exemplars must recognize this instantly.
- **Code before prose claims.** Every quantitative or structural claim a figure makes is
  produced by a tested `src/` primitive, never hand-drawn or hardcoded in a script.
- **Thin orchestrator discipline.** Business logic lives only in `src/`; `scripts/` coordinate
  I/O and call tested methods. Substrate-independent: the same rule the whole repo lives by.
- **Honest synthetic framing.** Illustrative simulations are reproducible (fixed seeds) and
  captioned as conceptual models, never presented as empirical findings.
- **Modularity is composability.** Each manuscript section and each figure is independently
  buildable and independently verifiable.
- **Branches need reversal.** AI, physiology, place context, event replay, and clinical
  translation stay outside the human-human kernel until their feedback, ethics, and stop
  conditions are explicit.

## Constraints

- Project root: this repository (the `Digi-PPPiP` checkout); no hardcoded absolute path.
- Lifecycle: private project; standalone development is fully supported, and template
  rendering is a lifecycle gate through a sibling `docxology/template` checkout
  (placed at `template/projects/Digi-PPPiP`).
- Structure MUST retain the template-compatible shape: `src/ tests/ scripts/ manuscript/
  pyproject.toml`, plus `ISA.md` at project root.
- Python ≥3.10; dependencies limited to `numpy, scipy, matplotlib, pyyaml` (+ `pytest,
  pytest-cov` dev). Optional `networkx` only if vendored-free; curvature implemented directly.
- `MPLBACKEND=Agg`; figures 300 dpi; colourblind-safe palette; deterministic (fixed seeds).
- `tool.coverage.run` omits the workflow module `src/figures.py` (mirrors exemplar omitting
  `analysis.py`/`dashboard.py`); the 90% gate applies to pure primitive modules.
- No mocks anywhere in `tests/` (repo No-Mocks policy) — real numerical examples only.
- Manuscript uses Pandoc syntax only: `[@citekey]`, `[@fig:label]`, `{#sec:label}`,
  `$$…$$ {#eq:label}`; never raw `\cite`/`\ref`. All cite keys exist in `references.bib`.
- Real author metadata has not been supplied; current manuscript metadata is draft-only and
  must not be treated as publication-ready attribution.
- Systems-governance records in `src/systems_governance.py` are claim-boundary artifacts:
  they do not prove safety, usefulness, relationship improvement, treatment effect, or
  physiological mechanism without direct participant evidence.
- Primary agent performs all writes (subagent Edit/Write is policy-denied in this repo);
  verification is on-disk and scoped to the active project.

## Goal

Produce a standalone, template-compatible project (renderable as a `docxology/template`
sidecar) consisting of
(1) a modular Pandoc manuscript of ≥16 ordered section files plus `config.yaml`,
`preamble.md`, `SYNTAX.md`, and `references.bib`, and (2) a composable figure-generation
codebase of tested `src/` primitive modules, one coverage-omitted `src/figures.py`
workflow module that emits the registered 300-dpi PNG set, a `src/manuscript_variables.py`
token hydrator, thin `scripts/` orchestrators, and a no-mocks `tests/` suite that passes at
≥90% line+branch coverage on the non-omitted `src/` primitives — all verified on disk.

## Criteria

### Group A — Scaffold & configuration

- [x] ISC-1: `pyproject.toml` exists and declares deps `numpy, scipy, matplotlib, pyyaml`.
- [x] ISC-2: `pyproject.toml` `[tool.pytest.ini_options]` sets `pythonpath=["src"]`, `testpaths=["tests"]`.
- [x] ISC-3: `pyproject.toml` `[tool.coverage.run]` `source=["src"]`, `branch=true`, and `omit` includes `src/figures.py`.
- [x] ISC-4: `pyproject.toml` `[tool.coverage.report]` `fail_under = 90`.
- [x] ISC-5: `manuscript/config.yaml` parses under `yaml.safe_load` and has `paper.title`, `authors`, `keywords`.
- [x] ISC-6: `config.yaml` has an `experiment:` block with the simulation parameters consumed by `manuscript_variables.py`.
- [x] ISC-7: `manuscript/preamble.md` contains a fenced `latex` block with `amsmath` and `natbib`.
- [x] ISC-8: `manuscript/SYNTAX.md` contains a figure-label registry table mapping `{#fig:…}` → PNG → generator function.
- [x] ISC-9: `manuscript/SYNTAX.md` contains a section-label registry covering every manuscript H1.
- [x] ISC-10: `src/__init__.py` and `tests/__init__.py` exist.
- [x] ISC-11: `tests/conftest.py` forces `MPLBACKEND=Agg` and adds `src/` to `sys.path`.
- [x] ISC-12: `Digi-PPPiP/README.md` exists describing the project, run commands, and module map.

### Group B — `src/taxonomy.py` (pure, tested)

- [x] ISC-13: `src/taxonomy.py` defines `TemporalMode` and `SpatialConfig` enums with 3 members each.
- [x] ISC-14: `Modality` dataclass carries `temporal, spatial, name, affordances: dict[str,float]`.
- [x] ISC-15: `build_taxonomy()` returns exactly 9 `Modality` objects (3×3 grid) with unique (temporal,spatial) keys.
- [x] ISC-16: each affordance score is bounded in `[0,1]` for every modality (tool: pytest assertion).
- [x] ISC-17: `recommend_modality(weights)` returns the argmax-utility modality and is deterministic for fixed input.
- [x] ISC-18: `recommend_modality` raises `ValueError` on unknown affordance key.
- [x] ISC-19: `taxonomy_matrix()` returns a 3×3 numpy array consumable by the figure layer.

### Group C — `src/active_inference.py` (pure, tested)

- [x] ISC-20: `variational_free_energy(mu, obs, prior_mu, prior_prec, lik_prec)` returns a finite float.
- [x] ISC-21: free energy is minimized at the precision-weighted posterior mean (numeric check vs analytic optimum, tol 1e-6).
- [x] ISC-22: `belief_update()` implements precision-weighted update; one step toward observation reduces free energy.
- [x] ISC-23: `DyadicState` dataclass holds both partners' beliefs and the shared-canvas observation.
- [x] ISC-24: `simulate_dyadic_session(coupled=True)` returns per-step free-energy and surprise arrays of equal length.
- [x] ISC-25: coupled session reaches lower terminal joint free energy than `coupled=False` for the default seed.
- [x] ISC-26: simulation is deterministic under a fixed `seed` (two runs return arrays equal to 1e-12).
- [x] ISC-27: `simulate_dyadic_session` raises `ValueError` for `steps <= 0`.

### Group D — `src/hyperscanning.py` (pure, tested)

- [x] ISC-28: `simulate_ibs_phases(steps)` returns an IBS time series segmented into 4 named phases summing to `steps`.
- [x] ISC-29: mean IBS in the `convergence` phase exceeds mean IBS in the `initiation` phase (default seed).
- [x] ISC-30: `forman_ricci_curvature(adj)` returns one curvature value per edge of the input adjacency matrix.
- [x] ISC-31: Forman–Ricci of a path-graph edge equals the closed-form value `4 - deg(u) - deg(v)` (exact check).
- [x] ISC-32: `forman_ricci_curvature` rejects a non-square / non-symmetric adjacency with `ValueError`.
- [x] ISC-33: `curvature_entropy(curvatures)` returns a non-negative float; equals 0 for a single-valued vector.
- [x] ISC-34: `detect_phase_transitions(entropy_series)` returns indices where |Δ entropy| exceeds the given threshold.
- [x] ISC-35: detected transition count is 0 on a constant series and ≥1 on a synthetic step series.
- [x] ISC-36: `inter_brain_network(t)` builds a symmetric adjacency whose curvature feeds the entropy proxy (integration probe).

### Group E — `src/narrative.py` (pure, tested)

- [x] ISC-37: `stroke_entropy(seq)` returns Shannon entropy in bits; equals 0 for a constant sequence.
- [x] ISC-38: entropy is maximal (log2 k) for a uniform alphabet of size k (tol 1e-9).
- [x] ISC-39: `surprisal(seq)` returns per-symbol −log2 p with length == len(seq).
- [x] ISC-40: `pivotal_moments(seq, z)` returns indices whose surprisal z-score exceeds `z`.
- [x] ISC-41: `convergence_index(seq)` is monotone-nondecreasing for an entropy-decreasing synthetic sequence.
- [x] ISC-42: `narrative_arc(seq)` returns rising/twist/resolution segment boundaries covering the full sequence.
- [x] ISC-43: empty-sequence inputs raise `ValueError` across the narrative API.

### Group F — `src/aesthetics.py` (pure, tested)

- [x] ISC-44: `epistemic_arc(steps)` returns expected-information-gain trajectory of length `steps`.
- [x] ISC-45: the arc is single-peaked (one interior maximum) — the "aha" location (tool: discrete second-difference check).
- [x] ISC-46: `aha_magnitude(arc)` equals peak minus baseline and is ≥0.
- [x] ISC-47: `order_change_balance(order, change)` returns a value in `[0,1]` maximized at the documented balance point.
- [x] ISC-48: arc is deterministic for fixed parameters (two calls equal to 1e-12).
- [x] ISC-49: invalid (negative) curiosity/precision parameters raise `ValueError`.

### Group G — `src/neuroergonomics.py` (pure, tested)

- [x] ISC-50: `flow_state(challenge, skill)` returns a label in {anxiety, flow, boredom} per the challenge–skill diagonal.
- [x] ISC-51: equal challenge==skill at sufficient magnitude returns `flow` (boundary check).
- [x] ISC-52: `technoference_cost(interruptions, lambda_)` is strictly increasing in `interruptions`.
- [x] ISC-53: `intentional_enclosure_gain()` returns a value in `[0,1]` increasing with notification suppression.
- [x] ISC-54: `attention_allocation()` returns a simplex (non-negative, sums to 1 within 1e-9).
- [x] ISC-55: negative `interruptions` raises `ValueError`.

### Group H — `src/evidence.py` (pure, tested)

- [x] ISC-56: `build_evidence_graph()` returns nodes for the 5 original PPPiP domains and ≥10 DigiPPPiP dimensions.
- [x] ISC-57: every evidence node carries ≥1 BibTeX citation key that exists in `references.bib`.
- [x] ISC-58: `domain_dimension_edges()` returns only edges whose endpoints are declared nodes (referential integrity).
- [x] ISC-59: `evidence_coverage()` returns the fraction of dimensions with ≥1 supporting citation, in `[0,1]`.
- [x] ISC-60: the graph is acyclic at the domain→dimension layer (topological-sort succeeds).
- [x] ISC-61: `adjacency()` returns a square matrix of order == node count, symmetric for the undirected projection.

### Group I — `src/figures.py` workflow module (coverage-omitted)

- [x] ISC-62: `src/figures.py` defines `apply_visualization_style()` setting a colourblind palette and 300 dpi savefig.
- [x] ISC-63: `register_figure()` appends an entry to an in-memory registry serialized to `output/figures/figure_registry.json`.
- [x] ISC-64: `generate_evolution_timeline()` writes `output/figures/evolution_timeline.png` (>5 kB).
- [x] ISC-65: `generate_cyberphysical_spectrum()` writes `cyberphysical_spectrum.png`.
- [x] ISC-66: `generate_taxonomy_matrix()` writes `taxonomy_matrix.png` using `taxonomy.taxonomy_matrix()`.
- [x] ISC-67: `generate_active_inference_loop()` writes `active_inference_loop.png` using `active_inference.simulate_dyadic_session()`.
- [x] ISC-68: `generate_ibs_phase_plot()` writes `ibs_phases.png` using `hyperscanning.simulate_ibs_phases()`.
- [x] ISC-69: `generate_geometric_hyperscanning_plot()` writes `geometric_hyperscanning.png` (curvature + entropy + transitions).
- [x] ISC-70: `generate_narrative_information_plot()` writes `narrative_information.png` using `narrative.*`.
- [x] ISC-71: `generate_epistemic_arc_plot()` writes `epistemic_arc.png` using `aesthetics.epistemic_arc()`.
- [x] ISC-72: `generate_neuroergonomics_flow_plot()` writes `neuroergonomics_flow.png` using `neuroergonomics.*`.
- [x] ISC-73: `generate_evidence_synthesis_plot()` writes `evidence_synthesis.png` using `evidence.build_evidence_graph()`.
- [x] ISC-74: `generate_research_agenda_plot()` writes `research_agenda.png`.
- [x] ISC-75: `main()` runs all generators and writes registered PNGs into `output/figures/`.
- [x] ISC-76: `main()` writes `output/figures/figure_registry.json` whose entries each have `label,png,generator`.
- [x] ISC-77: every registry `label` matches a `{#fig:…}` used in the manuscript (cross-reference integrity).
- [x] ISC-78: `main()` writes `output/data/digippppip_metrics.json` with the scalar metrics referenced by `{{TOKEN}}`s.

### Group J — `src/manuscript_variables.py` (pure, tested)

- [x] ISC-79: `generate_variables(project_root)` returns a flat `dict[str,str]` with UPPERCASE keys, no `{{}}`.
- [x] ISC-80: keys include `CONFIG_TITLE`, `CONFIG_NUM_DIMENSIONS`, `CONFIG_NUM_MODALITIES`, `GENERATION_TIMESTAMP`.
- [x] ISC-81: result-derived tokens fall back to `"N/A"` only in draft mode; render-mode callers use `require_metrics=True` and fail if `output/data/digippppip_metrics.json` is absent or incomplete.
- [x] ISC-82: `CONFIG_HASH` equals the first 16 hex of the sha256 of `config.yaml`.
- [x] ISC-83: `save_variables(vars, path)` writes sorted JSON and returns the path.
- [x] ISC-84: every `{{TOKEN}}` appearing in any `manuscript/*.md` is a key produced by `generate_variables`.

### Group K — `scripts/` thin orchestrators

- [x] ISC-85: `scripts/digippppip_figures.py` imports from `src.figures` and calls `main()`; contains no plotting logic.
- [x] ISC-86: `scripts/digippppip_figures.py` runs end-to-end via `python` and exits 0.
- [x] ISC-87: `scripts/z_generate_manuscript_variables.py` imports `src.manuscript_variables` and writes the variables JSON.
- [x] ISC-88: neither script defines a function that performs domain computation (thin-orchestrator audit by grep).

### Group L — `tests/` (no mocks, deterministic, ≥90%)

- [x] ISC-89: a `tests/test_taxonomy.py` exists and asserts ISC-13..19 behaviors with real values.
- [x] ISC-90: `tests/test_active_inference.py` exists and asserts ISC-20..27.
- [x] ISC-91: `tests/test_hyperscanning.py` exists and asserts ISC-28..36.
- [x] ISC-92: `tests/test_narrative.py` exists and asserts ISC-37..43.
- [x] ISC-93: `tests/test_aesthetics.py` exists and asserts ISC-44..49.
- [x] ISC-94: `tests/test_neuroergonomics.py` exists and asserts ISC-50..55.
- [x] ISC-95: `tests/test_evidence.py` exists and asserts ISC-56..61.
- [x] ISC-96: `tests/test_manuscript_variables.py` exists and asserts ISC-79..83.
- [x] ISC-97: no test file imports `unittest.mock`, `mock`, or calls `patch` (grep returns empty).
- [x] ISC-98: `uv run pytest tests --cov=src --cov-branch --rootdir .` exits 0 (all pass).
- [x] ISC-99: coverage on non-omitted `src/` ≥ 90% line+branch via `pytest --cov=src --cov-branch`.
- [x] ISC-100: every test uses a fixed seed where randomness is involved (grep for `seed`/`default_rng` in stochastic tests).

### Group M — Modular manuscript

- [x] ISC-101: `manuscript/00_abstract.md` exists, H1 `# Abstract {#sec:abstract}`, ≥1 `{{TOKEN}}`.
- [x] ISC-102: `01_introduction.md` covers original PPPiP foundation and motivates DigiPPPiP; H1 carries `{#sec:introduction}`.
- [x] ISC-103: `02_cyberphysical_expansion.md` covers the 6 cyberphysical modes; references `[@fig:cyberphysical_spectrum]`.
- [x] ISC-104: `03_temporal_architecture.md` covers synchronous/semisynchronous/asynchronous modes.
- [x] ISC-105: `04_active_inference.md` frames active inference as a non-mechanistic modeling lens, and `17_formalisms_appendix.md` owns the FEP, discrete-state active-inference, narrative-information, geometric-hyperscanning, and epistemic-arc equations/figures.
- [x] ISC-106: `05_neuroergonomics.md` covers neuroergonomics, BCI, technoference; references `[@fig:neuroergonomics_flow]`.
- [x] ISC-107: `06_cyber_phenomenology.md` covers telepresence/re-embodiment/marbled embodiment.
- [x] ISC-108: `07_accessibility.md` covers disability access and inclusive design principles.
- [x] ISC-109: `08_relational_aesthetics.md` covers Bourriaud and neurodynamics of relational aesthetics.
- [x] ISC-110: `09_place_based.md` covers digital placemaking and place-responsive DigiPPPiP.
- [x] ISC-111: `10_taxonomy.md` presents the 3×3 temporal–spatial taxonomy; references `[@fig:taxonomy_matrix]` and a `{#tbl:…}`.
- [x] ISC-112: `11_dyadic_digital_health.md` covers dyadic digital health and digital intimacy.
- [x] ISC-113: `13_research_agenda.md` enumerates the empirical priorities; references `[@fig:research_agenda]`.
- [x] ISC-114: `14_integrative_model.md` presents the cyberphysical-relational-practice synthesis.
- [x] ISC-115: `15_discussion.md` covers the relational-technology landscape and textosexual-future framing.
- [x] ISC-116: `16_conclusions.md` exists; no banned "In conclusion/In summary" section-opener (RASP prose rule).
- [x] ISC-117: `99_references.md` exists with `# References {#sec:references}`.
- [x] ISC-118: `references.bib` contains a valid entry for every `[@key]` used across `manuscript/*.md`.
- [x] ISC-119: `references.bib` includes `mikhailova2018pppip` (the foundational paper) with author/title/year.
- [x] ISC-120: every `[@fig:label]` in the manuscript resolves to a registry label (no dangling figure refs).
- [x] ISC-121: every `[@eq:label]` referenced is defined by a `$$…$$ {#eq:label}` or labelled equation block.
- [x] ISC-122: every `[@sec:label]` referenced is defined by some H1 `{#sec:label}` in the tree.

### Group N — Composability & integration

- [x] ISC-123: running `scripts/digippppip_figures.py` from a clean `output/` produces all registered PNGs (live probe).
- [x] ISC-124: each generated PNG is a valid PNG (magic-byte check `\x89PNG`).
- [x] ISC-125: `figure_registry.json` length == number of PNGs emitted (no orphan/missing registrations).
- [x] ISC-126: re-running figures is idempotent (second run overwrites, exit 0, same file count).
- [x] ISC-127: `z_generate_manuscript_variables.py` consumes the metrics JSON and emits a populated variables JSON.
- [x] ISC-128: a token-resolution dry-run substitutes every `{{TOKEN}}` in the manuscript (0 unresolved remaining).
- [x] ISC-129: each `src/` primitive imports with no `infrastructure.*` dependency (architectural isolation grep).
- [x] ISC-130: each figure generator calls at least one `src/` primitive (no figure invents its own numbers — grep audit).
- [x] ISC-131: the full `pytest` + figure-generation sequence completes within the E5 time budget on this machine.
- [x] ISC-132: project tree preserves the template-compatible top-level shape (`src tests scripts manuscript pyproject.toml`).

### Group O — Anti-criteria (must NOT happen)

- [x] ISC-133: Anti: any `tests/*.py` imports a mocking framework.
- [x] ISC-134: Anti: a `scripts/*.py` file implements domain math instead of delegating to `src/`.
- [x] ISC-135: Anti: a figure caption presents a synthetic simulation as an empirical fNIRS/EEG result.
- [x] ISC-136: Anti: a hardcoded numeric "finding" appears in a manuscript section without a producing `src/` primitive or citation.
- [x] ISC-137: Anti: the project is staged/committed/pushed without explicit user approval (confidentiality invariant).
- [x] ISC-138: Anti: `infrastructure/` or root `scripts/` are modified.
- [x] ISC-139: Anti: the manuscript contains raw LaTeX citation or reference macros in Markdown body.
- [x] ISC-140: Anti: a `[@key]` is used that has no entry in `references.bib`.
- [x] ISC-141: Anti: `src/figures.py` is counted into the coverage gate (must remain in `omit`).
- [x] ISC-142: Anti: a completion claim (`[x]`) is made without an on-disk artifact token (memory: forge/verify-on-disk).
- [x] ISC-143: Anti: coverage is asserted from a standalone number without the `--cov-branch` probe actually run.
- [x] ISC-144: Anti: a PNG is registered in `figure_registry.json` but absent from disk.
- [x] ISC-145: Anti: any manuscript H1 lacks a `{#sec:…}` label.

### Group P — Antecedent (experiential precondition)

- [x] ISC-146: Antecedent: the central `taxonomy_matrix.png` renders the 3×3 grid with both axes labelled and per-cell modality names legible at print size — the figure a reader recognizes instantly as "the DigiPPPiP map".

### Group Q — Numeric authority & cross-artifact consistency (advisor-refined)

- [x] ISC-147: `src/metrics.py` exists, is in the coverage `source` (NOT omitted), and exposes `compute_all_metrics()`.
- [x] ISC-148: every scalar in `output/data/digippppip_metrics.json` is produced by `metrics.compute_all_metrics()`, not computed in `figures.py` (grep audit: no arithmetic-bearing metric assignment in `figures.py`).
- [x] ISC-149: `tests/test_metrics.py` pins each metric to a closed-form/hand-computed expected value (no shape-only assertions).
- [x] ISC-150: each math-primitive test includes a negative control — flip one input, assert the output moves the correct direction.
- [x] ISC-151: `tests/test_integration_consistency.py` asserts set equality {PNG stems} == {registry labels} == {`[@fig:]` refs in manuscript}.
- [x] ISC-152: `tests/test_integration_consistency.py` asserts {`{{TOKEN}}`s in manuscript} ⊆ {keys from `generate_variables`} and every `[@key]` ∈ `references.bib`.
- [x] ISC-153: per-module pytest collected-count > 0 (guards against an import error silently shrinking collection while the suite stays green).

### Group R — Deep review, standalone hardening & sidecar publication (task 2, 2026-05-23)

> New task: review the project most deeply, run every gate, harden it for standalone
> distribution, then publish it as a clean **private** repo `docxology/Digi-PPPiP` whose
> documentation makes rendering-via-the-template-sidecar unambiguous. The export must be
> clone-correct (the crescent_city learning: a repo that passes in-situ can fail in a fresh
> clone — `feedback-exclusion-must-be-file-verified-against-tests`).

Review & checks (D1):
- [x] ISC-R1: full `pytest --cov=src --cov-branch` gate green on disk (≥90%, exit 0) — re-run after edits.
- [x] ISC-R2: `ruff check src tests scripts` clean.
- [x] ISC-R3: `mypy src tests scripts` clean.
- [x] ISC-R4: `scripts/digippppip_figures.py` emits the registered PNG set; each PNG valid (`\x89PNG`); registry count == PNG count.
- [x] ISC-R5: `z_generate_manuscript_variables.py` hydrates with 0 unresolved `{{TOKEN}}`s.
- [x] ISC-R6: template prerender passes for `projects/Digi-PPPiP/manuscript` (sidecar render gate).
- [x] ISC-R7: template render produces a Digi-PPPiP PDF on disk (the paper actually renders via sidecar).

Hardening / improvements (D1):
- [x] ISC-R8: no machine-specific absolute home path (a `/Users/...`-style path) remains in any tracked `tests/*.py` (grep returns empty).
- [x] ISC-R9: lifecycle doc test rewritten (`test_run_docs_describe_sidecar_render_without_local_paths`) to assert sidecar/active SEMANTICS (template-render relationship present, no passive-regression) WITHOUT a hardcoded absolute path — still green.
- [x] ISC-R10: docs no longer present a stale metrics snapshot — figures/tests/coverage numbers match the on-disk-verified current baseline (35 figures, 111 tests, 94.19%).
- [x] ISC-R11: no machine-specific absolute home path remains in README.md / AGENTS.md / RENDERING.md (genericized to clone-relative sidecar instructions).
- [x] ISC-R12: full suite still green on disk AFTER the test/doc edits (re-run, exit 0).

Sidecar documentation (D3):
- [x] ISC-R13: a dedicated sidecar rendering guide (`RENDERING.md`) exists with copy-paste clone→place→render commands targeting `docxology/template`.
- [x] ISC-R14: the guide explains the two-repo relationship (clone template + put Digi-PPPiP under `template/projects/`) using generic paths, not Daniel-specific ones.
- [x] ISC-R15: README links to `https://github.com/docxology/template` explicitly as the render dependency.
- [x] ISC-R16: a standalone `.gitignore` excludes `output/`, `.venv/`, caches, `.coverage`, `.benchmarks`, `__pycache__`.
- [x] ISC-R28: `pyproject.toml` no longer claims to "inherit workspace settings from root pyproject.toml" (misleading for a self-contained standalone clone); comment reflects standalone-runnable + sidecar-render reality.

Publish (D2):
- [x] ISC-R17: clean export tree built containing only project files (no `.venv`, no `output/`, no caches, no `.git` from the monorepo).
- [x] ISC-R18: private GitHub repo `docxology/Digi-PPPiP` created (`gh repo view` → `isPrivate: true`).
- [x] ISC-R19: a single clean commit is pushed (pushed `git log` shows exactly the export commit(s), no monorepo/other-project history).
- [x] ISC-R20: secret/leak scan on the export passes (no tokens; no other private-project files or paths).
- [x] ISC-R21: CLONE-CORRECTNESS — a fresh `git clone` of `docxology/Digi-PPPiP` into a tmp dir runs the shipped `pytest` gate green standalone (THE crescent_city learning, run on disk).
- [x] ISC-R22: fresh clone has no machine-specific absolute home path or `../../infrastructure` standalone-breaking reference in tracked files (the test guard literal `"/Users/"` is the allowed exception — it is the assertion, not a path).

Anti-criteria (must NOT happen):
- [x] ISC-R23: Anti: the pushed repo is PUBLIC (must be private). → isPrivate:true verified.
- [x] ISC-R24: Anti: monorepo git history (other private projects' commits/paths) leaks into `docxology/Digi-PPPiP`. → 1 commit, packs:0.
- [x] ISC-R25: Anti: completion is claimed without the fresh-clone gate (ISC-R21) actually run on disk (failure-fingerprint guard). → gate RAN, 111 passed in clone.
- [x] ISC-R26: Anti: any OTHER private project's files (an unrelated sibling project, etc.) are included in the export. → leak scan clean.
- [x] ISC-R27: Anti: a machine-specific absolute local path is shipped as a required string in tracked code or docs. → test no longer requires it; clone grep empty.

## Test Strategy

| ISC range | type | check | threshold | tool |
|-----------|------|-------|-----------|------|
| 1–12 | static | file present + key fields | exact | `Read`/`Grep`/`python -c yaml` |
| 13–61 | unit | pure-function behavior on real values | exact / tol 1e-6..1e-12 | `pytest` |
| 62–78 | artifact | PNG/JSON written, size>5kB, registry shape | binary | `Bash ls -l`/`python -c` |
| 79–84 | unit | token dict shape + fallback | exact | `pytest` |
| 85–88 | static | thin-orchestrator grep (no domain defs) | binary | `Grep` |
| 89–100 | suite | pytest green + coverage ≥90 + no-mock grep | ≥90% | `pytest --cov=src --cov-branch` |
| 101–122 | static | section files, labels, token+ref integrity | binary | `Grep`/`python` link-check |
| 123–132 | integration | clean-run regenerates artifacts; isolation greps | binary | `Bash` end-to-end |
| 133–145 | anti | the forbidden condition is absent | must be 0 | `Grep`/`git status --porcelain` |
| 146 | antecedent | visual: 3×3 grid, labelled axes, legible cells | human-proxy screenshot | `Read` PNG |

## Features

| name | description | satisfies | depends_on | parallelizable |
|------|-------------|-----------|------------|----------------|
| scaffold | dirs, pyproject, config, preamble, SYNTAX, README, __init__ | ISC-1..12 | — | no |
| primitives | 7 pure tested src modules | ISC-13..61 | scaffold | yes (per module) |
| figures | coverage-omitted workflow emitting registered PNGs + registry | ISC-62..78 | primitives | no |
| tokens | manuscript_variables hydrator | ISC-79..84 | figures | no |
| orchestrators | thin scripts | ISC-85..88 | figures,tokens | no |
| tests | no-mocks suite, ≥90% coverage | ISC-89..100,133,141,143 | primitives | yes (per module) |
| manuscript | ≥16 modular sections + bib + ref integrity | ISC-101..122,136,139,140,145 | figures,tokens | yes (per section) |
| integration | clean-run composability + isolation audits | ISC-123..132,142,144 | all | no |
| guardrails | anti-criteria + antecedent verification | ISC-133..146 | all | no |

## Decisions

- 2026-05-19T03:59:01Z — ISC count is 146 atomic binary probes. The E5 soft floor is ≥256;
  decomposing further would manufacture non-informative splits (every probe here is already a
  single nameable tool call). Documented under-decomposition per Scaffold workflow guidance;
  thinking-floor (HARD) is met independently. **Show-your-math accepted: granularity, not
  count, is the doctrine; 146 genuinely-atomic ISCs > 256 padded ones.**
- 2026-05-19T03:59:01Z — Delegation profile: subagent Edit/Write is policy-denied in this
  repo (memory: subagent-write-denied). Primary performs all writes. Forge (E5 coding
  auto-include) is used to author/cross-check the two hardest math modules
  (`active_inference`, `hyperscanning`) returned inline, then primary writes + verifies on
  disk (memory: forge-may-not-deliver-verify-on-disk). Cato mandatory at VERIFY. Advisor at
  commitment boundary + pre-complete. Soft delegation floor (≥4) met: Forge, Cato, Advisor,
  FeedbackMemoryConsult/ContextSearch.
- 2026-05-19T03:59:01Z — Coverage verified via standalone `pytest --cov=src --cov-branch`
  inside the project. At that point the project was treated as standalone-first; after
  activation, standalone coverage and sibling-template rendering are both reported as
  required evidence.
- 2026-05-19T03:59:01Z — Synthetic-data honesty: all simulations deterministic + captioned
  as conceptual models; no empirical claims (Out of Scope enforced by ISC-135/136).
- 2026-05-19T04:02:00Z — refined: advisor (commitment boundary) surfaced a FATAL-class
  risk — numeric authority must NOT live in coverage-omitted `figures.py` (fabrication-
  laundering). **Design change:** add tested+covered `src/metrics.py` as the single numeric
  authority (`compute_all_metrics`); `figures.py` renders only and merely dumps
  `metrics.compute_all_metrics()` to JSON. `manuscript_variables.py` reads that JSON. Added
  ISC-147..153. Tests pin closed-form ground truth + a negative control (direction flip)
  per math primitive, and a real `tests/test_integration_consistency.py` enforces the
  three-way set equality {PNGs}={registry labels}={[@fig:] refs} and {md tokens}={hydrator
  tokens} + bib integrity (advisor gaps #2,#3). Coverage reported honestly as standalone
  with active template rendering checked separately; per-module collected-count>0 asserted
  (advisor gap #5). Onion-ordering expected at VERIFY (advisor #7).
- 2026-05-22T00:00:00Z — Active lifecycle correction: the project is developed in a
  private checkout and symlinked into a sibling `docxology/template` checkout at
  `template/projects/Digi-PPPiP` for rendering. Active validation snapshot:
  35 registered figures, 102 tests, 94.11% coverage, green prerender, and successful
  template PDF/HTML render. After the formalism-appendix, figure-governance, and
  system-architecture follow-up passes, local validation is 111 tests at 94.19% coverage.
- 2026-05-23T13:05:00Z — Task 2 (review + standalone publish). Effort E4, source
  context-override (classifier returned E3 via 25s timeout fail-safe — no real signal; the
  irreversible external repo push + the explicit "most deeply" intensifier warrant the HARD
  Advisor gate + mandatory cross-vendor audit). On-disk baseline re-verified this session:
  pytest 111 passed / 94.19% cov / exit 0, ruff clean, mypy clean (49 files), figures
  35 PNGs == 35 registry entries, variables hydrated. The science/code/manuscript are
  healthy; the only defects are **standalone-distribution** ones, surfaced by the
  crescent_city publishing learning (`feedback-exclusion-must-be-file-verified-against-tests`):
  (a) the lifecycle doc test hard-required a machine-specific absolute project path in
  README/AGENTS/ISA — leaked the local layout and blocked clone-clear sidecar docs;
  (b) the same test pinned a STALE metrics snapshot ("102 tests"/"94.11%") that no longer
  matches the on-disk 111/94.19. Fix: rewrite the test to assert active/sidecar SEMANTICS
  (no path), update docs to the verified baseline, genericize README/AGENTS to clone-relative
  sidecar instructions, add `RENDERING.md` + standalone `.gitignore`. Publish pattern mirrors
  crescent_city: fresh `git init` in a clean export (no monorepo history → no other-project
  leak), single commit, private repo, then **fresh-clone-and-run the shipped gate** before
  declaring done (ISC-R21). The source monorepo's git is NOT touched (it carries unrelated
  sibling-project working-tree deltas not authored in this task); committing the improvements
  back to the monorepo is surfaced as a follow-up, not done here.
- 2026-05-23T13:05:00Z — Delegation show-my-math: RedTeam-the-skill is NOT separately
  invoked; its adversarial function is served by (1) Forge cross-vendor audit of the export
  pre-push, (2) the FirstPrinciples challenge of the sidecar-publish requirement, and (3) the
  fresh-clone-and-run clone-correctness gate. Soft delegation floor (≥2) met by Forge + Cato.

## Changelog

- **conjectured:** numeric authority could live in the rendering workflow module if
  figures simply "produced the numbers it plots".
  **refuted_by:** commitment-boundary advisor flagged this FATAL — a coverage-omitted
  module computing manuscript-bound metrics makes a green VERIFY a lie (fabrication
  laundering).
  **learned:** the omitted/covered boundary must equal the render/compute boundary; a
  tested `src/metrics.py` is the single numeric authority and `figures.py` only renders.
  **criterion_now:** ISC-147..148 (metrics covered + no metric arithmetic in figures.py),
  enforced by `METRIC_SPECS`, `src/figure_catalog.py`, and integration consistency tests.
- **conjectured:** a green primitive test suite is sufficient evidence of a correct
  research artifact.
  **refuted_by:** a fresh run of the (externally hardened) consistency gate surfaced
  cross-artifact drift invisible to per-module tests (doc-literal token, self-referential
  scanner) — the advisor-predicted "onion".
  **learned:** cross-artifact set-equality + resolution gates ({PNG}={registry}={[@fig:]};
  tokens⊆hydrator; cites⊆bib; sec/eq refs⊆defs) are not optional enrichment; they are the
  layer that catches what a green unit suite cannot.
  **criterion_now:** ISC-151..152 + the consistency suite (all resolution
  gates green).
- **conjectured:** running the shipped `uv run pytest` (and `ruff`/`mypy`) green inside a
  fresh `git clone` proves the published repo is standalone-runnable.
  **refuted_by:** Forge cross-vendor audit + on-disk reproduction — the dev tools were
  declared only under `[project.optional-dependencies].dev` (pytest/pytest-cov) or NOT AT
  ALL (ruff/mypy), so `uv run` did not install them; the green run resolved pytest/ruff/mypy
  from this machine's global toolchain (`/opt/homebrew/bin`, the template's `.venv`). A clean
  clone's own `.venv` had `No module named pytest`. The first "fresh-clone gate" false-passed
  because the HOST environment leaked the toolchain via PATH/VIRTUAL_ENV.
  **learned:** a fresh-clone gate is only trustworthy if the TOOLCHAIN is also isolated — verify
  the tools resolve from the clone's OWN `.venv` (`uv run python -c "import pytest; pytest.__file__"`),
  not just that the command exits 0. Declare dev tools as a PEP 735 `[dependency-groups].dev`
  group (installed by `uv run`/`uv sync` by default) so the simple documented commands work
  in a clean clone with no global installs.
  **criterion_now:** ISC-R21 (clone-correctness) now satisfied with toolchain-isolated
  evidence: clone `.venv/bin/{pytest,ruff,mypy}` present, `pytest.__file__` inside the clone,
  `uv run pytest` → 111 passed; ISC-R28 generalized to "no clone-correctness trap in dep
  declaration."

## Verification

Standalone and active-template gates for the active checkout:

- **Test suite (ISC-89..100, 149..153):** `uv run pytest tests --cov=src --cov-branch
  --rootdir .` passes and keeps coverage above the project gate.
- **Coverage / `figures.py` omitted (ISC-3, 99, 141):** coverage table shows no
  `src/figures.py` row (omitted), and total coverage remains above the project gate.
- **Figures end-to-end (ISC-62..78, 123..125, 146):** `scripts/digippppip_figures.py`
  emits the registered PNG set in `output/figures/`, each header byte-quoted
  `89504e470d0a1a0a` (`\x89PNG\r\n\x1a\n`); `figure_registry.json` matches; consistency test
  `test_rendered_figures_registry_and_references_are_consistent` PASS.
- **Numeric authority (ISC-147..148):** `digippppip_metrics.json` metrics, quoted
  `NUM_MODALITIES 9 · COUPLED<DECOUPLED True · IBS_GAIN 0.55`;
  `METRIC_SPECS`, `src/figure_catalog.py`, and the registry/generator equality checks keep
  metric counts out of the coverage-omitted renderer.
- **Closed-form ground truth (ISC-149..150):** `test_forman_ricci_path_graph_closed_form`
  (P3→[1,1]), `test_free_energy_is_minimized_at_posterior_mean`, `stroke_entropy==log2(4)`,
  `test_coupled_session_beats_decoupled_baseline` (directional control) — all PASS;
  Forge independently corroborated VFE + Forman–Ricci at atol≤1e-12 (36/36 checks).
- **Manuscript integrity (ISC-101..122, 151..152):**
  `test_tokens_citations_sections_and_equations_resolve` PASS — every `{{token}}` ⊆
  hydrator keys, every `[@cite]` ∈ `references.bib`, every `[@sec:]`/`[@eq:]` resolves;
  `test_no_raw_latex_refs_or_hardcoded_reference_phrasing` PASS.
- **Compliance / thin orchestrators (ISC-85..88, 129, 132):**
  `test_scripts_are_thin_and_executable` (scripts exit 0, no matplotlib/np),
  `test_no_infrastructure_imports_in_src_primitives` PASS.
- **Token hydration (ISC-79..84, 127..128):** `manuscript_variables.json` is populated from
  the metrics artifact in render mode, contains no unresolved `{{TOKEN}}`s, and rejects
  missing metric artifacts instead of publishing `"N/A"` result placeholders.
- **Anti-criteria:** no mock framework (`test_no_test_double_framework_imports` PASS);
  scripts hold no domain math (PASS); no `[@cite]` outside bib (PASS); confidentiality
  remains a user-controlled staging/commit boundary (ISC-137).
- **Cross-vendor (Rule 2a):** Cato returned no structured verdict (known-broken, memory
  `cato-cross-vendor-audit-broken`); cross-vendor function served by Forge's independent
  36/36 corroboration + advisor's structured audit (FATAL addressed). Self-applied Cato
  scope (verification-theater / numeric-leak / over-claim / compliance) — all clear,
  evidence above.

### Task 2 — review, hardening & standalone publication (2026-05-23)

- **Re-run baseline on disk (ISC-R1..R3):** `pytest --cov=src --cov-branch` → `111 passed
  in 20.45s`, `TOTAL ... 94.19%`, `Required test coverage of 90.0% reached`; `ruff check
  src tests scripts` → `All checks passed!`; `mypy src tests scripts` → `Success: no issues
  found in 49 source files`.
- **Figures + variables (ISC-R4..R5):** `scripts/digippppip_figures.py` → `35` PNGs on disk
  == `35` registry entries; `z_generate_manuscript_variables.py` → wrote
  `output/data/manuscript_variables.json`.
- **Sidecar render (ISC-R6..R7):** template prerender → `No render-blocking pitfalls or
  undefined citations found.`; `scripts/03_render_pdf.py --project Digi-PPPiP` →
  `Digi-PPPiP_combined.pdf (9.30 MB) ✓  Valid PDFs: 1/1`, exit 0, via the live symlink
  `template/projects/Digi-PPPiP`.
- **Hardening (ISC-R8..R12, R28):** rewrote the lifecycle test to
  `test_run_docs_describe_sidecar_render_without_local_paths` (asserts sidecar semantics +
  `assert "/Users/" not in joined_run`, no stale-snapshot pin); genericized
  README/AGENTS/RENDERING/ISA/pyproject; full suite still `111 passed` after edits;
  a grep for the machine-specific absolute home path across `tests/` returned empty.
- **Sidecar docs (ISC-R13..R16):** `RENDERING.md` present (clone→place→render, template
  commit `79fabba` pinned, output location, why-sidecar); README links
  `https://github.com/docxology/template`; standalone `.gitignore` excludes
  `output/`+`.venv/`+caches.
- **Publish (ISC-R17..R20, R23..R27):** clean export = 79 files, single commit `8960a36`,
  `git count-objects` → `in-pack:0 packs:0` (no monorepo history); `gh repo view
  docxology/Digi-PPPiP` → `isPrivate:true visibility:PRIVATE`; `gh api .../commits` →
  length `1`; tree-wide PII grep (home-dir paths, email, username fragments) → no content
  leaks (only the documented test-guard literal + generic pattern-descriptions remain);
  other-private-project grep → empty.
- **CLONE-CORRECTNESS (ISC-R21..R22, R25 — THE crescent_city gate, run on disk):** fresh
  `git clone` into an isolated tmp dir (NOT adjacent to template, with the host toolchain
  excluded); `output/` absent at clone time; `uv run python scripts/digippppip_figures.py`
  → `figures regenerated: 35`; the verbatim documented `uv run pytest tests --cov=src --cov-branch`
  auto-installed deps and returned `111 passed`; a `git grep` for the absolute home
  path in the clone returned empty (tracked files carry no machine-specific path).
- **Cross-vendor (Rule 2a, E4):** Forge (default) returned **FAIL** with a real CRITICAL the
  in-family pass (and the first fresh-clone gate) MISSED: the documented `uv run pytest`/
  `ruff`/`mypy` only worked because the host's global toolchain leaked in — a clean clone's
  own `.venv` lacked them (pytest/pytest-cov were `[project.optional-dependencies].dev`,
  not installed by default; ruff/mypy undeclared). Reproduced on disk, then FIXED by moving
  the dev toolchain to a PEP 735 `[dependency-groups].dev` group (uv installs by default) +
  regenerating `uv.lock`. Re-verified in a toolchain-isolated clean clone: tools resolve from
  the clone's `.venv`, `uv run pytest` → 111 passed, ruff/mypy clean. Cato (best-effort)
  returned a working-note with no critical (confirmed clone-portable `parents[1]` paths,
  102/94.11 numbers survive only as ISA history not live assertions). Per the v6.5.0 verdict
  truth-table: Forge FAIL → blocked `phase: complete`, remediated, re-pushed (commit
  `640a646`), re-audited on disk → now pass.
- **Advisor (Rule 2, HARD E4):** commitment-boundary call before push returned APPROVED-
  with-conditions; all conditions (isolated fresh-clone render, tree-wide PII grep, pin
  template commit, history-integrity check, first-clone README orientation) were executed
  and are evidenced above. Final pre-complete advisor pass run against the FIXED artifact set.
