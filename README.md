# Digi-PPPiP

A composable, fully-tested computational companion to the **DigiPPPiP — Digital
Partner Pen Play in Parallel** framework (a cyberphysical / temporal /
active-inference / neuroergonomic / phenomenological / accessibility /
place-based successor to Mikhailova & Friedman, 2018).

This is a self-contained research project: pure tested primitives in `src/`, a
modular Pandoc manuscript in `manuscript/`, thin orchestrator scripts, `{{TOKEN}}`
hydration, no-mocks tests, and a 90% coverage gate on the primitive layer. It has
**no renderer of its own** — the paper is produced by the
[`docxology/template`](https://github.com/docxology/template) research pipeline,
which this project plugs into as a **sidecar** (place it at
`template/projects/Digi-PPPiP`, then run the template's render). Full,
copy-paste sidecar instructions are in **[`RENDERING.md`](RENDERING.md)**.

Validation baseline (re-verified 2026-07-20, standalone): **35 registered
figures, 116 tests, ≥95% line+branch coverage** on the non-omitted `src/`
primitives (95.44% with the pinned dev toolchain), with a green template
prerender and a successful template PDF/HTML render.

> All computational illustrations are **deterministic conceptual models**, not
> empirical fNIRS/EEG findings.

> **Draft-metadata warning.** Real author metadata has not been supplied. Treat
> `manuscript/config.yaml` author fields as draft-only, leave `publication.doi`
> blank until a real archive or journal DOI exists, and do not interpret current
> author fields as publication-ready attribution.

## Layout

```
src/                 pure tested primitives (90% coverage gate)
  taxonomy.py          3×3 temporal–spatial modality taxonomy
  active_inference.py  dyadic coupled variational free energy
  hyperscanning.py     inter-brain synchrony + Forman–Ricci curvature
  narrative.py         narrative information theory (entropy/surprisal)
  aesthetics.py        active-inference epistemic arc
  neuroergonomics.py   flow / technoference / attention
  session_events.py    timestamped protocol logging + temporal classification
  outcomes.py          planned dyadic outcomes + multilevel model spec
  accessibility.py     access criteria, accommodations, and audit scoring
  source_quality.py    source classification + overclaim warnings
  claim_ledger.py      source-to-claim ledger + upgrade gates
  source_verification.py  checked DOI/stable-URL ledger + refresh triggers
  study_readiness.py   dyadic consent, archive-control, and AI-branch gates
  systems_governance.py  boundary, feedback, causal, ethics, and reversal gates
  figure_methods.py    figure-generation stages, visual grammar, audit criteria
  figure_artifact_audit.py  artifact-level registry / PNG / reference checks
  figure_catalog.py    typed figure specs + long-description source text
  provenance.py        output hashes + generated artifact inventory
  evidence.py          evidence-synthesis graph (domains → dimensions)
  metrics.py           SINGLE numeric authority (covered, tested)
  figures.py           rendering workflow ONLY (coverage-omitted)
  manuscript_variables.py  {{TOKEN}} hydrator
scripts/             thin orchestrators
manuscript/          modular Pandoc sections + config/preamble/SYNTAX/bib
tests/               no-mocks pytest suite
ISA.md               system of record (Ideal State Artifact)
AGENTS.md            local assistant/project rules
RENDERING.md         how to render the paper via the docxology/template sidecar
```

The project preamble sets compact `0.65in` PDF margins and red hyperlink,
URL, citation, anchor, and file-link colors. Keep those choices in the project
preamble so the template's infrastructure defaults do not need to be edited.

## Run (standalone)

```bash
# from this project root — generate figures + hydrate manuscript tokens
uv run python scripts/digippppip_figures.py
uv run python scripts/z_generate_manuscript_variables.py

# tests + coverage (the standalone quality gate)
uv run pytest tests --cov=src --cov-branch --cov-report=term-missing --rootdir .

# lint + types
uv run ruff check src tests scripts
uv run mypy src tests scripts
```

## Render the paper (sidecar to docxology/template)

This repository does not render PDFs by itself. To build the manuscript you
clone the [`docxology/template`](https://github.com/docxology/template) pipeline
and place this project under `template/projects/Digi-PPPiP` (symlink or copy),
then run the template's render from the template root:

```bash
# from your docxology/template checkout root, after placing Digi-PPPiP under projects/
uv run python -m infrastructure.validation.cli prerender \
  projects/Digi-PPPiP/manuscript --repo-root .
uv run python scripts/03_render_pdf.py --project Digi-PPPiP
```

See **[`RENDERING.md`](RENDERING.md)** for the full two-repo setup, including the
one-line symlink, the `./run.sh --project Digi-PPPiP --pipeline` path, and where
the output PDF lands. Do not make the public template repository track this
project's content.

## Numeric-authority rule

Every number that reaches the manuscript is computed by `src/metrics.py`
(tested, coverage-enforced) and serialized to
`output/data/digippppip_metrics.json`. `src/figures.py` renders only and never
computes a manuscript-bound metric. `tests/test_integration_consistency.py`
enforces figure/token/citation cross-artifact integrity.

## Scholarship and claims

The manuscript separates peer-reviewed sources, theory books, preprints,
reports, and official governance anchors through `src/source_quality.py` and
`src/source_verification.py`. Use verified DOI or stable-URL metadata before
adding citekeys, and keep active-inference, hyperscanning, digital-health,
accessibility, AI, privacy, and placemaking claims at the strength supported by
their source class. Perplexity or other web-search results are leads only; do
not add a source until its title, venue, year, and DOI or stable URL match.
The renderable manuscript metadata intentionally leaves `publication.doi` blank
until a real archive or journal DOI exists.

The generated-figure method is explicit in `src/figure_methods.py`: claim scope,
method lineage, tested primitive, visual encoding, deterministic render,
registry entry, caption reference, and render validation.
`src/figure_artifact_audit.py` adds an artifact-level check over generated PNG
files, registry rows, manuscript figure references, caption contracts,
dimensions, nonblank pixels, section alignment, long descriptions, and
claim-status metadata. Captions must name what is encoded, the generator or
data source, the method lineage, the manuscript role, the claim status, and the
interpretive caveat. `output/figures/long_descriptions/*.md`,
`output/data/source_verification_ledger.json`,
`output/data/study_readiness_audit.json`, and
`output/data/provenance_manifest.json` are intentional generated outputs.

The systems-governance layer in `src/systems_governance.py` keeps the
human-human mark loop separate from instrumentation, modeling, optional AI,
publication-governance, place, physiology, and clinical-translation branches.
It also exposes the capture-to-publication data-flow stages used by the
architecture and event-schema figures. Treat those records as executable claim
boundaries: each branch needs a feedback signal, causal assumption, ethics gate,
and reversal path before manuscript language can strengthen.
