# Digi-PPPiP Manuscript

Source of truth for the rendered paper: `manuscript/` holds the SECTION files,
configuration, bibliography, and preamble consumed by the
`docxology/template` sidecar pipeline (see root [`RENDERING.md`](../RENDERING.md)).

## Layout

- `config.yaml` — paper metadata (title, authors, publication DOI, keywords, rendering, license)
- `config.yaml.example` — copy of the config schema with placeholders
- `preamble.md` — shared preamble included before section content
- `references.bib` — BibTeX bibliography (resolved by Pandoc at render time)
- `00_abstract.md` … `18_formalisms_appendix.md` — ordered section files
- `99_references.md` — references section
- `SYNTAX.md` — manuscript markup conventions used in this repo
- `cover.png` — cover art

## Conventions

- Section files are ordered by numeric prefix and combined at render time.
- Numeric results appear as `{{TOKEN}}` placeholders (e.g. `{{RESULT_FE_REDUCTION_ABS}}`)
  injected from generated manuscript variables at render time — they are
  intentional, not unresolved gaps.
- Citations use bracketed Pandoc syntax resolved against `references.bib`.
