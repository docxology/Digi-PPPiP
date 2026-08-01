"""Artifact-level checks for generated DigiPPPiP figures."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
import re
import struct
import zlib

from figure_catalog import FIGURE_CLAIM_STATUSES, FIGURE_PLACEMENTS


@dataclass(frozen=True)
class FigureArtifactCheck:
    """One artifact-level figure audit check."""

    key: str
    label: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class FigureArtifactAudit:
    """Complete artifact-level audit report for generated figures."""

    total_figures: int
    score: float
    checks: tuple[FigureArtifactCheck, ...]


REQUIRED_REGISTRY_FIELDS: frozenset[str] = frozenset(
    {
        "label",
        "png",
        "generator",
        "description",
        "claim_status",
        "caption_contract",
        "section",
        "method_source_family",
        "accessibility_description",
        "placement",
        "long_description",
    }
)


def _figure_path(figure_dir: Path, png: str) -> Path:
    return figure_dir / Path(png).name


def _sidecar_path(figure_dir: Path, sidecar: str) -> Path:
    path = Path(sidecar)
    # Reject absolute paths: sidecar references must stay inside the figure
    # output tree to avoid silently reading/writing outside the project.
    if path.is_absolute():
        raise ValueError(f"sidecar path must be relative, got {sidecar!r}")
    if path.parts[:2] == ("output", "figures"):
        return figure_dir / Path(*path.parts[2:])
    return figure_dir / path.name


def _figure_refs(manuscript_text: str) -> set[str]:
    return set(re.findall(r"@fig:([A-Za-z0-9_]+)", manuscript_text)) | set(
        re.findall(r"\{#fig:([A-Za-z0-9_]+)\}", manuscript_text)
    )


def _section_text(manuscript_text: str, section: str) -> str:
    pattern = rf"^# .*\{{#sec:{re.escape(section)}\}}.*?(?=^# .*\{{#sec:|\Z)"
    match = re.search(pattern, manuscript_text, flags=re.MULTILINE | re.DOTALL)
    return match.group(0) if match else ""


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    if not path.exists() or not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    data = path.read_bytes()
    if len(data) < 33 or data[12:16] != b"IHDR":
        return None
    return struct.unpack("!II", data[16:24])


def _png_nonblank(path: Path) -> bool:
    data = path.read_bytes()
    chunks: list[tuple[bytes, bytes]] = []
    pos = 8
    while pos + 8 <= len(data):
        length = struct.unpack("!I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        chunks.append((kind, payload))
        pos += 12 + length
    ihdr = next((payload for kind, payload in chunks if kind == b"IHDR"), None)
    if ihdr is None:
        return False
    width, height = struct.unpack("!II", ihdr[:8])
    bit_depth, color_type = ihdr[8], ihdr[9]
    if bit_depth != 8:
        return True
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    if channels is None:
        return True
    compressed = b"".join(payload for kind, payload in chunks if kind == b"IDAT")
    if not compressed:
        return False
    try:
        raw = zlib.decompress(compressed)
    except zlib.error:
        return False
    stride = 1 + width * channels
    for row in range(height):
        start = row * stride
        if any(raw[start + 1:start + stride]):
            return True
    return False


def _all_unique(values: Sequence[str]) -> bool:
    return len(values) == len(set(values))


def _read_text_if_present(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def _has_reading_guidance(text: str) -> bool:
    required_markers = ("Long description", "Reading order:", "Caveat:", "Evidence boundary:")
    return all(marker in text for marker in required_markers)


def audit_figure_artifacts(
    registry: Sequence[Mapping[str, str]],
    figure_dir: Path,
    manuscript_text: str,
) -> FigureArtifactAudit:
    """Audit generated figure files, registry rows, descriptions, and manuscript references."""
    labels = [entry.get("label", "").removeprefix("fig:") for entry in registry]
    pngs = [entry.get("png", "") for entry in registry]
    generators = [entry.get("generator", "") for entry in registry]
    refs = _figure_refs(manuscript_text)
    files = [_figure_path(figure_dir, entry.get("png", "")) for entry in registry]
    sidecars = [_sidecar_path(figure_dir, entry.get("long_description", "")) for entry in registry]
    registered_stems = {Path(png).stem for png in pngs}
    actual_stems = {path.stem for path in figure_dir.glob("*.png")}
    dimensions = [_png_dimensions(path) for path in files]

    checks = (
        FigureArtifactCheck(
            "registry_nonempty",
            "registry is nonempty",
            bool(registry),
            f"{len(registry)} registry row(s)",
        ),
        FigureArtifactCheck(
            "required_fields",
            "registry rows contain required fields",
            all(REQUIRED_REGISTRY_FIELDS <= set(entry) for entry in registry),
            ",".join(sorted(REQUIRED_REGISTRY_FIELDS)),
        ),
        FigureArtifactCheck(
            "registry_uniqueness",
            "labels, files, and generators are unique",
            _all_unique(labels) and _all_unique(pngs) and _all_unique(generators),
            "label/png/generator uniqueness",
        ),
        FigureArtifactCheck(
            "files_present",
            "registered PNG files exist",
            all(path.exists() for path in files),
            f"{sum(path.exists() for path in files)}/{len(files)} present",
        ),
        FigureArtifactCheck(
            "orphan_pngs_absent",
            "output directory has no orphan or stale PNGs",
            actual_stems == registered_stems,
            f"{len(actual_stems & registered_stems)}/{len(actual_stems | registered_stems)} matching PNG stem(s)",
        ),
        FigureArtifactCheck(
            "png_headers",
            "registered files have PNG signatures",
            all(path.exists() and path.read_bytes().startswith(b"\x89PNG") for path in files),
            "PNG signature check",
        ),
        FigureArtifactCheck(
            "dimensions_positive",
            "registered PNG files expose positive dimensions",
            all(dimension is not None and dimension[0] > 0 and dimension[1] > 0 for dimension in dimensions),
            "IHDR width and height",
        ),
        FigureArtifactCheck(
            "nonblank_pixels",
            "registered PNG files contain nonblank pixel payloads",
            all(path.exists() and _png_nonblank(path) for path in files),
            "decompressed IDAT pixel check",
        ),
        FigureArtifactCheck(
            "labels_match_manuscript",
            "registry labels match manuscript figure references",
            set(labels) == refs,
            f"{len(set(labels) & refs)}/{len(set(labels) | refs)} matching label(s)",
        ),
        FigureArtifactCheck(
            "caption_contracts",
            "registry rows carry caption contracts",
            all(bool(entry.get("caption_contract", "").strip()) for entry in registry),
            "caption_contract field is populated",
        ),
        FigureArtifactCheck(
            "caption_prose_parity",
            "manuscript prose names registered generators",
            all(generator and generator in manuscript_text for generator in generators),
            "generator names appear in manuscript captions/prose",
        ),
        FigureArtifactCheck(
            "claim_status_valid",
            "claim statuses are explicit and valid",
            all(entry.get("claim_status") in FIGURE_CLAIM_STATUSES for entry in registry),
            ",".join(sorted(FIGURE_CLAIM_STATUSES)),
        ),
        FigureArtifactCheck(
            "placement_valid",
            "figure placements are explicit and valid",
            all(entry.get("placement") in FIGURE_PLACEMENTS for entry in registry),
            ",".join(sorted(FIGURE_PLACEMENTS)),
        ),
        FigureArtifactCheck(
            "long_descriptions_present",
            "long-description sidecars exist and are nonempty",
            all(path.exists() and path.read_text().strip() for path in sidecars),
            f"{sum(path.exists() and bool(path.read_text().strip()) for path in sidecars)}/{len(sidecars)} present",
        ),
        FigureArtifactCheck(
            "readability_metadata",
            "registry rows carry figure readability metadata",
            all(
                entry.get("description", "").strip()
                and entry.get("method_source_family", "").strip()
                and entry.get("accessibility_description", "").strip()
                and entry.get("caption_contract", "").strip()
                for entry in registry
            ),
            "description/method/accessibility/caption metadata populated",
        ),
        FigureArtifactCheck(
            "long_description_reading_guidance",
            "long descriptions include reading order, caveat, and evidence boundary",
            all(_has_reading_guidance(_read_text_if_present(path)) for path in sidecars),
            "required long-description guidance markers",
        ),
        FigureArtifactCheck(
            "section_alignment",
            "figure labels appear in their declared manuscript sections",
            all(
                entry.get("section")
                and labels[index] in _section_text(manuscript_text, entry.get("section", ""))
                for index, entry in enumerate(registry)
            ),
            "section-specific label lookup",
        ),
    )
    score = sum(check.passed for check in checks) / len(checks)
    return FigureArtifactAudit(total_figures=len(registry), score=score, checks=checks)


def audit_to_dict(audit: FigureArtifactAudit) -> dict[str, object]:
    """Return a JSON-serializable audit report."""
    return {
        "total_figures": audit.total_figures,
        "score": audit.score,
        "checks": [asdict(check) for check in audit.checks],
    }
