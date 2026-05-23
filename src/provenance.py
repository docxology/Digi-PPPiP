"""Provenance manifest utilities for DigiPPPiP generated artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class OutputProvenance:
    """Summary of one output family."""

    count: int
    files: tuple[str, ...]


@dataclass(frozen=True)
class ProvenanceManifest:
    """Hashes and output inventory for reproducible manuscript artifacts."""

    generated_at: str
    config_hash: str
    metrics_hash: str
    figure_registry_hash: str
    manuscript_hash: str
    outputs: dict[str, OutputProvenance]


def hash_file(path: Path) -> str:
    """Return the SHA-256 hash for a file, or an empty string if absent."""
    if not path.exists() or not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_many(paths: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path).encode("utf-8"))
        if path.exists() and path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest() if paths else ""


def _files(root: Path, pattern: str) -> tuple[Path, ...]:
    if not root.exists():
        return ()
    return tuple(sorted(path for path in root.glob(pattern) if path.is_file()))


def _output(root: Path, directory: str, pattern: str) -> OutputProvenance:
    files = _files(root / "output" / directory, pattern)
    return OutputProvenance(
        count=len(files),
        files=tuple(str(path.relative_to(root)) for path in files),
    )


def build_provenance_manifest(project_root: Path, *, generated_at: str | None = None) -> ProvenanceManifest:
    """Build the project output provenance manifest."""
    root = Path(project_root)
    manuscript_files = _files(root / "manuscript", "[0-9][0-9]_*.md") + (
        root / "manuscript" / "references.bib",
        root / "manuscript" / "config.yaml",
    )
    return ProvenanceManifest(
        generated_at=generated_at or datetime.now(UTC).isoformat(),
        config_hash=hash_file(root / "manuscript" / "config.yaml"),
        metrics_hash=hash_file(root / "output" / "data" / "digippppip_metrics.json"),
        figure_registry_hash=hash_file(root / "output" / "figures" / "figure_registry.json"),
        manuscript_hash=_hash_many(tuple(path for path in manuscript_files if path.exists())),
        outputs={
            "figures": _output(root, "figures", "*.png"),
            "figure_long_descriptions": _output(root, "figures/long_descriptions", "*.md"),
            "data": _output(root, "data", "*.json"),
            "manuscript": _output(root, "manuscript", "*.md"),
            "pdf": _output(root, "pdf", "*.pdf"),
            "web": _output(root, "web", "*"),
        },
    )


def manifest_to_dict(manifest: ProvenanceManifest) -> dict[str, object]:
    """Return a JSON-serializable provenance manifest."""
    return {
        "generated_at": manifest.generated_at,
        "config_hash": manifest.config_hash,
        "metrics_hash": manifest.metrics_hash,
        "figure_registry_hash": manifest.figure_registry_hash,
        "manuscript_hash": manifest.manuscript_hash,
        "outputs": {key: asdict(value) for key, value in manifest.outputs.items()},
    }


def write_provenance_manifest(project_root: Path, output_path: Path | None = None) -> Path:
    """Write the provenance manifest JSON and return its path."""
    root = Path(project_root)
    path = output_path or root / "output" / "data" / "provenance_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_provenance_manifest(root)
    path.write_text(json.dumps(manifest_to_dict(manifest), indent=2, sort_keys=True) + "\n")
    return path
