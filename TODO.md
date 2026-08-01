# Deferred work

This file tracks only open work. Completed windows are logged at the bottom;
the project's quality gates (pytest, ruff, mypy, coverage) define what the
manuscript may claim regardless of anything listed here.

## Status / Owner / Last reviewed

- Status: Open
- Owner: @digi-pppip-authors
- Last reviewed: 2026-07-31

## Open — outside the current instrument boundary

- The shared witness register (cross-line co-registration of report envelopes)
  is a separate DAF project by design; this project ships the figure generation
  and manuscript and stops.
- No external attestation or independent observation provenance is claimed.
  Adding an independently authored observation ledger needs its own testable
  provenance contract.
- Clinical/physiology deployment is out of scope until a reviewed protocol,
  intervention description, adverse-event route, and prespecified outcomes are
  in place.

## Open — from the 2026-07-31 red-team deep-review window, deferred with a stated reason

### Medium

1. **`source_verification.py` still does not perform live external DOI/URL
   resolution** — `locator_status` was honestly relabelled to `local_derived`
   (it no longer overclaims external verification), but the module still does
   not query a resolver at generation time.
   - Why it matters: the ledger proves locators + metadata exist locally; it
     does not prove a DOI resolves or a title/author pair matches a publisher
     page. Per AGENTS.md that is a manual, reviewed step before new scholarship
     is added.
   - Suggested fix: keep the manual gate (do NOT add network calls to a
     deterministic, offline pipeline). If live resolution is ever wanted, it
     must be an opt-in, seeded/recorded separate step — not part of the default
     figure/test path.

2. **`manuscript/SYNTAX.md`-driven figure/section/equation registries are
   asserted only by `test_integration_consistency.py`** — the single source of
   truth for which labels may be used lives in prose, not a machine-enforced
   schema.
   - Why it matters: adding a figure/section/equation label requires updating
     prose in two places; a mismatch fails only when the integration test runs.
   - Suggested fix: acceptable as-is (integration test guards it); optionally
     generate SYNTAX.md rows from the typed catalogs to remove the duplication.

3. **Four BibTeX citekeys don't match their first author / year** — **RESOLVED
   2026-07-31.** Renamed across manuscript + src/ + tests:
   - `luo2022cooperative` → `czeszumski2022cooperative` (first author Czeszumski)
   - `stephens2024narrativeinfo` → `schulz2024narrativeinfo` (first author Schulz)
   - `bolis2023secondperson` → `bolis2024secondperson` (entry year is 2024)
   - `digital2025relationship` → `kernova2025relationship` (first author Kernová)
   Verified: zero old keys remain; every in-prose citation still resolves to a
   bib entry.

- Update `README.md`, `AGENTS.md`, and `RENDERING.md` baseline to reflect the
  current on-disk state whenever a test or coverage figure changes (they are
  the published validation baseline). A stale number here silently reports the
  wrong state. (Docs now tagged 2026-07-31 / 128 tests / 97.45%.)
- Keep the factored docs in `docs/` (INDEX, ARCHITECTURE, FIGURES, TESTING,
  SCHOLARSHIP) in sync with source: `tests/test_integration_consistency.py::test_docs_folder_is_factored_and_referenced`
  guards that the index's advertised files exist and the root README/AGENTS link
  to them. Add any new top-level doc to INDEX's table and that test's allow-list.

### Minor

1. **`src/evidence.py` `is_acyclic()` cycle-detection** — **RESOLVED 2026-07-31.**
   `is_acyclic()` now accepts an explicit `edges` argument, and a new
   `test_is_acyclic_detects_a_cycle` verifies a synthetic two-node cycle returns
   False while the real edge layer stays acyclic.
2. **`src/manuscript_variables.py` `_stringify` uses `%g` float formatting** —
   lossy for very small/large manuscript-bound scalars.
   - Why it matters: manuscript prose shows `0.0001` where `0.000100` was
     intended; low practical risk given the current value ranges.
   - Suggested fix: keep `%g` but document the intentional lossiness in the
     docstring (marked as accepted behaviour).
3. **`web-app/server/` has no automated test suite** — the Python pytest suite
   covers `src/`, but the Socket.IO relay has no tests.
   - Why it matters: a refactor of `index.js` could break relay behaviour with
     no gate catching it.
   - Suggested fix: add a minimal Node test (e.g. `node:test` + socket.io-client)
     asserting connect/broadcast/disconnect, plus payload-cap, rate-limit, and
     CORS behaviour.
4. **`pyproject.toml` version `0.1.0` vs `manuscript/config.yaml` `paper.version:
   "1.0"`** — reviewer flagged the mismatch. These are intentionally separate
   versioning domains (Python package version vs manuscript draft version), so
   no change is warranted; noted here so the distinction is explicit.
5. **`mikhailova2018pppip` title "PPPiParadigm"** — reviewer flagged as a typo.
   Verified against Crossref DOI `10.3390/arts7030039`: the published title IS
   "A New PPPiParadigm for Relationship Improvement". **No change** — the bib
   entry is correct as published.

