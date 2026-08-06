# Digi-PPPiP — Documentation Index

This folder holds the project's factored technical documentation. The four
root-level files remain canonical and are read by the integration gate; the
documents below go deeper into individual subsystems:

| Document | Covers |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | `src/` module map, data-flow, the numeric-authority rule, and governance layers |
| [`FIGURES.md`](FIGURES.md) | The figure system: catalog, rendering workflow, method contract, caption contract, and artifact audit |
| [`TESTING.md`](TESTING.md) | The pytest suite: organization, coverage gate, no-mocks discipline, and how to run it |
| [`SCHOLARSHIP.md`](SCHOLARSHIP.md) | Source verification, the claim ledger, study readiness, and how to add scholarship safely |
| [`RENDERING.md`](../RENDERING.md) | (root) How the paper is rendered via the `docxology/template` sidecar |

## Suggested reading order

New to the repo: `README.md` → `RENDERING.md` → `ARCHITECTURE.md` →
`FIGURES.md` → `TESTING.md`.

Working on a manuscript claim: `SCHOLARSHIP.md` + `manuscript/SYNTAX.md`.

Validating a change: `TESTING.md` (gates) → run the commands listed there.

## Quick orientation

- **39 registered figure generators**, each with a typed spec in
  `src/figure_catalog.py` and a render function in `src/figures.py`.
- **128 tests**, ≥90% branch-coverage gate on `src/` (currently ~97.45%).
- **138 governed BibTeX citekeys** with source-verification records.
- Figures, token values, and manuscript labels are cross-referenced by
  `tests/test_integration_consistency.py`.

All paths in these documents are relative to the repository root.
