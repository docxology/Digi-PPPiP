from pathlib import Path
import json
import re
import subprocess
import sys

from claim_ledger import claim_source_keys
from evidence import citation_keys
from figure_catalog import FIGURE_GENERATOR_NAMES, figure_specs
from figure_methods import figure_method_source_keys
from figures import main as render_figures
from manuscript_variables import generate_variables, save_variables
from metrics import NUM_FIGURES
from source_verification import (
    build_source_verification_records,
    source_verification_required_keys,
    source_verification_audit,
    source_verification_record_keys,
)
from study_readiness import audit_study_readiness, study_readiness_cases, study_readiness_source_keys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SECTION_TITLES = {
    "00_abstract.md": ("Abstract", "abstract"),
    "01_introduction.md": (
        "Introduction: From Shared Marks to Study-Ready Infrastructure",
        "introduction",
    ),
    "02_cyberphysical_expansion.md": (
        "Cyberphysical Substrate: Canvas, Body, Archive",
        "cyberphysical",
    ),
    "03_temporal_architecture.md": (
        "Temporal Coordination: Turns, Overlap, and Persistence",
        "temporal",
    ),
    "04_active_inference.md": (
        "Modeling Lens: Active Inference Without Mechanism Claims",
        "active_inference",
    ),
    "05_neuroergonomics.md": (
        "Neuroergonomic Burden and Shared Attention",
        "neuroergonomics",
    ),
    "06_cyber_phenomenology.md": (
        "Cyber-Phenomenology: Presence, Embodiment, and Mediation",
        "phenomenology",
    ),
    "07_accessibility.md": (
        "Accessible Shared Drawing: Capability Before Claim",
        "accessibility",
    ),
    "08_relational_aesthetics.md": (
        "Relational Aesthetics: Coauthored Marks and Social Form",
        "relational_aesthetics",
    ),
    "09_place_based.md": (
        "Place-Based Micropractice and Digital Placemaking",
        "place",
    ),
    "10_taxonomy.md": (
        "Temporal-Spatial Taxonomy for Study Design",
        "taxonomy",
    ),
    "11_dyadic_digital_health.md": (
        "Dyadic Digital Health: Consent, Relationship Boundaries, and AI Separation",
        "health",
    ),
    "12_methods_protocol.md": (
        "Methods Protocol: Governance, Provenance, and Validation",
        "methods_protocol",
    ),
    "13_research_agenda.md": (
        "Research Agenda: From Feasibility to Evidence",
        "agenda",
    ),
    "14_integrative_model.md": (
        "Integrative Model: The Human-Human DigiPPPiP Kernel",
        "integrative",
    ),
    "15_discussion.md": (
        "Discussion: Limits, Failure Modes, and Future Replacement",
        "discussion",
    ),
    "16_casestudies.md": (
        "Case Studies: Dementia Care as a Stress Test",
        "casestudies",
    ),
    "17_conclusions.md": (
        "Conclusions: Study-Ready Without Overclaiming",
        "conclusions",
    ),
    "18_formalisms_appendix.md": (
        "Appendix: Free-Energy and Active-Inference Formalisms",
        "formalisms_appendix",
    ),
    "99_references.md": ("References", "references"),
}

FORMALISM_EQUATION_LABELS = {
    "vfe",
    "posterior",
    "forman_ricci",
    "shannon",
    "epistemic_arc",
}
FORMALISM_FIGURE_LABELS = {
    "active_inference_mapping",
    "active_inference_loop",
    "network_analysis_pipeline",
    "geometric_hyperscanning",
    "hyperscanning_alignment",
    "narrative_information",
    "epistemic_arc",
}


def _manuscript_text() -> str:
    section_files = sorted((PROJECT_ROOT / "manuscript").glob("[0-9][0-9]_*.md"))
    return "\n".join(path.read_text() for path in section_files)


def _bib_keys() -> set[str]:
    text = (PROJECT_ROOT / "manuscript" / "references.bib").read_text()
    return set(re.findall(r"@\w+\{([^,]+),", text))


def _bib_entries() -> dict[str, str]:
    text = (PROJECT_ROOT / "manuscript" / "references.bib").read_text()
    return {
        match.group(1): match.group(0)
        for match in re.finditer(r"@\w+\{([^,]+),.*?(?=\n@|\Z)", text, flags=re.DOTALL)
    }


def _citation_refs() -> set[str]:
    citation_refs = set(re.findall(r"@([A-Za-z0-9_]+)", _manuscript_text()))
    return {key for key in citation_refs if not key.startswith(("fig", "sec", "eq", "tbl"))}


