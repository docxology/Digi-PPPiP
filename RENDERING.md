# Rendering the Digi-PPPiP paper (sidecar to `docxology/template`)

`Digi-PPPiP` is a **content repository**, not a renderer. It ships the manuscript,
the figure-generation code, the tests, and the project configuration — but the
machinery that turns Markdown + figures into a PDF (Pandoc, XeLaTeX, validation,
the multi-stage pipeline) lives in a separate, reusable repository:
[`docxology/template`](https://github.com/docxology/template).

You render the paper by running this project **inside** a `docxology/template`
checkout, as a *sidecar* project under `template/projects/`. The two repos stay
independent in git; they only meet on disk at render time.

```
docxology/template/              ← the rendering pipeline (clone separately)
├── infrastructure/              ← Pandoc/XeLaTeX/validation engine
├── scripts/                     ← pipeline orchestrators (00–09)
├── run.sh                       ← interactive + pipeline entry point
└── projects/
    ├── template_code_project/   ← exemplars shipped with the template
    ├── template_prose_project/
    └── Digi-PPPiP/              ← THIS repo, placed here (symlink or copy)
```

---

## 1. Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python env + runner used by both repos)
- A LaTeX toolchain for PDF output (XeLaTeX via TeX Live / MacTeX), as required
  by `docxology/template`. The template's own README covers LaTeX package setup.
- `git`

## 2. Clone both repositories side by side

```bash
# pick any working directory
git clone https://github.com/docxology/template.git
git clone https://github.com/docxology/Digi-PPPiP.git
```

> **Validated against** `docxology/template` @ `79fabba` (2026-05-23). The template
> pipeline is designed to be forward-compatible, but `docxology/template` evolves;
> if a future template revision changes the render contract and the steps below
> fail, check out the template at this commit (`git -C template checkout 79fabba`)
> to reproduce the validated render, then upgrade.

## 3. Place Digi-PPPiP under the template's `projects/`

The template discovers projects under `template/projects/<name>`. Make this repo
visible there with a **symlink** (recommended — no duplication):

```bash
ln -s "$(pwd)/Digi-PPPiP" template/projects/Digi-PPPiP
```

…or a **copy**, if you prefer not to symlink:

```bash
cp -R Digi-PPPiP template/projects/Digi-PPPiP
```

> The public `docxology/template` repository only ever tracks its two exemplar
> projects. A symlinked or copied `projects/Digi-PPPiP` is local-only and is
> never committed back to the template — do not force it into the template's git.

## 4. Generate this project's figures + manuscript tokens

Run the project's own (standalone) steps first so the figures, the metrics JSON,
and the hydrated `{{TOKEN}}` values exist before rendering:

```bash
cd template/projects/Digi-PPPiP        # or this repo's root directly
uv run python scripts/digippppip_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```

## 5. Render the paper from the template root

```bash
cd ../../                              # back to the docxology/template root

# (a) validate the manuscript is render-ready
uv run python -m infrastructure.validation.cli prerender \
  projects/Digi-PPPiP/manuscript --repo-root .

# (b) render the PDF
uv run python scripts/03_render_pdf.py --project Digi-PPPiP
```

Or use the interactive / full-pipeline entry point, which runs figures, tests,
render, and validation end to end:

```bash
./run.sh --project Digi-PPPiP --pipeline
```

## 6. Where the output lands

The template writes deliverables under its own `output/` tree:

```
template/output/Digi-PPPiP/pdf/      ← the rendered PDF(s)
template/output/Digi-PPPiP/figures/  ← figures copied into the deliverable
template/output/Digi-PPPiP/reports/  ← validation reports
```

Everything under `output/` is disposable and regeneratable — it is never
committed (see `.gitignore`).

---

## Standalone checks (no template needed)

You can exercise everything except PDF rendering directly from this repo:

```bash
uv run python scripts/digippppip_figures.py        # 35 figures → output/figures/
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests --cov=src --cov-branch --cov-report=term-missing --rootdir .
uv run ruff check src tests scripts
uv run mypy src tests scripts
```

Baseline (re-verified 2026-07-20): **35 registered figures, 116 tests, ≥95%
line+branch coverage** (95.44% with the pinned dev toolchain), ruff + mypy clean.
All dev tools (pytest, ruff, mypy) are pinned in `uv.lock` under the `dev`
dependency group, so the commands above work in a fresh clone with no global
installs.

## Why a sidecar?

Keeping the pipeline in `docxology/template` and the content here means: the
rendering engine is maintained and upgraded once for every project; this repo
stays small, reviewable, and focused on the science; and the manuscript can be
re-rendered by anyone who clones both repos, with no project-specific build
infrastructure to maintain.
