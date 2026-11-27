# Render the Digi-PPPiP manuscript

The canonical source is under [docs/manuscript](manuscript/README.md). The deposited PDF and tracked `output/` are retained records. Use a fresh sparse checkout that omits `output/` before regenerating the synthetic figures, metrics, and hydrated sections. The four tracked interface screenshots are used as figure inputs.

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/docxology/Digi-PPPiP.git
cd Digi-PPPiP
git sparse-checkout set --no-cone '/*' '!/output/'
uv sync --locked --python 3.11
uv run --locked --no-sync python scripts/digippppip_figures.py
uv run --locked --no-sync python scripts/z_generate_manuscript_variables.py
```

The figure script uses deterministic conceptual cases and the supplied demo images. The hydrator reads the generated metrics and writes resolved sources in `output/manuscript/`. Missing metrics fail the hydration. The scripts use local files and do not recruit study participants or obtain measurement data.

Use a separate [Template checkout](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2) at `87704feae0a4490ef7dad9c931d268e8c30273c2`, with Pandoc, pandoc-crossref, and LaTeX from the [Template run guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/RUN_GUIDE.md). Set `digi_checkout` to the absolute Digi-PPPiP checkout path. Run from Template with a fresh project slot.

```sh
uv sync --locked --no-dev
mkdir -p projects/working
ln -s "$digi_checkout" projects/working/Digi-PPPiP
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/Digi-PPPiP --skip-manuscript-hydration
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/Digi-PPPiP
```

Inspect the combined PDF under `output/pdf/`, HTML at `output/web/index.html`, and validation and provenance reports under `output/reports/` in the Digi-PPPiP checkout. Keep these outputs in the verification checkout. The [release PDF](../Digi-PPPiP_combined.pdf) continues to identify the deposited edition. See [standalone checks](TESTING.md) for the Python suite.