def _section_headings() -> dict[str, tuple[str, str]]:
    headings: dict[str, tuple[str, str]] = {}
    for path in sorted((PROJECT_ROOT / "manuscript").glob("[0-9][0-9]_*.md")):
        first_line = path.read_text().splitlines()[0]
        match = re.fullmatch(r"#\s+(.+?)\s+\{#sec:([A-Za-z0-9_]+)\}", first_line)
        assert match is not None
        headings[path.name] = (match.group(1), match.group(2))
    return headings


def _syntax_section_registry() -> dict[str, tuple[str, str]]:
    syntax_text = (PROJECT_ROOT / "manuscript" / "SYNTAX.md").read_text()
    rows: dict[str, tuple[str, str]] = {}
    for match in re.finditer(
        r"^\|\s+`([^`]+[.]md)`\s+\|\s+(.+?)\s+\|\s+`\{#sec:([A-Za-z0-9_]+)\}`\s+\|$",
        syntax_text,
        flags=re.MULTILINE,
    ):
        rows[match.group(1)] = (match.group(2), match.group(3))
    return rows


def _syntax_equation_registry() -> dict[str, str]:
    syntax_text = (PROJECT_ROOT / "manuscript" / "SYNTAX.md").read_text()
    rows: dict[str, str] = {}
    for match in re.finditer(
        r"^\|\s+`\{#eq:([A-Za-z0-9_]+)\}`\s+\|.+?\|\s+`([^`]+[.]md)`\s+\|$",
        syntax_text,
        flags=re.MULTILINE,
    ):
        rows[match.group(1)] = match.group(2)
    return rows


def test_section_titles_labels_and_syntax_registry_are_consistent():
    headings = _section_headings()
    syntax_rows = _syntax_section_registry()

    assert headings == EXPECTED_SECTION_TITLES
    assert syntax_rows == EXPECTED_SECTION_TITLES
    assert len(headings) == 20


def test_formalisms_appendix_owns_equations_and_model_figures():
    appendix = (PROJECT_ROOT / "manuscript" / "18_formalisms_appendix.md").read_text()
    active_inference_main = (PROJECT_ROOT / "manuscript" / "04_active_inference.md").read_text()
    main_text = "\n".join(
        path.read_text()
        for path in sorted((PROJECT_ROOT / "manuscript").glob("[0-9][0-9]_*.md"))
        if path.name < "18_formalisms_appendix.md"
    )
    syntax_equations = _syntax_equation_registry()

    assert set(re.findall(r"\{#eq:([A-Za-z0-9_]+)\}", appendix)) == FORMALISM_EQUATION_LABELS
    assert not re.search(r"\{#eq:[A-Za-z0-9_]+\}", main_text)
    assert "{#fig:" not in active_inference_main
    assert "{#eq:" not in active_inference_main
    assert "@sec:formalisms_appendix" in active_inference_main
    assert {label: syntax_equations[label] for label in FORMALISM_EQUATION_LABELS} == {
        label: "18_formalisms_appendix.md" for label in FORMALISM_EQUATION_LABELS
    }

    specs_by_label = {spec.label.removeprefix("fig:"): spec for spec in figure_specs()}
    assert {specs_by_label[label].section for label in FORMALISM_FIGURE_LABELS} == {"formalisms_appendix"}
    for label in FORMALISM_FIGURE_LABELS:
        assert f"{{#fig:{label}" in appendix
        assert f"{{#fig:{label}" not in main_text


def test_run_docs_describe_sidecar_render_without_local_paths():
    """Run/render docs must document the template-sidecar contract and stay
    clone-portable.

    Replaces an earlier check that hard-required a machine-specific absolute
    project path in the docs and pinned a stale test/coverage snapshot. Both
    coupled the repo to one machine and broke a standalone clone. The robust
    invariants are: (a) every run/render doc names
    the template render relationship; (b) no machine-specific absolute path leaks
    into a published clone; (c) the docs never regress to stale "passive / not
    rendered" framing.
    """
    run_docs = {
        path.name: path.read_text()
        for path in (
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "AGENTS.md",
            PROJECT_ROOT / "RENDERING.md",
        )
    }
    joined_run = "\n".join(run_docs.values())

    # (a) The sidecar render contract is documented in every run/render doc.
    for name, text in run_docs.items():
        assert "template" in text.lower(), f"{name} omits the template render relationship"
    assert "render" in joined_run.lower()

    # (b) No machine-specific absolute path leaks into a published standalone clone.
    assert "/Users/" not in joined_run, "a local absolute path leaked into the run/render docs"

    # (c) No regression to stale "passive / not rendered" framing across prose docs.
    guard_text = joined_run + "\n" + (PROJECT_ROOT / "ISA.md").read_text()
    assert "private passive project" not in guard_text.lower()
    assert "passive projects are not rendered" not in guard_text.lower()
    assert "optional only after promotion" not in guard_text.lower()
    assert "`04_active_inference.md` covers FEP" not in guard_text
    assert "`04_active_inference.md` references `[@fig:active_inference_loop]`" not in guard_text


