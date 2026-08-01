# Digi-PPPiP Testing

This document explains how the test suite is organized, what the coverage gate
guarantees, and how to run the non-render validation (no template checkout
required).

## What is tested

22 test files cover every `src/` module. A hard rule (enforced by
`tests/test_integration_consistency.py`) is that **no mocks or test doubles are
allowed** — tests use only deterministic real values. Every test passes an
explicit seed where randomness is involved, so output is reproducible.

The suite is split into:

- **Unit tests** — one file per `src/` module (`test_taxonomy.py`,
  `test_active_inference.py`, `test_metrics.py`, …), pinning closed-form math,
  edge cases, and error paths with `pytest.raises`.
- **`tests/test_integration_consistency.py`** — cross-artifact integrity:
  figure registry vs. rendered PNGs vs. manuscript `@fig:` references; tokens
  vs. hydrator output; citations vs. `references.bib`; section/equation/table
  labels; scripts being thin and executable; and the no-mocks / no-infrastructure
  import audits.

## Coverage gate

`pyproject.toml` sets `[tool.coverage.report] fail_under = 90` with branch
coverage over `src/` (omitting `src/figures.py`, which is render-only and has no
numeric authority). Current total is ~97.45%; every `src/` module sits at or
above 90% individually.

`figure_artifact_audit.py`, `hyperscanning.py`, `neuroergonomics.py`, and
`session_events.py` were the historically weakest modules; targeted edge-case
tests raised each above the gate.

## Running the gates

```bash
# from the project root
uv run pytest tests --cov=src --cov-branch --cov-report=term-missing --rootdir .
uv run ruff check src tests scripts
uv run mypy src tests scripts
```

Regenerate figures and manuscript variables before rendering:

```bash
uv run python scripts/digippppip_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Interpreting a failure

- A **figure/registry/label** failure means generated artifacts or manuscript
  references are out of sync — regenerate figures, then check
  `output/figures/figure_artifact_audit.json` and `figure_registry.json`.
- A **token/variable** failure means `output/data/digippppip_metrics.json` is
  missing or stale, or a `{{TOKEN}}` has no hydrator value — run the two
  regeneration scripts or update `src/manuscript_variables.py`.
- A **citation** failure means a `@citekey` has no matching `references.bib`
  entry, or a source-verification record is incomplete.
- A **source-verification** failure means `source_verification_ledger.json` is
  stale relative to the bibliography — regenerate outputs.

## Guidance for adding tests

- Add one test file mirroring the module under test; keep it deterministic and
  mock-free.
- Cover error paths with `pytest.raises` and edge cases (empty inputs, negative
  values, boundary thresholds).
- If a test relies on randomness, pass an explicit seed.
- Keep the integration-consistency invariants intact — do not weaken the
  registry/label/citation closure checks.
