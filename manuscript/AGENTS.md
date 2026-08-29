# Manuscript — Agent Guide

## Layout

| Path | Purpose |
|---|---|
| `config.yaml` | Authoritative metadata; parsed by the render pipeline |
| `config.yaml.example` | Schema copy with placeholder values |
| `preamble.md` | LaTeX/pandoc preamble shared by all passes |
| `00_abstract.md`–`18_formalisms_appendix.md` | Ordered section sources |
| `99_references.md` | References section; bibliography in `references.bib` |
| `SYNTAX.md` | Markup conventions (anchors, tokens, citations) |
| `cover.png` | Cover art referenced by the renderer |

## Conventions

- Numeric claims are `{{RESULT_*}}` tokens injected from generated variables at
  render time — do not hand-edit tokens into literals.
- Every citation citekey must exist in `references.bib` and be verified against
  a DOI resolver or primary source (see [`SCHOLARSHIP.md`](../SCHOLARSHIP.md)).
- Section anchors use `{#sec:...}`; cross-references between sections use them.
- Rendering happens only via the docxology/template sidecar pipeline
  ([`RENDERING.md`](../RENDERING.md)); never run ad-hoc pandoc here.

## Maintenance

Keep section files' order stable; adding a section means adding the file with
the next numeric prefix and registering it in the render order expected by the
template pipeline.
