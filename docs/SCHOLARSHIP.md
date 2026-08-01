# Digi-PPPiP Scholarship & Source Governance

This document explains how scholarship enters the project safely: the source
verification ledger, the claim ledger, study readiness, and the rules for
adding a new citation or claim.

## Two-rule summary

1. **Verify before adding.** Add external scholarship only after confirming the
   paper exists under a real, checkable metadata record — title, author, year,
   venue, and DOI or stable URL. Web-search / Perplexity results are discovery
   leads only; verify DOIs through a resolver (doi.org), publisher page,
   Crossref, DataCite, PubMed, or arXiv before touching `references.bib`.
2. **Never fabricate locators.** Preprints, theory sources, and conceptual
   simulations are marked as limited evidence. `publication.doi` in
   `manuscript/config.yaml` stays blank until a real archive or journal DOI
   exists. The manuscript is rendered as a `docxology/template` sidecar, so the
   governance ledgers generated here are consumed at render time.

## Source verification ledger (`src/source_verification.py`)

`build_source_verification_records()` reads `manuscript/references.bib` and
produces one `SourceVerificationRecord` per citekey that has a DOI or stable
URL locator. Every governed citekey (from the claim ledger, evidence graph,
figure methods, study readiness, systems governance, and manuscript citations)
must be covered, or the ledger's audit score drops below 1.0.

The `locator_status` is **`local_derived`**: it records that a DOI/URL was
derived from the local BibTeX entry. It deliberately does **not** claim that an
external resolver was queried at generation time — the pipeline is
deterministic and offline. External resolution is a separate, manual, reviewed
step before new scholarship is added.

## Claim ledger (`src/claim_ledger.py`)

`CLAIM_LEDGER` maps stable manuscript claim families (e.g. `shared_drawing_relation`,
`access_capability`) to the `evidence_keys` that support them, the `max_strength`
currently warranted, and the `next_evidence` gate required before the claim may
strengthen. Add recurring, manuscript-level evidence claims here, not only in
prose, so the claim↔source boundary stays machine-checked.

## Study readiness (`src/study_readiness.py`)

Human-subjects, dyadic archive-control, and AI-mediation protocol claims live in
`study_readiness_cases()`, each with participant rights and governing source
anchors. `audit_study_readiness()` requires the full case set and the optional
AI-branch separation, enforced by tests.

## Systems governance (`src/systems_governance.py`)

Boundary, feedback-loop, causal-assumption, ethics-gate, and reversal-path
claims for the human–human kernel and its optional branches (instrumentation,
modeling, optional AI, physiology, place, clinical translation) live in the
typed records here. `governance_score()` checks every record's fields by name
(excluding the record key) and requires nonzero `source_keys`.

## Adding a citation end to end

1. Fetch the authoritative metadata (DOI/Crossref/arXiv) for the source.
2. Add a `@type{key, …}` entry to `manuscript/references.bib`.
3. Reference it from manuscript prose with `[@key]` and, if it is a recurring
   claim, add it to `src/claim_ledger.py` (or the relevant readiness /
   governance / figure-method list) so source verification tracks it.
4. Regenerate outputs:
   ```bash
   uv run python scripts/digippppip_figures.py
   uv run python scripts/z_generate_manuscript_variables.py
   ```
5. Run the gates (see [`TESTING.md`](TESTING.md)). The integration test fails
   if any `@key` lacks a bib entry or a verification record, or if any bib entry
   lacks a locator or a named (non-"others") author.

## Guidance

- Prefer a DOI/stable URL per entry; `url` alone is acceptable for books,
  standards, and regulations where DOIs are non-standard.
- Keep keys descriptive and, where feasible, aligned to the first author and
  year (e.g. `czeszumski2022cooperative`).
- When strengthening claim language, do so only when the matching empirical
  gate (validation ladder) has been reached — not merely because a more adjacent
  citation appeared.
