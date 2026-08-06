# Digi-PPPiP Figures

This document describes the figure system end to end: how a figure is declared
in the typed catalog, how it is rendered, what the method and caption contracts
require, and how `figure_artifact_audit.py` verifies the produced artifacts.

## The figure lifecycle

1. **Declared** — a `FigureSpec` in `src/figure_catalog.py` (label, filename,
   generator, manuscript section, claim status, method-source family,
   accessibility description, placement).
2. **Warranted** — the method contract in `src/figure_methods.py` maps each
   figure to a generation stage, audit criteria, and a scholarly source family.
3. **Rendered** — a `generate_<name>()` function in `src/figures.py` draws a
   deterministic PNG into `output/figures/` and registers a row in
   `figure_registry.json`.
4. **Described** — a long-description sidecar is written under
   `output/figures/long_descriptions/`.
5. **Audited** — `figure_artifact_audit.py` verifies artifact integrity.
6. **Referenced** — the manuscript cites the figure by Pandoc label.

There are 39 registered figures. `scripts/digippppip_figures.py` regenerates
all of them deterministically. The rendered PNGs are consumed by the
`docxology/template` sidecar pipeline at PDF/HTML render time (see
[`../RENDERING.md`](../RENDERING.md)).

## Claim statuses

Valid statuses (enforced by `FIGURE_CLAIM_STATUSES`):

- `conceptual` — a framework illustration, not a measurement.
- `protocol` — encodes study/protocol structure, not results.
- `audit` — encodes the project's own governance machinery.
- `analytic_simulation` — a deterministic toy/synthetic diagnostic.
- `empirical_placeholder` — reserves a slot for future participant data.

The status is stamped onto the figure itself and recorded in the registry, so a
viewer can tell at a glance that the image is not participant outcome evidence.

## Method contract (`src/figure_methods.py`)

Figures are treated as reproducible *claim objects* rather than decoration.
Each generation stage states an artifact and a quality gate (claim scope →
method lineage → tested primitive → visual encoding → deterministic render →
registry → caption reference → accessibility description → render validation).
The audit criteria require deterministic inputs, a registry entry, a caption
contract, a claim boundary, source alignment, method lineage, accessibility
text, legend/axis integrity, aesthetic accessibility, text-fit readability,
render resolution, auto-numbered refs, and a visible claim-status stamp.

## Caption contract

Every manuscript figure caption should name, per `CAPTION_CONTRACT_ITEMS`:

1. What the figure encodes.
2. Which code module or data source generated it.
3. Which method lineage warrants the figure form.
4. Which manuscript argument it supports.
5. How to read the main marks, axes, or panels.
6. Whether it is conceptual, protocol, audit, analytic simulation, or empirical
   placeholder.
7. Which caveat limits interpretation.
8. What future evidence would upgrade the claim.

`figure_artifact_audit.py` checks that generator names appear in manuscript
prose (`caption_prose_parity`) and that every registry row carries a populated
caption contract.

## Artifact audit (`src/figure_artifact_audit.py`)

After rendering, the audit verifies: registry uniqueness, PNG files present,
no orphan PNGs, label↔reference match, caption contracts populated, claim-status
and placement validity, long descriptions present and non-empty, readability
metadata populated, and long-description reading guidance markers present.

Run it (standalone) via:

```bash
uv run python scripts/digippppip_figures.py
# then inspect output/figures/figure_artifact_audit.json
```

## Viewing / extension

To add a figure: add a `FigureSpec` in `src/figure_catalog.py`, a
`generate_<name>()` in `src/figures.py`, a caption in the appropriate
`manuscript/NN_*.md`, and (if it is claim-bearing) update the methods contract
or claim ledger as appropriate. The integration test
(`tests/test_integration_consistency.py::test_rendered_figures_registry_and_references_are_consistent`)
will fail unless registry, PNG, and manuscript references all agree.
