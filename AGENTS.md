# AGENTS.md - Digi-PPPiP Project Guidance

This research project uses the separate [docxology/template](https://github.com/docxology/template) renderer. See the [pinned workflow](docs/RENDERING.md) for the current manuscript location and how to preserve the deposited outputs.

## Read Order

1. `README.md`
2. `docs/RENDERING.md` (how the paper is rendered via the template sidecar)
3. `docs/INDEX.md` (factored technical documentation: architecture, figures,
   testing, scholarship)
4. `docs/history/ISA.md`
5. `docs/manuscript/SYNTAX.md`

## Architecture Rules

- Keep business logic in `src/`.
- Keep `scripts/` as thin orchestrators over `src/` APIs.
- Do not import the template's `infrastructure.*` packages from pure source primitives.
- Do not add mocks or fake data layers to tests; use deterministic real values.
- Treat every generated figure as conceptual unless it is backed by real participant data.
- Keep reusable figure-method logic in `src/figure_methods.py`; `src/figures.py` renders only.
- Keep typed figure labels, filenames, statuses, sections, method-source families, placements, and long-description text in `src/figure_catalog.py`.
- Keep claim-to-source governance in `src/claim_ledger.py`, executable source verification in `src/source_verification.py`, study-readiness governance in `src/study_readiness.py`, systems-boundary governance in `src/systems_governance.py`, and figure artifact checks in `src/figure_artifact_audit.py`.
- Valid figure statuses are `conceptual`, `protocol`, `audit`, `analytic_simulation`, and `empirical_placeholder`; do not reintroduce the older analytic/empirical shortcut.
- When figure methods cite scholarship, map sources to explicit method gates in `src/figure_methods.py`; do not leave source support only in prose.

## Manuscript Rules

- Use Pandoc citekeys, figure labels, equation labels, and section labels.
- Do not hard-code numbered references; use labels for figures, equations, and sections.
- Keep manuscript-bound scalar values on the tested path: `src/metrics.py` -> `output/data/digippppip_metrics.json` -> `src/manuscript_variables.py` -> `output/data/manuscript_variables.json`.
- Pipeline and render callers (`src/manuscript_outputs.py`, `scripts/z_generate_manuscript_variables.py` without `--allow-draft`) pass `require_metrics=True` so result-derived tokens fail instead of falling back to `"N/A"`.
- Add external scholarship only after verifying title, author, year, venue, and DOI or stable URL.
- Treat web-search and Perplexity output as discovery leads only; verify DOI/title pairs through a DOI resolver, publisher page, Crossref, DataCite, PubMed, or arXiv before editing `references.bib`.
- Add recurring evidence claims to `src/claim_ledger.py` when they become manuscript-level claims, not only to prose.
- Add human-subjects, dyadic archive-control, or AI-mediation protocol claims to `src/study_readiness.py` when they become manuscript-level requirements.
- Add boundary, feedback-loop, causal-assumption, ethics-gate, or reversibility claims to `src/systems_governance.py` when they become manuscript-level systems claims.
- Preserve the recorded publication DOI and author attribution. Keep any future edition metadata tied to its own deposit.
- Mark preprints, theory sources, and conceptual simulations as limited evidence.

## Validation

Use the [standalone test guide](docs/TESTING.md) and the [pinned Template workflow](docs/RENDERING.md). Generated verification artifacts belong in a clean sparse checkout with the retained `output/` excluded.