## Completed / Closed (from the 2026-07-31 red-team pass)

- **Git hygiene**: `web-app/server/node_modules/` (845 files) removed from
  tracking; `node_modules/`, `**/node_modules/`, `web-app/client/dist*`, and
  `helpful/` added to `.gitignore`; the stray 9.3 MB
  `helpful/Digi-PPPiP_combined.pdf` duplicate removed from tracking. Tracked
  file count dropped 950 → 104.
- **Web-app server hardened** (`web-app/server/index.js`): CORS origin is now
  env-configurable (`CORS_ORIGIN`) with a conservative local default instead of
  `"*"`; per-event payload size cap (64 KiB) on `draw_path`/`undo_stroke`/
  `cursor_move`; connection cap (`MAX_CONNECTIONS`) with a `server_full` event;
  connection counter replaced with a Set (cannot drift negative on reconnect);
  per-socket token-bucket rate limit (`RATE_LIMIT`, default 240 events/sec) to
  throttle broadcast amplification; `maxHttpBufferSize` pinned to 64 KiB;
  graceful SIGTERM/SIGINT shutdown added. `web-app/server/README.md` documents
  the tuning knobs.
- **`src/metrics.py`**: `METRIC_SPECS["NUM_FIGURES"]` corrected from `"figures"`
  (a coverage-omitted module) to `"figure_catalog"` (the real covered source).
  `compute_all_metrics` now validates config (non-negative seed, positive
  steps/nodes/precisions) at the boundary instead of failing deeper.
- **`src/session_events.py`**: `turn_balance` gained an optional
  `partner_actors` set so AI/facilitator/third actors can be excluded from the
  dyadic balance denominator as the docstring promised (legacy behaviour
  preserved when omitted).
- **`src/source_verification.py`**: overclaiming `locator_status="matched"`
  relabelled to the honest `"local_derived"` with a transparency note in the
  module docstring; BibTeX entry splitting and field extraction are now
  brace-aware (nested braces and `@` in field values no longer truncate
  entries). Audit check label updated accordingly.
- **`src/systems_governance.py`**: `governance_score` now checks fields by name
  (excluding `key`) instead of filtering by value comparison, so a field whose
  value equals the record key is no longer skipped.
- **`src/figure_artifact_audit.py`**: `_sidecar_path` rejects absolute paths
  (raises `ValueError`) instead of silently returning them, preventing reads
  outside the figure output tree.
- **Docs truth**: README/AGENTS/RENDERING baseline updated to 126 tests /
  97.45% coverage / 2026-07-31; README numeric-authority rule clarified that
  `figures.py` only invokes the covered `metrics.compute_all_metrics()` and
  never computes a scalar; `active_inference.py` decoupled-mode docstring
  corrected ("constant from the first update onward"); ISA progress/updated
  headers bumped.
- **Tests + coverage**: 10 new tests added (turn_balance partner filtering,
  metrics config validation + spec-source audit, brace-aware BibTeX parsing,
  quoted/absent fields, governance field-by-name score, absolute-sidecar
  rejection, PNG parsing edge branches, hyperscanning/neuroergonomics edge
  cases, session-event field validation). Coverage rose 95.56% → **97.45%**,
  test count 116 → **126**. Every src/ module is now ≥ 90% individually
  (was: `figure_artifact_audit` 85.71%, `hyperscanning` 88.51%,
  `neuroergonomics` 87.76%, `session_events` 88.76%).
- **Citekey renames (S1)**: four BibTeX keys aligned with first-author/year
  across manuscript + src/ + tests (`luo2022cooperative`→`czeszumski2022cooperative`,
  `stephens2024narrativeinfo`→`schulz2024narrativeinfo`,
  `bolis2023secondperson`→`bolis2024secondperson`,
  `digital2025relationship`→`kernova2025relationship`); zero old keys remain,
  every citation resolves. 127 tests now pass.
- **`is_acyclic` cycle-detection**: `evidence.is_acyclic()` accepts an explicit
  `edges` list; new test proves a synthetic cycle is detected while the real
  edge layer stays acyclic. `figure_method_counts` test strengthened with pinned
  exact counts so it is no longer tautological.
- **Gates green**: 127 passed, 0 failed; ruff clean; mypy clean; figure + token
  regeneration scripts run clean.
- **Docs factored into `docs/`**: added `docs/INDEX.md` (entry point + layout),
  `ARCHITECTURE.md`, `FIGURES.md`, `TESTING.md`, and `SCHOLARSHIP.md`; linked
  them from `README.md` (layout + a Documentation section), updated `AGENTS.md`
  read order, and added a guard test
  `test_docs_folder_is_factored_and_referenced` that verifies INDEX's advertised
  files exist and that root docs link to `docs/INDEX.md`. Baseline numbers in
  README/AGENTS/RENDERING/docs corrected to 128 tests. (128 tests now pass.)
