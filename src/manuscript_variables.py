"""Manuscript variable generation for DigiPPPiP.

The hydrator returns flat ``UPPERCASE_KEY -> str`` values for the template
renderer. Configuration-derived values come from ``manuscript/config.yaml``;
result-derived values come from ``output/data/digippppip_metrics.json`` and use
``"N/A"`` only in exploratory draft mode when the figure/metrics pass has not
run. Render-mode callers should use ``require_metrics=True`` so missing metric
artifacts fail before placeholder values can enter the manuscript.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

RESULT_KEYS: tuple[str, ...] = (
    "NUM_MODALITIES",
    "NUM_TEMPORAL_MODES",
    "NUM_SPATIAL_CONFIGS",
    "NUM_EVIDENCE_DOMAINS",
    "NUM_EVIDENCE_DIMENSIONS",
    "EVIDENCE_COVERAGE_PCT",
    "NUM_EVENT_LOG_FIELDS",
    "EVENT_LOG_MEAN_INTERVAL_S",
    "EVENT_LOG_TURN_BALANCE",
    "NUM_OUTCOME_MEASURES",
    "NUM_OUTCOME_DOMAINS",
    "DEFAULT_DESIGN_STRENGTH_SCORE",
    "NUM_ACCESSIBILITY_CRITERIA",
    "ACCESSIBILITY_AUDIT_SCORE",
    "NUM_SOURCE_QUALITY_TYPES",
    "NUM_CLAIM_BOUNDARY_DOMAINS",
    "NUM_VALIDATION_LADDER_STAGES",
    "NUM_SYSTEM_BOUNDARY_ELEMENTS",
    "NUM_FEEDBACK_LOOPS",
    "NUM_CAUSAL_ASSUMPTIONS",
    "NUM_ETHICS_GATES",
    "SYSTEM_GOVERNANCE_SCORE",
    "NUM_FIGURE_METHOD_STAGES",
    "NUM_FIGURE_AUDIT_CRITERIA",
    "NUM_VISUAL_ENCODING_ROLES",
    "NUM_FIGURE_METHOD_SOURCE_FAMILIES",
    "NUM_CAPTION_CONTRACT_ITEMS",
    "FIGURE_METHOD_SCORE",
    "NUM_FIGURES",
    "TAXONOMY_PEAK_SYNCHRONY",
    "COUPLED_FE_FINAL",
    "DECOUPLED_FE_FINAL",
    "FE_REDUCTION_ABS",
    "IBS_INITIATION_MEAN",
    "IBS_CONVERGENCE_MEAN",
    "IBS_GAIN",
    "CURVATURE_ENTROPY_MAX",
    "NUM_CURVATURE_TRANSITIONS",
    "NARRATIVE_MAX_ENTROPY_BITS",
    "EPISTEMIC_AHA_MAGNITUDE",
    "EPISTEMIC_PEAK_STEP",
)


def _load_config(project_root: Path) -> dict[str, Any]:
    path = project_root / "manuscript" / "config.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _load_metrics(project_root: Path, *, required: bool = False) -> dict[str, Any]:
    path = project_root / "output" / "data" / "digippppip_metrics.json"
    if not path.exists():
        if required:
            raise FileNotFoundError(f"required metrics artifact is missing: {path}")
        return {}
    return cast(dict[str, Any], json.loads(path.read_text()))


def _config_hash(project_root: Path) -> str:
    path = project_root / "manuscript" / "config.yaml"
    if not path.exists():
        return "N/A"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _stringify(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def generate_variables(project_root: Path, *, require_metrics: bool = False) -> dict[str, str]:
    """Generate renderer-ready variables for every ``{{TOKEN}}`` in the manuscript."""
    root = Path(project_root)
    config = _load_config(root)
    metrics = _load_metrics(root, required=require_metrics)
    if require_metrics:
        missing_keys = sorted(set(RESULT_KEYS) - set(metrics))
        if missing_keys:
            raise KeyError(f"metrics artifact is missing required key(s): {missing_keys}")
    paper = config.get("paper", {})
    publication = config.get("publication", {})
    experiment = config.get("experiment", {})

    variables: dict[str, str] = {
        "CONFIG_TITLE": _stringify(paper.get("title", "DigiPPPiP")),
        "CONFIG_SUBTITLE": _stringify(paper.get("subtitle", "")),
        "CONFIG_VERSION": _stringify(paper.get("version", "1.0")),
        "CONFIG_PUBLICATION_YEAR": _stringify(publication.get("year", "2026")),
        "CONFIG_NUM_MODALITIES": _stringify(
            len(experiment.get("temporal_modes", [])) * len(experiment.get("spatial_configs", []))
        ),
        "CONFIG_NUM_TEMPORAL_MODES": _stringify(len(experiment.get("temporal_modes", []))),
        "CONFIG_NUM_SPATIAL_CONFIGS": _stringify(len(experiment.get("spatial_configs", []))),
        "CONFIG_SESSION_STEPS": _stringify(experiment.get("session_steps", "N/A")),
        "CONFIG_DYADIC_STEPS": _stringify(experiment.get("dyadic_steps", "N/A")),
        "CONFIG_NUM_DIMENSIONS": _stringify(metrics.get("NUM_EVIDENCE_DIMENSIONS", "N/A")),
        "CONFIG_HASH": _config_hash(root),
        "GENERATION_TIMESTAMP": datetime.now(timezone.utc).isoformat(),
    }

    for key in RESULT_KEYS:
        variables[f"RESULT_{key}"] = _stringify(metrics.get(key, "N/A"))

    return {key: value for key, value in sorted(variables.items())}


def save_variables(variables: dict[str, str], path: Path) -> Path:
    """Write sorted manuscript variables JSON and return the output path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(sorted(variables.items())), indent=2, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    root = Path.cwd()
    save_variables(generate_variables(root), root / "output" / "data" / "manuscript_variables.json")