def test_rendered_figures_registry_and_references_are_consistent():
    paths = render_figures(PROJECT_ROOT)
    assert len(paths) == NUM_FIGURES
    assert all(path.read_bytes().startswith(b"\x89PNG") for path in paths)
    registry = json.loads((PROJECT_ROOT / "output" / "figures" / "figure_registry.json").read_text())
    registry_stems = {Path(entry["png"]).stem for entry in registry}
    registry_labels = {entry["label"].removeprefix("fig:") for entry in registry}
    png_stems = {path.stem for path in paths}
    text = _manuscript_text()
    figure_refs = set(re.findall(r"@fig:([A-Za-z0-9_]+)", text))
    assert registry_stems == png_stems == registry_labels == figure_refs
    assert tuple(entry["generator"] for entry in registry) == FIGURE_GENERATOR_NAMES
    assert all(entry["long_description"] for entry in registry)
    assert all((PROJECT_ROOT / entry["long_description"]).exists() for entry in registry)
    artifact_audit = json.loads((PROJECT_ROOT / "output" / "figures" / "figure_artifact_audit.json").read_text())
    assert artifact_audit["score"] == 1.0
    provenance = json.loads((PROJECT_ROOT / "output" / "data" / "provenance_manifest.json").read_text())
    assert provenance["config_hash"]
    assert provenance["metrics_hash"]
    assert provenance["figure_registry_hash"]
    assert provenance["outputs"]["figures"]["count"] == NUM_FIGURES


def test_syntax_figure_registry_matches_generated_registry():
    render_figures(PROJECT_ROOT)
    registry = json.loads((PROJECT_ROOT / "output" / "figures" / "figure_registry.json").read_text())
    generated_labels = {entry["label"].removeprefix("fig:") for entry in registry}
    syntax_text = (PROJECT_ROOT / "manuscript" / "SYNTAX.md").read_text()
    syntax_labels = set(re.findall(r"\{#fig:([A-Za-z0-9_]+)\}", syntax_text))
    figure_refs = set(re.findall(r"@fig:([A-Za-z0-9_]+)", _manuscript_text()))
    assert syntax_labels == generated_labels == figure_refs


def test_tokens_citations_sections_and_equations_resolve():
    render_figures(PROJECT_ROOT)
    variables = generate_variables(PROJECT_ROOT, require_metrics=True)
    save_variables(variables, PROJECT_ROOT / "output" / "data" / "manuscript_variables.json")
    text = _manuscript_text()
    tokens = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", text))
    assert tokens <= set(variables)

    assert _citation_refs() <= _bib_keys()
    assert citation_keys() <= _bib_keys()
    assert claim_source_keys() <= _bib_keys()
    assert figure_method_source_keys() <= _bib_keys()
    assert study_readiness_source_keys() <= _bib_keys()
    source_records = build_source_verification_records((PROJECT_ROOT / "manuscript" / "references.bib").read_text())
    required_source_keys = source_verification_required_keys(PROJECT_ROOT / "manuscript")
    assert required_source_keys <= source_verification_record_keys(source_records)
    assert source_verification_audit(required_source_keys, source_records).score == 1.0
    assert audit_study_readiness(study_readiness_cases()).score == 1.0

    section_defs = set(re.findall(r"\{#sec:([A-Za-z0-9_]+)\}", text))
    section_refs = set(re.findall(r"@sec:([A-Za-z0-9_]+)", text))
    assert section_refs <= section_defs

    equation_defs = set(re.findall(r"\{#eq:([A-Za-z0-9_]+)\}", text))
    equation_refs = set(re.findall(r"@eq:([A-Za-z0-9_]+)", text))
    assert equation_refs <= equation_defs

    table_defs = set(re.findall(r"\{#tbl:([A-Za-z0-9_]+)\}", text))
    table_refs = set(re.findall(r"@tbl:([A-Za-z0-9_]+)", text))
    assert table_refs <= table_defs

    script = PROJECT_ROOT / "scripts" / "z_generate_manuscript_variables.py"
    completed = subprocess.run([sys.executable, str(script)], cwd=PROJECT_ROOT, check=False)
    assert completed.returncode == 0
    resolved_text = "\n".join(
        path.read_text() for path in sorted((PROJECT_ROOT / "output" / "manuscript").glob("[0-9][0-9]_*.md"))
    )
    assert not re.search(r"\{\{[A-Z0-9_]+\}\}", resolved_text)
    assert '"N/A"' not in (PROJECT_ROOT / "output" / "data" / "manuscript_variables.json").read_text()
    source_ledger = PROJECT_ROOT / "output" / "data" / "source_verification_ledger.json"
    study_audit = PROJECT_ROOT / "output" / "data" / "study_readiness_audit.json"
    provenance = PROJECT_ROOT / "output" / "data" / "provenance_manifest.json"
    assert source_ledger.exists()
    assert study_audit.exists()
    assert provenance.exists()
    source_ledger_payload = json.loads(source_ledger.read_text())
    assert source_ledger_payload["score"] == 1.0
    assert set(source_ledger_payload["required_keys"]) == required_source_keys
    assert all(record["title"] for record in source_ledger_payload["records"])
    assert all(record["author"] for record in source_ledger_payload["records"])
    assert all(record["year"] for record in source_ledger_payload["records"])
    assert all(record["venue"] for record in source_ledger_payload["records"])
    assert all(record["metadata_source"] == "local_bibtex" for record in source_ledger_payload["records"])
    assert json.loads(study_audit.read_text())["score"] == 1.0


