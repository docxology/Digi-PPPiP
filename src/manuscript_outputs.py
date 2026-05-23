"""Manuscript output generation for DigiPPPiP.

This module owns render-preparation artifacts that are project-local and do
not depend on the public template repository infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil

from manuscript_variables import generate_variables, save_variables
from provenance import write_provenance_manifest
from source_verification import (
    audit_to_dict as source_audit_to_dict,
    build_source_verification_records,
    records_to_dicts,
    source_verification_audit,
    source_verification_required_keys,
)
from study_readiness import (
    audit_study_readiness,
    audit_to_dict as study_audit_to_dict,
    cases_to_dicts,
    study_readiness_cases,
)

TOKEN_PATTERN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
EXCLUDED_MARKDOWN = frozenset({"AGENTS.md", "README.md", "SYNTAX.md"})


@dataclass(frozen=True)
class ManuscriptOutputPaths:
    """Paths written by the manuscript output generation pass."""

    variables_path: Path
    resolved_manuscript_dir: Path
    source_ledger_path: Path
    study_audit_path: Path
    provenance_manifest_path: Path


def substitute_manuscript_tokens(text: str, variables: dict[str, str]) -> str:
    """Replace known ``{{UPPERCASE_KEY}}`` tokens and preserve unknown tokens."""

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return variables.get(key, match.group(0))

    return TOKEN_PATTERN.sub(replace, text)


def write_resolved_manuscript_tree(
    project_root: Path,
    variables: dict[str, str],
    output_dir: Path | None = None,
) -> Path:
    """Write resolved manuscript inputs to ``output/manuscript``."""
    root = Path(project_root)
    manuscript_dir = root / "manuscript"
    out_dir = output_dir or root / "output" / "manuscript"
    out_dir.mkdir(parents=True, exist_ok=True)

    for stale in tuple(out_dir.glob("*.md")) + tuple(out_dir.glob("*.bib")):
        stale.unlink()
    for stale_name in ("config.yaml", "preamble.md"):
        stale = out_dir / stale_name
        if stale.exists():
            stale.unlink()

    for path in sorted(manuscript_dir.glob("*.md")):
        if path.name in EXCLUDED_MARKDOWN:
            continue
        resolved = substitute_manuscript_tokens(path.read_text(), variables)
        (out_dir / path.name).write_text(resolved)

    for name in ("config.yaml",):
        source = manuscript_dir / name
        if source.exists():
            shutil.copy2(source, out_dir / name)

    for bib_path in sorted(manuscript_dir.glob("*.bib")):
        shutil.copy2(bib_path, out_dir / bib_path.name)

    return out_dir


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def write_source_verification_ledger(project_root: Path, output_path: Path | None = None) -> Path:
    """Write the executable source-verification ledger JSON."""
    root = Path(project_root)
    path = output_path or root / "output" / "data" / "source_verification_ledger.json"
    bib_text = (root / "manuscript" / "references.bib").read_text()
    source_records = build_source_verification_records(bib_text)
    required_source_keys = source_verification_required_keys(root / "manuscript")
    source_audit = source_verification_audit(required_source_keys, source_records)
    return _write_json(
        path,
        {
            "score": source_audit.score,
            "required_keys": sorted(required_source_keys),
            "records": records_to_dicts(source_records),
            "audit": source_audit_to_dict(source_audit),
        },
    )


def write_study_readiness_audit(project_root: Path, output_path: Path | None = None) -> Path:
    """Write the study-readiness audit JSON."""
    root = Path(project_root)
    path = output_path or root / "output" / "data" / "study_readiness_audit.json"
    study_cases = study_readiness_cases()
    study_audit = audit_study_readiness(study_cases)
    return _write_json(
        path,
        {
            "score": study_audit.score,
            "cases": cases_to_dicts(study_cases),
            "audit": study_audit_to_dict(study_audit),
        },
    )


def generate_manuscript_outputs(project_root: Path) -> ManuscriptOutputPaths:
    """Generate manuscript variables, resolved sources, ledgers, and provenance."""
    root = Path(project_root)
    variables = generate_variables(root, require_metrics=True)
    variables_path = save_variables(variables, root / "output" / "data" / "manuscript_variables.json")
    resolved_dir = write_resolved_manuscript_tree(root, variables)
    source_ledger_path = write_source_verification_ledger(root)
    study_audit_path = write_study_readiness_audit(root)
    provenance_manifest_path = write_provenance_manifest(root)
    return ManuscriptOutputPaths(
        variables_path=variables_path,
        resolved_manuscript_dir=resolved_dir,
        source_ledger_path=source_ledger_path,
        study_audit_path=study_audit_path,
        provenance_manifest_path=provenance_manifest_path,
    )