def test_used_bibliography_entries_have_verified_locators_and_named_authors():
    entries = _bib_entries()
    used_keys = _citation_refs() | citation_keys()
    assert used_keys <= set(entries)
    missing_locator = [
        key for key in sorted(used_keys) if not re.search(r"^\s*(doi|url)\s*=", entries[key], re.MULTILINE)
    ]
    placeholder_authors = [
        key for key in sorted(used_keys) if re.search(r"\bothers\b", entries[key], re.IGNORECASE)
    ]
    assert missing_locator == []
    assert placeholder_authors == []


def test_project_metadata_does_not_publish_placeholder_doi():
    config_text = (PROJECT_ROOT / "manuscript" / "config.yaml").read_text()
    assert "zenodo.00000000" not in config_text
    doi_match = re.search(r'^\s*doi:\s*"([^"]*)"', config_text, re.MULTILINE)
    assert doi_match is not None
    doi = doi_match.group(1).strip()
    assert doi == "" or not re.search(r"(00000000|example|placeholder)", doi, re.IGNORECASE)


def test_no_raw_latex_refs_or_hardcoded_reference_phrasing():
    text = _manuscript_text()
    assert "\\cite{" not in text
    assert "\\ref{" not in text
    assert "\\eqref{" not in text
    assert not re.search(r"\b(Figure|Section|Equation)\s+\d+", text)


def test_project_sources_and_docs_avoid_hardcoded_numbered_references():
    paths = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "AGENTS.md",
        PROJECT_ROOT / "ISA.md",
        *sorted((PROJECT_ROOT / "src").glob("*.py")),
        *sorted((PROJECT_ROOT / "scripts").glob("*.py")),
        *sorted((PROJECT_ROOT / "manuscript").glob("*.md")),
    ]
    offenders: list[str] = []
    for path in paths:
        text = path.read_text()
        if re.search(r"\b(Figure|Section|Equation)\s+\d+", text):
            offenders.append(str(path.relative_to(PROJECT_ROOT)))
    assert offenders == []


def test_scripts_are_thin_and_executable():
    scripts = sorted((PROJECT_ROOT / "scripts").glob("*.py"))
    assert scripts
    for script in scripts:
        text = script.read_text()
        assert "matplotlib" not in text
        assert "np." not in text
        assert "infrastructure." not in text
    for script in scripts:
        completed = subprocess.run([sys.executable, str(script)], cwd=PROJECT_ROOT, check=False)
        assert completed.returncode == 0


def test_no_test_double_framework_imports_and_collection_is_nonempty():
    tests = sorted((PROJECT_ROOT / "tests").glob("test_*.py"))
    assert tests
    for path in tests:
        text = path.read_text()
        assert not re.search(r"^\s*from\s+unittest[.]mock\b", text, re.MULTILINE)
        assert not re.search(r"^\s*(from|import)\s+mock\b", text, re.MULTILINE)
        assert not re.search(r"^\s*patch[(]", text, re.MULTILINE)
        assert "def test_" in text


def test_no_infrastructure_imports_in_src_primitives():
    for path in (PROJECT_ROOT / "src").glob("*.py"):
        if path.name == "figures.py":
            continue
        text = path.read_text()
        assert not re.search(r"^\s*import\s+infrastructure\b", text, re.MULTILINE)
        assert not re.search(r"^\s*from\s+infrastructure\b", text, re.MULTILINE)
