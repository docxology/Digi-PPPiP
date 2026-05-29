"""Figure rendering workflow for DigiPPPiP.

This module is intentionally coverage-omitted: it renders artifacts and writes
registries, while all manuscript-bound scalar authority stays in
``src/metrics.py`` and the pure primitives. Figure meaning and claim status are
defined in covered modules before this renderer turns them into PNG artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
import textwrap
from typing import Callable, cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np
import yaml  # type: ignore[import-untyped]

from accessibility import domain_scores
from active_inference import simulate_dyadic_session
from aesthetics import epistemic_arc, order_change_balance
from claim_ledger import claim_records
from evidence import build_evidence_graph
from figure_artifact_audit import audit_figure_artifacts, audit_to_dict
from figure_catalog import FIGURE_GENERATOR_NAMES, figure_long_description_map, figure_spec_by_generator
from figure_methods import (
    aesthetic_grammar_rules,
    aesthetic_palette,
    caption_contract_items,
    composition_archetypes,
    contrast_ratio,
    figure_audit_criteria,
    figure_generation_stages,
    figure_method_source_families,
    figure_method_score,
    visual_encoding_channels,
)
from hyperscanning import (
    PHASES,
    curvature_entropy,
    detect_phase_transitions,
    forman_ricci_curvature,
    inter_brain_network,
    simulate_ibs_phases,
)
from metrics import compute_all_metrics
from narrative import convergence_index, pivotal_moments, stroke_entropy, surprisal
from neuroergonomics import attention_allocation, intentional_enclosure_gain, technoference_cost
from outcomes import OUTCOME_MEASURES, multilevel_model_spec, outcome_domains
from provenance import write_provenance_manifest
from session_events import example_protocol_events, summarize_event_log
from source_verification import build_source_verification_records, source_verification_required_keys, source_verification_summary
from source_quality import CLAIM_STRENGTH_LEVELS, TYPE_STRENGTH, claim_boundaries, validation_ladder
from study_readiness import study_readiness_matrix_rows
from systems_governance import data_flow_stages, system_architecture_lanes
from taxonomy import SpatialConfig, TemporalMode, build_taxonomy, taxonomy_matrix

FigureGenerator = Callable[[Path], Path]

PALETTE = aesthetic_palette()

GRAMMAR = {
    "actor": PALETTE["blue"],
    "artifact": PALETTE["green"],
    "signal": PALETTE["orange"],
    "context": PALETTE["purple"],
    "caution": PALETTE["red"],
    "neutral": PALETTE["gray"],
}

FIGURE_FOOTER = (
    "Deterministic project-code figure; not participant outcome data unless stated."
)

FIGURE_REGISTRY: list[dict[str, str]] = []
TAXONOMY_CELL_LABEL_MAX_CHARS = 20
TAXONOMY_CELL_LABEL_MAX_LINES = 3
CLAIM_LEDGER_LABEL_MAX_CHARS = 28

CLAIM_LEDGER_DISPLAY_LABELS = {
    "shared_drawing_relation": "shared drawing relation",
    "workspace_awareness": "workspace awareness",
    "temporal_coordination": "temporal coordination",
    "active_inference_model": "active inference model",
    "digital_art_therapy_boundary": "art therapy boundary",
    "neuroergonomic_burden_boundary": "neuroergonomic burden",
    "phenomenological_presence_boundary": "phenomenological presence",
    "access_capability": "access capability",
    "relational_coregulation_boundary": "relational co-regulation",
    "place_micropractice": "place micropractice",
    "long_distance_place_boundary": "long-distance place",
    "figure_provenance": "figure provenance",
    "dyadic_privacy_governance": "privacy governance",
    "systems_boundary_governance": "systems governance",
    "lightweight_intimacy": "lightweight intimacy",
    "ai_relationship_boundary": "AI relationship boundary",
}


def taxonomy_cell_label_lines(
    label: str,
    *,
    max_chars: int = TAXONOMY_CELL_LABEL_MAX_CHARS,
    max_lines: int = TAXONOMY_CELL_LABEL_MAX_LINES,
) -> tuple[str, ...]:
    """Return bounded, matrix-safe line breaks for taxonomy cell labels."""
    normalized = " ".join(label.split())
    if not normalized:
        return ("",)

    lines: list[str] = []
    segments = normalized.split(" + ")
    for index, segment in enumerate(segments):
        suffix = " +" if index < len(segments) - 1 else ""
        wrapped = textwrap.wrap(
            f"{segment.strip()}{suffix}",
            width=max_chars,
            break_long_words=False,
            break_on_hyphens=False,
        )
        lines.extend(wrapped or [f"{segment.strip()}{suffix}"])

    if len(lines) <= max_lines and all(len(line) <= max_chars for line in lines):
        return tuple(lines)

    fallback = textwrap.wrap(
        normalized,
        width=max_chars,
        max_lines=max_lines,
        placeholder="...",
        break_long_words=True,
        break_on_hyphens=False,
    )
    return tuple(fallback or [normalized[:max_chars]])


def claim_ledger_display_label(
    claim_id: str,
    *,
    max_chars: int = CLAIM_LEDGER_LABEL_MAX_CHARS,
) -> str:
    """Return a one-line label that fits the dense claim-ledger figure."""
    label = CLAIM_LEDGER_DISPLAY_LABELS.get(claim_id, claim_id.replace("_", " "))
    return textwrap.shorten(label, width=max_chars, placeholder="...")


def _rgba_to_hex(rgba: tuple[float, float, float, float] | tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(channel * 255):02X}" for channel in rgba[:3])


def _contrast_text_color(background_hex: str) -> str:
    candidates = (PALETTE["ink"], "#FFFFFF")
    return max(candidates, key=lambda foreground: contrast_ratio(foreground, background_hex))


def apply_visualization_style() -> None:
    """Apply a compact, colourblind-safe Matplotlib style."""
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 9.5,
            "axes.titlesize": 12.5,
            "axes.labelsize": 10,
            "legend.fontsize": 8,
            "figure.facecolor": PALETTE["paper"],
            "savefig.facecolor": PALETTE["paper"],
            "axes.facecolor": PALETTE["paper"],
            "axes.titleweight": "bold",
            "axes.edgecolor": PALETTE["gray"],
            "axes.labelcolor": PALETTE["ink"],
            "xtick.color": PALETTE["ink"],
            "ytick.color": PALETTE["ink"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": PALETTE["line"],
            "grid.alpha": 0.32,
            "lines.linewidth": 2.2,
        }
    )


def register_figure(
    label: str,
    png: str,
    generator: str,
    description: str,
) -> None:
    """Append one figure metadata row to the in-memory registry."""
    spec = figure_spec_by_generator(generator)
    if label != spec.label or Path(png).name != spec.filename:
        raise RuntimeError(f"figure registration does not match typed spec for {generator}")
    FIGURE_REGISTRY.append(
        {
            "label": label,
            "png": png,
            "generator": generator,
            "description": description,
            "claim_status": spec.claim_status,
            "caption_contract": "; ".join(caption_contract_items()),
            "section": spec.section,
            "method_source_family": spec.method_source_family,
            "accessibility_description": spec.accessibility_description,
            "placement": spec.placement,
            "long_description": f"output/figures/long_descriptions/{Path(spec.filename).stem}.md",
        }
    )


def _save(
    fig: plt.Figure,
    out_dir: Path,
    filename: str,
    label: str,
    description: str,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    generator = _caller_name()
    claim_status = figure_spec_by_generator(generator).claim_status
    _stamp_figure(fig, generator=generator, claim_status=claim_status)
    fig.tight_layout(rect=(0, 0.085, 1, 0.985))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    register_figure(label, f"output/figures/{filename}", generator, description)
    return path


def _caller_name() -> str:
    import inspect

    return inspect.stack()[2].function


def _load_experiment(project_root: Path) -> dict[str, object]:
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.exists():
        return {}
    config = yaml.safe_load(config_path.read_text()) or {}
    experiment = config.get("experiment", {})
    return experiment if isinstance(experiment, dict) else {}


def _project_root_from_out_dir(out_dir: Path) -> Path:
    """Return the project root for an ``output/figures`` directory."""
    return Path(out_dir).resolve().parents[1]


def _figure_experiment(out_dir: Path) -> dict[str, object]:
    """Load experiment configuration for a figure generator."""
    return _load_experiment(_project_root_from_out_dir(out_dir))


def _int_param(config: dict[str, object], key: str, default: int) -> int:
    value = config.get(key, default)
    if isinstance(value, str | int | float):
        return int(value)
    raise TypeError(f"experiment.{key} must be int-compatible")


def _float_param(config: dict[str, object], key: str, default: float) -> float:
    value = config.get(key, default)
    if isinstance(value, str | int | float):
        return float(value)
    raise TypeError(f"experiment.{key} must be float-compatible")


def _setup_canvas(ax: Axes, title: str) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(
        plt.Rectangle(
            (0.012, 0.035),
            0.976,
            0.895,
            facecolor="#FFFFFF",
            alpha=0.84,
            edgecolor=PALETTE["line"],
            linewidth=0.9,
            zorder=-10,
        )
    )
    ax.text(0.026, 0.965, "DigiPPPiP governed visual grammar", fontsize=6.4, color=PALETTE["gray"])
    ax.set_title(title, pad=16, color=PALETTE["ink"])


def _stamp_figure(fig: plt.Figure, *, generator: str, claim_status: str) -> None:
    status_colors = {
        "conceptual": PALETTE["violet"],
        "protocol": PALETTE["green"],
        "audit": PALETTE["blue"],
        "analytic_simulation": PALETTE["orange"],
        "empirical_placeholder": PALETTE["red"],
    }
    status_color = status_colors.get(claim_status, GRAMMAR["caution"])
    fig.text(
        0.01,
        0.018,
        claim_status.upper(),
        ha="left",
        va="bottom",
        fontsize=6.8,
        weight="bold",
        color="#FFFFFF",
        bbox={"boxstyle": "round,pad=0.26", "fc": status_color, "ec": status_color, "lw": 0.0},
    )
    fig.text(
        0.24,
        0.018,
        f"{generator} | {FIGURE_FOOTER}",
        ha="left",
        va="bottom",
        fontsize=6.4,
        color="#64748b",
    )


def _box(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    *,
    color: str,
    width: float = 0.18,
    height: float = 0.12,
    fontsize: int = 8,
    alpha: float = 0.18,
) -> None:
    shadow = FancyBboxPatch(
        (x - width / 2 + 0.006, y - height / 2 - 0.006),
        width,
        height,
        boxstyle="round,pad=0.014,rounding_size=0.018",
        facecolor=PALETTE["gray"],
        alpha=0.08,
        edgecolor="none",
        zorder=0,
    )
    ax.add_patch(shadow)
    rect = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.014,rounding_size=0.018",
        facecolor=color,
        alpha=alpha,
        edgecolor=color,
        linewidth=1.15,
        zorder=1,
    )
    ax.add_patch(rect)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, wrap=True, color=PALETTE["ink"], zorder=2)


def _arrow(ax: Axes, start: tuple[float, float], end: tuple[float, float], *, color: str | None = None) -> None:
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={"arrowstyle": "->", "color": color or GRAMMAR["neutral"], "lw": 1.3},
    )


def _caveat(ax: Axes, text: str) -> None:
    ax.text(
        0.5,
        0.04,
        text,
        ha="center",
        va="center",
        fontsize=8,
        color=GRAMMAR["caution"],
        bbox={"boxstyle": "round,pad=0.25", "fc": "#FFF2EC", "ec": GRAMMAR["caution"], "lw": 0.95},
    )


def _panel_label(ax: Axes, label: str) -> None:
    ax.text(
        0.01,
        0.98,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        weight="bold",
        color="#0f172a",
        bbox={"boxstyle": "round,pad=0.18", "fc": "#f8fafc", "ec": "#cbd5e1", "lw": 0.7},
    )


def generate_evolution_timeline(out_dir: Path) -> Path:
    """Render the conceptual evolution from PPPiP to DigiPPPiP."""
    labels = ["paper", "screen", "hybrid", "brain", "story", "place"]
    years = [2018, 2020, 2023, 2025, 2026, 2026.5]
    y = np.array([1, 1.4, 1.1, 1.7, 1.35, 1.55])
    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    ax.plot(years, y, color=PALETTE["blue"], linewidth=2.5)
    ax.scatter(years, y, s=120, color=list(PALETTE.values())[: len(years)], zorder=3)
    for x, yy, label in zip(years, y, labels):
        ax.text(x, yy + 0.07, label, ha="center", va="bottom", weight="bold")
    ax.set_yticks([])
    ax.set_ylim(0.82, 2.05)
    ax.set_xlabel("conceptual timeline")
    ax.set_title(
        "DigiPPPiP extends PPPiP from paper practice to cyberphysical research program",
        pad=12,
    )
    ax.set_xlim(2017.6, 2027)
    return _save(
        fig,
        out_dir,
        "evolution_timeline.png",
        "fig:evolution_timeline",
        "Conceptual timeline from paper PPPiP to cyberphysical DigiPPPiP.",
    )


def generate_cyberphysical_spectrum(out_dir: Path) -> Path:
    """Render the physical-to-digital modality spectrum."""
    modes = ["physical", "digital", "hybrid", "AR", "VR", "asynchronous"]
    x = np.arange(len(modes))
    haptic = np.array([0.95, 0.30, 0.70, 0.65, 0.45, 0.35])
    reach = np.array([0.05, 0.90, 0.70, 0.65, 0.80, 0.95])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, haptic, marker="o", label="haptic richness", color=PALETTE["green"])
    ax.plot(x, reach, marker="s", label="geographic reach", color=PALETTE["purple"])
    ax.fill_between(x, haptic, reach, color=PALETTE["sky"], alpha=0.16)
    ax.set_xticks(x, modes, rotation=20, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("affordance score")
    ax.set_title("Cyberphysical DigiPPPiP trades haptic richness against reach")
    ax.legend()
    return _save(
        fig,
        out_dir,
        "cyberphysical_spectrum.png",
        "fig:cyberphysical_spectrum",
        "Affordance spectrum for physical, digital, hybrid, AR, VR, and asynchronous modes.",
    )


def generate_cpss_architecture(out_dir: Path) -> Path:
    """Render DigiPPPiP as a cyber-physical-social system."""
    lanes = system_architecture_lanes()
    status_colors = {
        "inside kernel": PALETTE["blue"],
        "support boundary": PALETTE["sky"],
        "computed lens": PALETTE["violet"],
        "outside default": PALETTE["orange"],
        "evidence boundary": PALETTE["green"],
    }
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    ax.text(
        0.03,
        0.94,
        "default path is human-human; models, logs, AI, and publication checks are governed branches",
        fontsize=8.4,
        color=PALETTE["gray"],
        ha="left",
        va="center",
    )
    for index, lane in enumerate(lanes):
        y = 0.82 - index * 0.165
        color = status_colors[lane.boundary_status]
        linestyle = "--" if lane.boundary_status == "outside default" else "-"
        ax.add_patch(
            FancyBboxPatch(
                (0.035, y - 0.048),
                0.15,
                0.096,
                boxstyle="round,pad=0.014,rounding_size=0.015",
                facecolor=color,
                edgecolor=color,
                linewidth=0.9,
                alpha=0.92,
            )
        )
        ax.text(
            0.11,
            y + 0.012,
            lane.label,
            ha="center",
            va="center",
            fontsize=7.4,
            color="#FFFFFF",
            weight="bold",
        )
        ax.text(0.11, y - 0.024, lane.boundary_status, ha="center", va="center", fontsize=5.8, color="#FFFFFF")
        ax.add_patch(
            FancyBboxPatch(
                (0.23, y - 0.06),
                0.39,
                0.12,
                boxstyle="round,pad=0.012,rounding_size=0.014",
                facecolor=PALETTE["paper"],
                edgecolor=color,
                linestyle=linestyle,
                linewidth=1.2,
            )
        )
        for component_index, component in enumerate(lane.components):
            x = 0.255 + component_index * 0.092
            ax.add_patch(
                FancyBboxPatch(
                    (x, y - 0.026),
                    0.079,
                    0.052,
                    boxstyle="round,pad=0.01,rounding_size=0.01",
                    facecolor=color,
                    edgecolor=color,
                    alpha=0.16,
                    linewidth=0.8,
                )
            )
            ax.text(
                x + 0.0355,
                y,
                textwrap.fill(component, width=10),
                ha="center",
                va="center",
                fontsize=5.8,
                color=PALETTE["ink"],
                linespacing=0.96,
            )
            if component_index < len(lane.components) - 1:
                _arrow(ax, (x + 0.082, y), (x + 0.091, y), color=PALETTE["gray"])
        ax.add_patch(
            FancyBboxPatch(
                (0.67, y - 0.06),
                0.29,
                0.12,
                boxstyle="round,pad=0.012,rounding_size=0.014",
                facecolor="#FFFFFF",
                edgecolor=PALETTE["line"],
                linewidth=0.9,
            )
        )
        ax.text(
            0.685,
            y,
            textwrap.fill(lane.governance_gate, width=42),
            ha="left",
            va="center",
            fontsize=6.4,
            color=PALETTE["ink"],
            linespacing=1.05,
        )
    ax.text(0.425, 0.055, "components", ha="center", fontsize=7.2, color=PALETTE["gray"])
    ax.text(0.815, 0.055, "governance gate / non-claim", ha="center", fontsize=7.2, color=PALETTE["gray"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("DigiPPPiP system architecture: kernel, branches, and evidence gates")
    return _save(
        fig,
        out_dir,
        "cpss_architecture.png",
        "fig:cpss_architecture",
        "System architecture showing the human-human kernel, optional branches, and governance gates.",
    )


def generate_dyadic_task_matrix(out_dir: Path) -> Path:
    """Render the dyadic study-condition matrix."""
    rows = ["peer-peer", "mentor-novice", "human-AI-assisted"]
    cols = ["co-located\nsync", "remote\nsync", "remote\nturns", "persistent\nasync"]
    values = np.array(
        [
            [0.95, 0.75, 0.62, 0.42],
            [0.78, 0.68, 0.70, 0.55],
            [0.60, 0.64, 0.66, 0.72],
        ]
    )
    fig, ax = plt.subplots(figsize=(9.4, 5.3))
    cmap = LinearSegmentedColormap.from_list(
        "digipppip_dyadic",
        [PALETTE["mist"], PALETTE["sky"], PALETTE["green"], PALETTE["orange"]],
    )
    image = ax.imshow(values, cmap=cmap, vmin=0.35, vmax=1)
    ax.set_xticks(range(len(cols)), cols)
    ax.set_yticks(range(len(rows)), rows)
    ax.tick_params(axis="both", labelsize=8.5)
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            score = values[row, col]
            if score >= 0.70:
                ax.add_patch(
                    plt.Rectangle(
                        (col - 0.5, row - 0.5),
                        1,
                        1,
                        fill=False,
                        hatch="///",
                        edgecolor="#FFFFFF",
                        linewidth=0.0,
                    )
                )
            ax.text(
                col,
                row - 0.08,
                f"{score:.2f}",
                ha="center",
                va="center",
                color="#FFFFFF" if score >= 0.60 else PALETTE["ink"],
                fontsize=10,
                weight="bold",
            )
            ax.text(
                col,
                row + 0.22,
                "high cue load" if score >= 0.70 else "study cell",
                ha="center",
                va="center",
                color="#FFFFFF" if score >= 0.60 else PALETTE["gray"],
                fontsize=6.5,
            )
    ax.set_xticks(np.arange(-0.5, len(cols), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color="#FFFFFF", linewidth=1.4)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_xlabel("temporal-spatial study condition")
    ax.set_ylabel("role structure")
    ax.set_title("Dyadic task matrix for staged DigiPPPiP studies")
    ax.text(
        0.0,
        -0.18,
        "Hatched cells mark high coordination demand; values are protocol-planning scores, not outcomes.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=GRAMMAR["caution"],
    )
    fig.colorbar(image, ax=ax, fraction=0.045, pad=0.035, label="mutual-responsiveness demand")
    return _save(
        fig,
        out_dir,
        "dyadic_task_matrix.png",
        "fig:dyadic_task_matrix",
        "Study-condition matrix across role structure and temporal-spatial mode.",
    )


def generate_taxonomy_matrix(out_dir: Path) -> Path:
    """Render the 3 x 3 temporal-spatial taxonomy matrix."""
    score = taxonomy_matrix("neural_synchrony")
    modalities = {(m.temporal, m.spatial): m.name for m in build_taxonomy()}
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    cmap = LinearSegmentedColormap.from_list(
        "digipppip_taxonomy",
        [PALETTE["mist"], PALETTE["sky"], PALETTE["green"], PALETTE["violet"]],
    )
    image = ax.imshow(score, cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(SpatialConfig)), [s.value.replace("_", "\n") for s in SpatialConfig])
    ax.set_yticks(range(len(TemporalMode)), [t.value for t in TemporalMode])
    for i, temporal in enumerate(TemporalMode):
        for j, spatial in enumerate(SpatialConfig):
            cell_score = score[i, j]
            if cell_score >= 0.70:
                ax.add_patch(
                    plt.Rectangle(
                        (j - 0.5, i - 0.5),
                        1,
                        1,
                        fill=False,
                        hatch="xx",
                        edgecolor="#FFFFFF",
                        linewidth=0.0,
                    )
                )
            background_hex = _rgba_to_hex(cmap(cell_score))
            ax.text(
                j,
                i - 0.10,
                "\n".join(taxonomy_cell_label_lines(modalities[(temporal, spatial)])),
                ha="center",
                va="center",
                color=PALETTE["ink"],
                fontsize=7.2,
                weight="bold",
                linespacing=1.05,
                bbox={
                    "boxstyle": "round,pad=0.22",
                    "facecolor": PALETTE["paper"],
                    "edgecolor": PALETTE["line"],
                    "linewidth": 0.5,
                    "alpha": 0.90,
                },
                zorder=4,
            )
            ax.text(
                j,
                i + 0.33,
                f"{cell_score:.2f}",
                ha="center",
                va="center",
                color=_contrast_text_color(background_hex),
                fontsize=7,
                weight="bold",
                zorder=4,
            )
    ax.set_xticks(np.arange(-0.5, len(SpatialConfig), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(TemporalMode), 1), minor=True)
    ax.grid(which="minor", color="#FFFFFF", linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_title("Temporal-spatial taxonomy of DigiPPPiP modalities")
    ax.set_xlabel("spatial configuration")
    ax.set_ylabel("temporal structure")
    fig.colorbar(image, ax=ax, fraction=0.045, pad=0.035, label="neural synchrony affordance")
    return _save(
        fig,
        out_dir,
        "taxonomy_matrix.png",
        "fig:taxonomy_matrix",
        "Three-by-three DigiPPPiP temporal-spatial taxonomy.",
    )


def generate_event_logging_schema(out_dir: Path) -> Path:
    """Render the event-log schema and a tiny session trace."""
    events = example_protocol_events()
    summary = summarize_event_log(events)
    stages = data_flow_stages()
    status_colors = {
        "observed": PALETTE["blue"],
        "derived": PALETTE["sky"],
        "computed": PALETTE["violet"],
        "rendered": PALETTE["green"],
        "governed": PALETTE["orange"],
        "published": PALETTE["purple"],
    }
    fig, ax = plt.subplots(figsize=(11.2, 5.4))
    ax.axis("off")
    ax.text(
        0.035,
        0.605,
        "raw human action stays distinct from derived metrics, computed diagnostics, governed ledgers, and render outputs",
        fontsize=7.4,
        color=PALETTE["gray"],
    )
    for index, stage in enumerate(stages):
        x = 0.035 + index * 0.137
        y = 0.68
        color = status_colors[stage.data_status]
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                0.112,
                0.18,
                boxstyle="round,pad=0.012,rounding_size=0.013",
                facecolor=PALETTE["paper"],
                edgecolor=color,
                linewidth=1.25,
            )
        )
        ax.text(x + 0.056, y + 0.137, stage.label, ha="center", va="center", fontsize=8.2, weight="bold")
        ax.text(
            x + 0.056,
            y + 0.098,
            stage.data_status,
            ha="center",
            va="center",
            fontsize=6.2,
            color="#FFFFFF",
            bbox={"boxstyle": "round,pad=0.18", "fc": color, "ec": color, "lw": 0},
        )
        ax.text(
            x + 0.056,
            y + 0.042,
            textwrap.fill(stage.artifact, width=14),
            ha="center",
            va="center",
            fontsize=5.8,
            color=PALETTE["ink"],
            linespacing=0.95,
        )
        if index < len(stages) - 1:
            _arrow(ax, (x + 0.115, y + 0.09), (x + 0.132, y + 0.09), color=PALETTE["gray"])
    fields = ["timestamp", "actor", "action", "channel", "archive state", "optional branch"]
    for field_index, field in enumerate(fields):
        y = 0.45 - field_index * 0.045
        ax.add_patch(
            FancyBboxPatch(
                (0.055, y - 0.014),
                0.17,
                0.032,
                boxstyle="round,pad=0.006,rounding_size=0.006",
                facecolor=PALETTE["mist"],
                edgecolor=PALETTE["line"],
                linewidth=0.6,
            )
        )
        ax.text(0.068, y, field, ha="left", va="center", fontsize=6.6, color=PALETTE["ink"])
    ax.text(0.055, 0.50, "minimum event row", fontsize=8.2, weight="bold", color=PALETTE["blue"])
    actors = {"partner_a": PALETTE["blue"], "partner_b": PALETTE["orange"]}
    ax.text(0.31, 0.50, "illustrative partner trace", fontsize=8.2, weight="bold", color=PALETTE["blue"])
    ax.plot([0.31, 0.89], [0.31, 0.31], color=PALETTE["line"], linewidth=1.0)
    max_timestamp = max(event.timestamp_s for event in events)
    for event in events:
        x = 0.31 + (event.timestamp_s / max_timestamp) * 0.58
        color = actors.get(event.actor, PALETTE["gray"])
        ax.scatter(x, 0.31, s=86, color=color, zorder=3)
        ax.text(
            x,
            0.37,
            textwrap.fill(event.action.replace("_", " "), width=10),
            ha="center",
            va="bottom",
            fontsize=5.8,
            color=PALETTE["ink"],
        )
    ax.text(
        0.31,
        0.22,
        f"{summary.temporal_mode}; mean interval {summary.mean_interval_s:.1f}s; turn balance {summary.turn_balance:.2f}",
        ha="left",
        fontsize=7.0,
        color=PALETTE["gray"],
    )
    ax.text(
        0.055,
        0.105,
        "Human-authored marks stay distinct from computed diagnostics and publication artifacts; optional AI logs remain separable.",
        ha="left",
        fontsize=7.3,
        color=GRAMMAR["caution"],
        bbox={"boxstyle": "round,pad=0.25", "fc": "#FFF7ED", "ec": PALETTE["orange"], "lw": 0.8},
    )
    ax.set_title("DigiPPPiP event data flow from partner action to governed publication artifact")
    return _save(
        fig,
        out_dir,
        "event_logging_schema.png",
        "fig:event_logging_schema",
        "Event schema, data-flow path, and example session trace for reproducible protocol logging.",
    )


def generate_active_inference_mapping(out_dir: Path) -> Path:
    """Render the model-variable mapping behind the active-inference equations."""
    groups = (
        (
            0.17,
            "latent states",
            ("partner intention", "narrative state", "shared affect"),
            PALETTE["purple"],
        ),
        (
            0.50,
            "observations",
            ("stroke event", "pause or latency", "utterance or cue"),
            PALETTE["blue"],
        ),
        (
            0.83,
            "policies",
            ("draw", "wait", "respond", "revise"),
            PALETTE["green"],
        ),
    )
    fig, ax = plt.subplots(figsize=(9.2, 4.9))
    ax.add_patch(
        FancyBboxPatch(
            (0.05, 0.11),
            0.90,
            0.76,
            boxstyle="round,pad=0.018,rounding_size=0.025",
            facecolor="#FFFFFF",
            edgecolor=PALETTE["line"],
            linewidth=0.9,
            zorder=0,
        )
    )
    for x, group, items, color in groups:
        ax.add_patch(
            FancyBboxPatch(
                (x - 0.125, 0.36),
                0.25,
                0.40,
                boxstyle="round,pad=0.018,rounding_size=0.02",
                facecolor=color,
                alpha=0.16,
                edgecolor=color,
                linewidth=1.2,
                zorder=1,
            )
        )
        ax.text(x, 0.69, group, ha="center", va="center", fontsize=10, weight="bold", color=PALETTE["ink"])
        for idx, item in enumerate(items):
            ax.text(
                x,
                0.59 - idx * 0.068,
                item,
                ha="center",
                va="center",
                fontsize=8.2,
                color=PALETTE["ink"],
                zorder=2,
            )
    arrow_y = 0.32
    _arrow(ax, (0.29, arrow_y), (0.39, arrow_y), color=PALETTE["gray"])
    _arrow(ax, (0.61, arrow_y), (0.71, arrow_y), color=PALETTE["gray"])
    ax.annotate(
        "",
        xy=(0.18, 0.77),
        xytext=(0.82, 0.77),
        arrowprops={
            "arrowstyle": "->",
            "color": PALETTE["gray"],
            "lw": 1.2,
            "connectionstyle": "arc3,rad=0.23",
        },
    )
    ax.text(0.34, 0.25, "sample", ha="center", fontsize=7.2, color=PALETTE["gray"])
    ax.text(0.66, 0.25, "select", ha="center", fontsize=7.2, color=PALETTE["gray"])
    ax.text(
        0.50,
        0.16,
        "posterior from one turn becomes a partner-conditioned prior for the next visible mark",
        ha="center",
        fontsize=8.2,
        color=GRAMMAR["caution"],
        bbox={"boxstyle": "round,pad=0.28", "fc": "#FFF7ED", "ec": PALETTE["orange"], "lw": 0.8},
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Active-inference variables mapped to observable drawing events")
    return _save(
        fig,
        out_dir,
        "active_inference_mapping.png",
        "fig:active_inference_mapping",
        "Mapping from DigiPPPiP events to active-inference model components.",
    )


def generate_active_inference_loop(out_dir: Path) -> Path:
    """Render coupled and decoupled free-energy trajectories."""
    cfg = _figure_experiment(out_dir)
    steps = _int_param(cfg, "dyadic_steps", 60)
    seed = _int_param(cfg, "random_seed", 0)
    prior_prec = _float_param(cfg, "prior_precision", 1.0)
    lik_prec = _float_param(cfg, "likelihood_precision", 2.0)
    coupled = simulate_dyadic_session(
        steps=steps,
        coupled=True,
        seed=seed,
        prior_prec=prior_prec,
        lik_prec=lik_prec,
    )["free_energy"]
    decoupled = simulate_dyadic_session(
        steps=steps,
        coupled=False,
        seed=seed,
        prior_prec=prior_prec,
        lik_prec=lik_prec,
    )["free_energy"]
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ax.plot(coupled, color=PALETTE["blue"], label="coupled dyad")
    ax.plot(decoupled, color=PALETTE["orange"], linestyle="--", label="decoupled baseline")
    ax.scatter([len(coupled) - 1], [coupled[-1]], color=PALETTE["blue"], s=34, zorder=3)
    ax.scatter([len(decoupled) - 1], [decoupled[-1]], color=PALETTE["orange"], s=34, zorder=3)
    ax.text(
        0.58,
        0.13,
        f"terminal gap: {decoupled[-1] - coupled[-1]:.2f}",
        transform=ax.transAxes,
        fontsize=8,
        color=PALETTE["ink"],
        bbox={"boxstyle": "round,pad=0.25", "fc": "#FFFFFF", "ec": PALETTE["line"], "lw": 0.8},
    )
    ax.set_xlabel("modeled mark step")
    ax.set_ylabel("joint variational free energy")
    ax.set_title("Toy reciprocal-updating free-energy trajectories")
    ax.legend(loc="center right", frameon=True)
    return _save(
        fig,
        out_dir,
        "active_inference_loop.png",
        "fig:active_inference_loop",
        "Conceptual coupled active-inference trajectory.",
    )


def generate_network_analysis_pipeline(out_dir: Path) -> Path:
    """Render the hyperscanning/network-analysis pipeline."""
    steps = ["raw signals", "cleaning", "windowing", "IBS", "graph", "curvature"]
    fig, ax = plt.subplots(figsize=(9, 2.8))
    for idx, step in enumerate(steps):
        x = 0.08 + idx * 0.16
        rect = plt.Rectangle(
            (x, 0.38),
            0.12,
            0.24,
            facecolor=PALETTE["green"] if idx % 2 else PALETTE["blue"],
            alpha=0.22,
            edgecolor=PALETTE["gray"],
        )
        ax.add_patch(rect)
        ax.text(x + 0.06, 0.50, step, ha="center", va="center", fontsize=8)
        if idx < len(steps) - 1:
            ax.annotate(
                "",
                xy=(x + 0.155, 0.50),
                xytext=(x + 0.12, 0.50),
                arrowprops={"arrowstyle": "->", "color": PALETTE["gray"]},
            )
    ax.text(
        0.5,
        0.18,
        "Permutation tests and motion/physiology checks are required before interpretation.",
        ha="center",
        fontsize=8,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Hyperscanning and interaction-network analysis pipeline")
    return _save(
        fig,
        out_dir,
        "network_analysis_pipeline.png",
        "fig:network_analysis_pipeline",
        "Reproducible pipeline from raw dyadic signals to network diagnostics.",
    )


def generate_ibs_phase_plot(out_dir: Path) -> Path:
    """Render the four-phase inter-brain-synchrony profile."""
    cfg = _figure_experiment(out_dir)
    session = simulate_ibs_phases(
        steps=_int_param(cfg, "session_steps", 120),
        seed=_int_param(cfg, "random_seed", 0),
    )
    ibs = session["ibs"]
    phase = session["phase"]
    colors = {
        "initiation": PALETTE["gray"],
        "elaboration": PALETTE["blue"],
        "convergence": PALETTE["green"],
        "completion": PALETTE["purple"],
    }
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(ibs, color=PALETTE["blue"], linewidth=2)
    for name in PHASES:
        idx = np.where(phase == name)[0]
        ax.axvspan(idx[0], idx[-1], color=colors[name], alpha=0.12)
        ax.text(idx.mean(), ibs.max() + 0.02, name, ha="center", fontsize=8)
    ax.set_ylim(0, 1)
    ax.set_xlabel("modeled session step")
    ax.set_ylabel("IBS proxy")
    ax.set_title("Conceptual IBS phase profile across a DigiPPPiP session")
    return _save(
        fig,
        out_dir,
        "ibs_phases.png",
        "fig:ibs_phases",
        "Four-phase conceptual inter-brain-synchrony profile.",
    )


def generate_accessibility_audit_radar(out_dir: Path) -> Path:
    """Render an accessibility domain radar from the audit primitive."""
    capabilities = {
        "stylus",
        "touch",
        "keyboard",
        "switch",
        "voice",
        "high_contrast",
        "audio_description",
        "plain_language",
        "low_distraction_mode",
        "save_consent",
        "delete_control",
        "replay_control",
        "assisted_drawing",
        "haptic_feedback",
        "role_switching",
    }
    scores = domain_scores(capabilities)
    labels = list(scores)
    values = np.array(list(scores.values()), dtype=float)
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)
    closed_angles = np.append(angles, angles[0])
    closed_values = np.append(values, values[0])
    ax.plot(closed_angles, closed_values, color=PALETTE["purple"], linewidth=2)
    ax.fill(closed_angles, closed_values, color=PALETTE["purple"], alpha=0.18)
    ax.set_xticks(angles, labels)
    ax.set_ylim(0, 1)
    ax.set_title("Accessibility audit by design domain", y=1.08)
    return _save(
        fig,
        out_dir,
        "accessibility_audit_radar.png",
        "fig:accessibility_audit_radar",
        "Accessibility audit radar generated from explicit implementation capabilities.",
    )


def generate_geometric_hyperscanning_plot(out_dir: Path) -> Path:
    """Render curvature entropy and detected phase transitions."""
    cfg = _figure_experiment(out_dir)
    steps = _int_param(cfg, "session_steps", 120)
    seed = _int_param(cfg, "random_seed", 0)
    nodes = _int_param(cfg, "network_nodes", 8)
    entropies = np.array(
        [
            curvature_entropy(forman_ricci_curvature(inter_brain_network(t, nodes, seed)))
            for t in range(steps)
        ]
    )
    transitions = detect_phase_transitions(entropies, _float_param(cfg, "curvature_transition_threshold", 0.15))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(entropies, color=PALETTE["red"], linewidth=2, label="curvature entropy")
    ax.scatter(transitions, entropies[transitions], color=PALETTE["blue"], s=20, label="transitions")
    ax.set_xlabel("modeled session step")
    ax.set_ylabel("entropy (bits)")
    ax.set_title("Forman-Ricci curvature entropy as a phase-transition proxy")
    ax.legend()
    return _save(
        fig,
        out_dir,
        "geometric_hyperscanning.png",
        "fig:geometric_hyperscanning",
        "Conceptual geometric-hyperscanning curvature entropy.",
    )


def generate_source_quality_map(out_dir: Path) -> Path:
    """Render conservative source-quality tiers used by the manuscript."""
    source_types = list(TYPE_STRENGTH)
    scores = {
        "peer_reviewed_article": 4,
        "book": 3,
        "conference_or_report": 2,
        "preprint": 1,
        "misc": 0.5,
    }
    values = [scores[source_type] for source_type in source_types]
    y = np.arange(len(source_types))
    labels = [source_type.replace("_", " ") for source_type in source_types]
    colors = [PALETTE["blue"], PALETTE["green"], PALETTE["orange"], PALETTE["purple"], PALETTE["gray"]]
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    ax.barh(y, values, color=colors, alpha=0.86, edgecolor="#FFFFFF", linewidth=1.2)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 4.5)
    ax.set_xticks(range(5), ["unknown", "provisional", "limited", "theory", "scoped"])
    ax.set_xlabel("maximum claim strength")
    ax.set_title("Source-quality map for manuscript claim discipline")
    for idx, source_type in enumerate(source_types):
        strength, warning = TYPE_STRENGTH[source_type]
        ax.text(
            0.08,
            idx,
            strength,
            ha="left",
            va="center",
            fontsize=8,
            weight="bold",
            color=_contrast_text_color(colors[idx]),
        )
        ax.text(
            values[idx] + 0.08,
            idx,
            textwrap.fill(warning, width=48),
            va="center",
            fontsize=7.1,
            color=PALETTE["gray"],
        )
    ax.text(
        0.02,
        -0.18,
        "Bars constrain claim language; direct DigiPPPiP evidence is still required for outcome claims.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=GRAMMAR["caution"],
    )
    return _save(
        fig,
        out_dir,
        "source_quality_map.png",
        "fig:source_quality_map",
        "Conservative source-quality tiers used to avoid overclaiming.",
    )


def generate_claim_boundary_matrix(out_dir: Path) -> Path:
    """Render claim domains against maximum evidence-backed strength."""
    boundaries = claim_boundaries()
    levels = list(CLAIM_STRENGTH_LEVELS)
    matrix = np.zeros((len(boundaries), len(levels)), dtype=float)
    for row, boundary in enumerate(boundaries):
        matrix[row, : boundary.score + 1] = 1.0

    fig, (ax, evidence_ax) = plt.subplots(
        1,
        2,
        figsize=(12.4, 6.65),
        gridspec_kw={"width_ratios": [1.05, 1.55]},
    )
    fig.suptitle("Claim-strength and evidence-boundary matrix", y=0.985, fontsize=13.5, color=PALETTE["ink"])
    cmap = LinearSegmentedColormap.from_list("claim_boundary", ["#F5F7FA", PALETTE["green"]])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    level_labels = ["concept", "descr.", "assoc.", "compar.", "causal /\nclinical"]
    ax.set_xticks(range(len(levels)), level_labels)
    ax.set_yticks(range(len(boundaries)), [boundary.label for boundary in boundaries])
    ax.set_xlabel("claim strength")
    ax.set_title("current maximum", color=PALETTE["blue"], pad=12)
    for row, boundary in enumerate(boundaries):
        for col in range(len(levels)):
            if col <= boundary.score:
                ax.text(col, row, "ok", ha="center", va="center", fontsize=7, weight="bold", color=PALETTE["ink"])
        ax.plot(
            [boundary.score - 0.42, boundary.score + 0.42],
            [row + 0.34, row + 0.34],
            color=PALETTE["blue"],
            linewidth=2.2,
            solid_capstyle="round",
        )
    ax.set_xticks(np.arange(-0.5, len(levels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(boundaries), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.25)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(axis="x", labelsize=7)
    ax.tick_params(axis="y", labelsize=8)

    evidence_ax.axis("off")
    evidence_ax.set_title("evidence gate before stronger claims", fontsize=10.5, color=PALETTE["blue"], pad=12)
    evidence_ax.set_xlim(0, 1)
    evidence_ax.set_ylim(0, 1)
    evidence_ax.add_patch(
        plt.Rectangle((0.0, 0.0), 0.98, 0.94, facecolor="#FFFFFF", alpha=0.88, edgecolor=PALETTE["line"])
    )
    rows_per_column = (len(boundaries) + 1) // 2
    row_height = 0.82 / rows_per_column
    column_width = 0.475
    for row, boundary in enumerate(boundaries):
        column = row // rows_per_column
        slot = row % rows_per_column
        x0 = 0.018 + column * 0.49
        y = 0.89 - slot * row_height
        evidence_ax.add_patch(
            plt.Rectangle(
                (x0, y - row_height * 0.74),
                column_width,
                row_height * 0.84,
                facecolor=PALETTE["mist"] if row % 2 == 0 else "#FFFFFF",
                edgecolor=PALETTE["line"],
                linewidth=0.4,
                alpha=0.9,
            )
        )
        evidence_ax.text(
            x0 + 0.012,
            y,
            textwrap.fill(boundary.label, width=19),
            fontsize=7.0,
            weight="bold",
            va="top",
            color=PALETTE["ink"],
        )
        evidence_ax.text(
            x0 + 0.22,
            y,
            textwrap.fill(boundary.required_evidence, width=29),
            fontsize=6.4,
            va="top",
            color=PALETTE["ink"],
        )
    evidence_ax.text(
        0.03,
        0.015,
        "Green cells show currently defensible claim strength; blank cells require new evidence.",
        fontsize=7.5,
        color=GRAMMAR["caution"],
    )
    return _save(
        fig,
        out_dir,
        "claim_boundary_matrix.png",
        "fig:claim_boundary_matrix",
        "Claim-strength matrix mapping DigiPPPiP risk domains to evidence requirements.",
    )


def generate_claim_ledger_matrix(out_dir: Path) -> Path:
    """Render a manuscript claim ledger with evidence-strength ceilings."""
    records = claim_records()
    strength_index = {name: idx for idx, name in enumerate(CLAIM_STRENGTH_LEVELS)}
    scores = np.array([strength_index[record.max_strength] for record in records], dtype=float)
    labels = [claim_ledger_display_label(record.claim_id) for record in records]
    y = np.arange(len(records))

    evidence_counts = np.array([len(record.evidence_keys) for record in records], dtype=float)
    fig, ax = plt.subplots(figsize=(11.8, 7.8))
    colors = [PALETTE["sky"], PALETTE["green"], PALETTE["orange"], PALETTE["purple"], PALETTE["red"]]
    ax.barh(y, scores, color=[colors[int(score)] for score in scores], alpha=0.82, edgecolor="#FFFFFF")
    ax.scatter(
        np.full_like(evidence_counts, len(CLAIM_STRENGTH_LEVELS) - 0.42),
        y,
        s=42 + evidence_counts * 9,
        color=PALETTE["blue"],
        alpha=0.78,
        label="evidence-key count",
    )
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_ylim(len(records) - 0.5, -1.0)
    ax.set_xlim(-0.2, len(CLAIM_STRENGTH_LEVELS) + 0.22)
    ax.set_xticks(range(len(CLAIM_STRENGTH_LEVELS)), [level.replace("_", "\n") for level in CLAIM_STRENGTH_LEVELS])
    ax.set_xlabel("maximum defensible claim strength")
    ax.set_title("Claim ledger: source-backed ceilings and next evidence gates")
    ax.tick_params(axis="y", labelsize=7.4)
    ax.tick_params(axis="x", labelsize=8.0)
    ax.text(
        len(CLAIM_STRENGTH_LEVELS) - 0.42,
        -0.76,
        "source-key count",
        ha="center",
        va="center",
        fontsize=7,
        color=PALETTE["gray"],
    )
    for idx, record in enumerate(records):
        ax.text(
            scores[idx] + 0.08,
            idx,
            textwrap.shorten(record.next_evidence, width=58, placeholder="..."),
            va="center",
            fontsize=7,
            color=PALETTE["gray"],
        )
        ax.text(
            len(CLAIM_STRENGTH_LEVELS) - 0.42,
            idx,
            str(int(evidence_counts[idx])),
            ha="center",
            va="center",
            fontsize=6.8,
            weight="bold",
            color="#FFFFFF",
        )
    ax.text(
        0.50,
        -0.15,
        "Each row is a manuscript claim family; bars show current ceiling, text names the evidence needed to upgrade.",
        ha="center",
        va="top",
        fontsize=8,
        color=GRAMMAR["caution"],
        transform=ax.transAxes,
    )
    return _save(
        fig,
        out_dir,
        "claim_ledger_matrix.png",
        "fig:claim_ledger_matrix",
        "Claim-ledger matrix linking manuscript claim families to evidence ceilings and upgrade gates.",
    )


def generate_source_verification_readiness(out_dir: Path) -> Path:
    """Render the executable source-verification readiness profile."""
    root = _project_root_from_out_dir(out_dir)
    bib_text = (root / "manuscript" / "references.bib").read_text()
    required = source_verification_required_keys(root / "manuscript")
    records = build_source_verification_records(bib_text)
    summary = source_verification_summary(required, records, bib_text)

    count_labels = [
        "governed citekeys",
        "covered governed",
        "priority refresh",
        "official anchors",
        "reporting anchors",
        "missing records",
    ]
    count_values = np.array(
        [
            summary.required_records,
            summary.covered_required_records,
            summary.priority_records,
            summary.official_records,
            summary.reporting_records,
            summary.missing_records,
        ],
        dtype=float,
    )
    colors = [
        PALETTE["blue"],
        PALETTE["green"],
        PALETTE["orange"],
        PALETTE["purple"],
        PALETTE["sky"],
        PALETTE["red"] if summary.missing_records else PALETTE["green"],
    ]

    fig, (ax, tier_ax) = plt.subplots(
        1,
        2,
        figsize=(12.2, 6.0),
        gridspec_kw={"width_ratios": [1.25, 1.0]},
    )
    fig.suptitle("Source-verification readiness profile", y=0.985, fontsize=13.5, color=PALETTE["ink"])

    y = np.arange(len(count_labels))
    ax.barh(y, count_values, color=colors, alpha=0.88, edgecolor="#FFFFFF", linewidth=1.2)
    ax.set_yticks(y, count_labels)
    ax.invert_yaxis()
    ax.set_xlabel("citekey count")
    ax.set_xlim(0, max(count_values.max() * 1.18, 1.0))
    for idx, value in enumerate(count_values):
        ax.text(value + 0.35, idx, f"{int(value)}", va="center", fontsize=8.5, weight="bold", color=PALETTE["ink"])
    ax.set_title("coverage and refresh pressure", color=PALETTE["blue"], pad=12)
    ax.grid(axis="x", color=PALETTE["line"], alpha=0.45)
    ax.grid(axis="y", visible=False)

    tier_ax.axis("off")
    tier_ax.set_title("source tiers and recheck triggers", fontsize=10.5, color=PALETTE["blue"], pad=12)
    tier_ax.add_patch(plt.Rectangle((0.0, 0.0), 0.98, 0.94, facecolor="#FFFFFF", alpha=0.78, edgecolor=PALETTE["line"]))
    tier_ax.text(
        0.04,
        0.90,
        f"total verified records: {summary.total_records}",
        fontsize=8.2,
        weight="bold",
        color=PALETTE["ink"],
    )
    tier_items = list(summary.tier_counts.items())
    trigger_items = list(summary.recheck_trigger_counts.items())
    tier_ax.text(0.04, 0.81, "source tiers", fontsize=8.3, weight="bold", color=PALETTE["blue"])
    tier_ax.text(0.55, 0.81, "recheck triggers", fontsize=8.3, weight="bold", color=PALETTE["red"])
    for idx, (tier, count) in enumerate(tier_items):
        y_pos = 0.73 - idx * 0.098
        tier_ax.add_patch(
            plt.Rectangle(
                (0.04, y_pos - 0.032),
                0.40,
                0.062,
                facecolor=PALETTE["sky"],
                alpha=0.30,
                edgecolor=PALETTE["line"],
            )
        )
        tier_ax.text(0.07, y_pos, str(count), va="center", fontsize=8.5, weight="bold", color=PALETTE["ink"])
        tier_ax.text(0.18, y_pos, tier.replace("_", " "), va="center", fontsize=7.1, color=PALETTE["ink"])
    for idx, (trigger, count) in enumerate(trigger_items):
        y_pos = 0.73 - idx * 0.14
        tier_ax.add_patch(
            plt.Rectangle(
                (0.55, y_pos - 0.045),
                0.39,
                0.085,
                facecolor=PALETTE["orange"],
                alpha=0.24,
                edgecolor=PALETTE["line"],
            )
        )
        tier_ax.text(0.58, y_pos, str(count), va="center", fontsize=8.2, weight="bold", color=PALETTE["ink"])
        tier_ax.text(
            0.70,
            y_pos,
            textwrap.fill(trigger.replace("_", " "), width=24),
            va="center",
            fontsize=6.7,
            color=PALETTE["ink"],
        )
    return _save(
        fig,
        out_dir,
        "source_verification_readiness.png",
        "fig:source_verification_readiness",
        "Source-verification readiness dashboard for governed citekeys, priority refreshes, tiers, and triggers.",
    )


def generate_study_readiness_matrix(out_dir: Path) -> Path:
    """Render the dyadic study-readiness governance matrix."""
    rows = study_readiness_matrix_rows()
    labels = [row.label for row in rows]
    columns = ["right", "protocol", "sources", "dyadic scope", "conflict rule", "AI branch"]
    matrix = np.array(
        [
            [
                float(row.rights_defined),
                float(row.protocol_defined),
                float(row.source_anchor_count > 0),
                float(row.partner_scope in {"both_partners", "shared_archive", "either_partner"}),
                float(row.conflict_rule != "not_applicable"),
                float(row.ai_scope == "optional_separate_branch"),
            ]
            for row in rows
        ],
        dtype=float,
    )

    fig, (ax, detail_ax) = plt.subplots(
        1,
        2,
        figsize=(13.0, 7.1),
        gridspec_kw={"width_ratios": [1.0, 1.22]},
    )
    fig.suptitle("Study-readiness governance matrix", y=0.985, fontsize=13.5, color=PALETTE["ink"])
    cmap = LinearSegmentedColormap.from_list("study_readiness", ["#F7FAFC", PALETTE["green"]])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(columns)), columns, rotation=35, ha="right")
    ax.set_yticks(range(len(rows)), labels)
    ax.tick_params(axis="both", labelsize=7.5)
    ax.set_title("participant-facing controls", color=PALETTE["blue"], pad=12)
    for row_idx, row in enumerate(rows):
        for col_idx in range(len(columns)):
            if col_idx == 2:
                text = str(row.source_anchor_count)
            else:
                text = "yes" if matrix[row_idx, col_idx] else ""
            color = "white" if matrix[row_idx, col_idx] else "#111827"
            weight = "bold" if text else "normal"
            ax.text(col_idx, row_idx, text, ha="center", va="center", fontsize=6.8, color=color, weight=weight)
        if row.applicability == "optional_ai_branch":
            ax.add_patch(
                plt.Rectangle(
                    (-0.5, row_idx - 0.5),
                    len(columns),
                    1,
                    fill=False,
                    hatch="///",
                    edgecolor=PALETTE["purple"],
                    linewidth=1.4,
                )
            )
        elif row.partner_scope == "shared_archive":
            ax.add_patch(
                plt.Rectangle(
                    (-0.5, row_idx - 0.5),
                    len(columns),
                    1,
                    fill=False,
                    edgecolor=PALETTE["blue"],
                    linewidth=0.8,
                )
            )
    ax.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.25)
    ax.tick_params(which="minor", bottom=False, left=False)

    detail_ax.axis("off")
    detail_ax.set_title("edge-case routing", fontsize=10.5, color=PALETTE["blue"], pad=12)
    detail_ax.add_patch(
        plt.Rectangle((0.0, 0.0), 0.98, 0.94, facecolor="#FFFFFF", alpha=0.88, edgecolor=PALETTE["line"])
    )
    selected = [
        row
        for row in rows
        if row.key
        in {
            "dyadic_consent",
            "deletion",
            "export",
            "replay",
            "one_partner_disagrees",
            "ai_branch_governance",
        }
    ]
    for idx, row in enumerate(selected):
        y_pos = 0.86 - idx * 0.14
        color = PALETTE["purple"] if row.ai_scope == "optional_separate_branch" else PALETTE["green"]
        detail_ax.add_patch(
            plt.Rectangle((0.03, y_pos - 0.05), 0.24, 0.09, facecolor=color, alpha=0.30, edgecolor=PALETTE["line"])
        )
        if row.ai_scope == "optional_separate_branch":
            detail_ax.add_patch(
                plt.Rectangle(
                    (0.03, y_pos - 0.05),
                    0.24,
                    0.09,
                    fill=False,
                    hatch="///",
                    edgecolor=PALETTE["purple"],
                    linewidth=0.9,
                )
            )
        detail_ax.text(
            0.15,
            y_pos,
            row.label,
            ha="center",
            va="center",
            fontsize=7.1,
            weight="bold",
            color=PALETTE["ink"],
        )
        detail_ax.text(
            0.31,
            y_pos,
            textwrap.fill(
                f"scope={row.partner_scope.replace('_', ' ')}; "
                f"conflict={row.conflict_rule.replace('_', ' ')}; "
                f"AI={row.ai_scope.replace('_', ' ')}; sources={row.source_anchor_count}",
                width=58,
            ),
            va="center",
            fontsize=7,
            color=PALETTE["ink"],
        )
    detail_ax.text(
        0.04,
        0.06,
        (
            "The matrix preserves the human-human default while isolating optional AI support as a separately "
            "governed branch."
        ),
        fontsize=7.5,
        color=GRAMMAR["caution"],
    )
    detail_ax.text(
        0.04,
        0.015,
        "Blue outlines mark shared-archive controls; purple hatching marks optional AI governance.",
        fontsize=6.7,
        color=PALETTE["gray"],
    )
    return _save(
        fig,
        out_dir,
        "study_readiness_matrix.png",
        "fig:study_readiness_matrix",
        "Study-readiness matrix for dyadic consent, archive controls, disagreement handling, and optional AI.",
    )


def generate_validation_ladder(out_dir: Path) -> Path:
    """Render the staged empirical path before stronger claims are made."""
    stages = validation_ladder()
    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    _setup_canvas(ax, "Staged empirical validation ladder")
    ys = np.linspace(0.82, 0.18, len(stages))
    colors = [PALETTE["sky"], PALETTE["green"], PALETTE["purple"], PALETTE["orange"], PALETTE["red"]]
    for idx, (stage, y) in enumerate(zip(stages, ys)):
        _box(
            ax,
            0.38,
            y,
            f"{stage.stage}\n{stage.claim_unlocked}",
            color=colors[idx],
            width=0.48,
            height=0.105,
            fontsize=7,
            alpha=0.22,
        )
        _box(
            ax,
            0.78,
            y,
            stage.required_controls,
            color=GRAMMAR["caution"] if idx >= 3 else GRAMMAR["context"],
            width=0.30,
            height=0.105,
            fontsize=6,
            alpha=0.16,
        )
        if idx < len(stages) - 1:
            _arrow(ax, (0.38, y - 0.055), (0.38, ys[idx + 1] + 0.055), color=PALETTE["gray"])
    ax.text(0.38, 0.94, "claim unlocked by evidence", ha="center", fontsize=8, weight="bold")
    ax.text(0.78, 0.94, "minimum controls", ha="center", fontsize=8, weight="bold")
    _caveat(ax, "Physiology sits last: no neural measure upgrades a weak relational or access design.")
    return _save(
        fig,
        out_dir,
        "validation_ladder.png",
        "fig:validation_ladder",
        "Staged empirical validation ladder from feasibility to optional physiology.",
    )


def generate_narrative_information_plot(out_dir: Path) -> Path:
    """Render narrative entropy, surprisal, and convergence diagnostics."""
    seq = [0, 1, 0, 2, 3, 1, 4, 2, 5, 5, 4, 2, 2, 1, 1, 0, 0, 0, 0, 0] * 3
    s = surprisal(seq)
    pivots = pivotal_moments(seq, z=1.0)
    conv = convergence_index(seq, window=10)
    fig, axes = plt.subplots(2, 1, figsize=(8.4, 5.3), sharex=False)
    x_s = np.arange(len(s))
    axes[0].plot(x_s, s, color=PALETTE["blue"], label="surprisal")
    axes[0].scatter(pivots, s[pivots], color=PALETTE["red"], s=32, label="pivotal moments", zorder=3)
    for pivot in pivots[:1]:
        axes[0].annotate(
            "pivot",
            xy=(pivot, s[pivot]),
            xytext=(pivot + 1.2, s[pivot] + 0.25),
            fontsize=6.8,
            color=PALETTE["red"],
            arrowprops={"arrowstyle": "->", "color": PALETTE["red"], "lw": 0.8},
        )
    axes[0].set_ylabel("bits")
    axes[0].set_title(f"Synthetic stroke sequence: entropy {stroke_entropy(seq):.2f} bits")
    axes[0].legend(loc="upper right", frameon=True)
    axes[1].plot(conv, marker="o", color=PALETTE["green"], label="motif convergence")
    axes[1].fill_between(np.arange(len(conv)), conv, color=PALETTE["green"], alpha=0.12)
    axes[1].set_xlabel("window")
    axes[1].set_ylabel("index")
    axes[1].set_ylim(0, 1.05)
    axes[1].legend(loc="lower right", frameon=True)
    return _save(
        fig,
        out_dir,
        "narrative_information.png",
        "fig:narrative_information",
        "Narrative-information diagnostics for a conceptual stroke sequence.",
    )


def generate_multilevel_outcome_model(out_dir: Path) -> Path:
    """Render the planned multilevel outcome model."""
    spec = multilevel_model_spec()
    domains = outcome_domains()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.scatter([0.2], [0.5], s=1500, color=PALETTE["sky"], alpha=0.28)
    ax.text(0.2, 0.5, "fixed effects\n" + "\n".join(spec.fixed_effects), ha="center", va="center", fontsize=8)
    ax.scatter([0.5], [0.5], s=1600, color=PALETTE["green"], alpha=0.25)
    ax.text(0.5, 0.5, "dyad-level\nmixed model", ha="center", va="center", weight="bold")
    ax.scatter([0.8], [0.5], s=1500, color=PALETTE["purple"], alpha=0.25)
    ax.text(0.8, 0.5, "outcomes\n" + "\n".join(domains[:4]), ha="center", va="center", fontsize=8)
    for start, end in [(0.2, 0.5), (0.5, 0.8)]:
        ax.annotate(
            "",
            xy=(end - 0.10, 0.5),
            xytext=(start + 0.10, 0.5),
            arrowprops={"arrowstyle": "->", "color": PALETTE["gray"], "lw": 1.4},
        )
    ax.text(0.5, 0.12, f"{len(OUTCOME_MEASURES)} measures; formula: {spec.formula}", ha="center", fontsize=7)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Multilevel outcome model for DigiPPPiP studies")
    return _save(
        fig,
        out_dir,
        "multilevel_outcome_model.png",
        "fig:multilevel_outcome_model",
        "Mixed-model outcome plan linking study conditions to dyadic outcomes.",
    )


def generate_epistemic_arc_plot(out_dir: Path) -> Path:
    """Render the active-inference aesthetic epistemic arc."""
    cfg = _figure_experiment(out_dir)
    steps = _int_param(cfg, "session_steps", 120)
    arc = epistemic_arc(
        steps,
        _float_param(cfg, "epistemic_curiosity", 1.0),
        _float_param(cfg, "epistemic_precision", 0.6),
    )
    balances = np.array([order_change_balance(x, 1 - x) for x in np.linspace(0, 1, steps)])
    fig, ax = plt.subplots(figsize=(8.2, 4.3))
    normalized_arc = arc / arc.max()
    peak = int(np.argmax(arc))
    ax.plot(normalized_arc, color=PALETTE["blue"], label="expected information gain")
    ax.plot(balances, color=PALETTE["orange"], label="order-change balance")
    ax.axvline(peak, color=PALETTE["green"], linestyle="--", label="annotated peak")
    ax.scatter([peak], [normalized_arc[peak]], s=44, color=PALETTE["green"], zorder=3)
    ax.annotate(
        "co-discovery\nhypothesis",
        xy=(peak, normalized_arc[peak]),
        xytext=(peak + steps * 0.10, 0.78),
        fontsize=8,
        color=PALETTE["ink"],
        arrowprops={"arrowstyle": "->", "color": PALETTE["gray"], "lw": 0.9},
        bbox={"boxstyle": "round,pad=0.25", "fc": "#FFFFFF", "ec": PALETTE["line"], "lw": 0.8},
    )
    ax.set_xlabel("modeled mark step")
    ax.set_ylabel("normalized value")
    ax.set_ylim(-0.02, 1.08)
    ax.set_title("Expected-information-gain arc for aesthetic co-discovery")
    ax.legend(loc="upper right", frameon=True)
    return _save(
        fig,
        out_dir,
        "epistemic_arc.png",
        "fig:epistemic_arc",
        "Conceptual active-inference epistemic arc for aesthetic experience.",
    )


def generate_neuroergonomics_flow_plot(out_dir: Path) -> Path:
    """Render flow channel, technoference cost, and enclosure gain."""
    grid = np.linspace(0, 1, 60)
    challenge, skill = np.meshgrid(grid, grid)
    flow = 1 - np.abs(challenge - skill)
    interruptions = np.arange(0, 9)
    costs = [technoference_cost(int(i)) for i in interruptions]
    suppress = np.linspace(0, 1, 9)
    gains = [intentional_enclosure_gain(float(s)) for s in suppress]
    allocation = attention_allocation()

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.5))
    image = axes[0].imshow(flow, origin="lower", extent=[0, 1, 0, 1], cmap="YlGnBu")
    axes[0].set_title("flow channel")
    axes[0].set_xlabel("skill")
    axes[0].set_ylabel("challenge")
    fig.colorbar(image, ax=axes[0], fraction=0.046)
    axes[1].plot(interruptions, costs, marker="o", color=PALETTE["red"], label="cost")
    axes[1].plot(np.linspace(0, 8, 9), gains, marker="s", color=PALETTE["green"], label="enclosure gain")
    axes[1].set_title("technoference")
    axes[1].set_xlabel("interruptions / suppression")
    axes[1].legend()
    axes[2].bar(
        ["partner", "self", "canvas"],
        allocation,
        color=[PALETTE["blue"], PALETTE["orange"], PALETTE["purple"]],
    )
    axes[2].set_ylim(0, 1)
    axes[2].set_title("attention simplex")
    return _save(
        fig,
        out_dir,
        "neuroergonomics_flow.png",
        "fig:neuroergonomics_flow",
        "Neuroergonomic flow, technoference, and attention-allocation diagnostics.",
    )


def generate_evidence_synthesis_plot(out_dir: Path) -> Path:
    """Render the evidence graph as a bipartite lineage map."""
    graph = build_evidence_graph()
    domains = cast(list[str], graph["domains"])
    dimensions = cast(list[str], graph["dimensions"])
    edges = cast(list[tuple[str, str]], graph["edges"])
    nodes = cast(dict[str, list[str]], graph["nodes"])
    fig, ax = plt.subplots(figsize=(10.8, 6.8))
    y_domain = np.linspace(0.9, 0.1, len(domains))
    y_dim = np.linspace(0.95, 0.05, len(dimensions))
    domain_pos = {name: (0.08, y) for name, y in zip(domains, y_domain)}
    dim_pos = {name: (0.92, y) for name, y in zip(dimensions, y_dim)}
    ax.add_patch(plt.Rectangle((0.015, 0.02), 0.20, 0.94, facecolor=PALETTE["mist"], edgecolor="none", alpha=0.75))
    ax.add_patch(plt.Rectangle((0.76, 0.02), 0.22, 0.94, facecolor="#EEF8F5", edgecolor="none", alpha=0.75))
    for src, dst in edges:
        linewidth = 0.9 + 0.22 * min(len(nodes[dst]), 10)
        ax.plot(
            [domain_pos[src][0], dim_pos[dst][0]],
            [domain_pos[src][1], dim_pos[dst][1]],
            color=PALETTE["sky"],
            alpha=0.38,
            linewidth=linewidth,
        )
    for name, (x, y) in domain_pos.items():
        count = len(nodes[name])
        ax.scatter(x, y, s=150 + 24 * count, color=PALETTE["blue"], edgecolor="#FFFFFF", linewidth=1.1)
        ax.text(x + 0.025, y, name.replace("_", " "), va="center", fontsize=8, weight="bold")
        ax.text(x - 0.028, y, str(count), va="center", ha="center", fontsize=6.5, color="#FFFFFF", weight="bold")
    for name, (x, y) in dim_pos.items():
        count = len(nodes[name])
        ax.scatter(x, y, s=90 + 13 * count, color=PALETTE["green"], edgecolor="#FFFFFF", linewidth=0.9)
        ax.text(x - 0.025, y, name.replace("_", " "), ha="right", va="center", fontsize=7.7, weight="bold")
        ax.text(x + 0.030, y, str(count), va="center", ha="center", fontsize=6.2, color="#FFFFFF", weight="bold")
    ax.axis("off")
    ax.set_title("Evidence synthesis: PPPiP domains to DigiPPPiP dimensions")
    ax.text(0.08, 0.97, "source domains", ha="center", fontsize=8, color=PALETTE["blue"], weight="bold")
    ax.text(0.92, 0.97, "DigiPPPiP dimensions", ha="center", fontsize=8, color=PALETTE["green"], weight="bold")
    ax.text(
        0.50,
        0.02,
        "Node numbers are citekey counts; edges express lineage, not direct validation.",
        ha="center",
        fontsize=7.5,
        color=GRAMMAR["caution"],
    )
    return _save(
        fig,
        out_dir,
        "evidence_synthesis.png",
        "fig:evidence_synthesis",
        "Bipartite evidence graph from original PPPiP domains to DigiPPPiP dimensions.",
    )


def generate_research_agenda_plot(out_dir: Path) -> Path:
    """Render priorities for the proposed DigiPPPiP research agenda."""
    labels = [
        "hyperscanning",
        "geometric\nnetworks",
        "narrative\ninformation",
        "accessibility",
        "place-based",
        "active\ninference",
        "longitudinal",
    ]
    feasibility = np.array([0.65, 0.50, 0.80, 0.70, 0.75, 0.55, 0.45])
    value = np.array([0.90, 0.85, 0.75, 0.95, 0.70, 0.85, 0.95])
    x = np.arange(len(labels))
    width = 0.38
    fig, ax = plt.subplots(figsize=(8.5, 4))
    ax.bar(x - width / 2, feasibility, width, color=PALETTE["sky"], label="feasibility")
    ax.bar(x + width / 2, value, width, color=PALETTE["purple"], label="research value")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("relative priority score")
    ax.set_title("Research agenda priorities for DigiPPPiP")
    ax.legend()
    return _save(
        fig,
        out_dir,
        "research_agenda.png",
        "fig:research_agenda",
        "Conceptual priority map for DigiPPPiP empirical research.",
    )


def generate_conceptual_ecology(out_dir: Path) -> Path:
    """Render the actors, artifacts, signals, and contexts in one visual grammar."""
    fig, ax = plt.subplots(figsize=(9, 5.2))
    _setup_canvas(ax, "Conceptual ecology of DigiPPPiP")
    _box(ax, 0.16, 0.72, "partner A\nbody + intention", color=GRAMMAR["actor"])
    _box(ax, 0.84, 0.72, "partner B\nbody + intention", color=GRAMMAR["actor"])
    _box(ax, 0.30, 0.50, "device A\nstylus + screen", color=GRAMMAR["signal"])
    _box(ax, 0.70, 0.50, "device B\nstylus + screen", color=GRAMMAR["signal"])
    _box(ax, 0.50, 0.52, "shared canvas\nlayers + history", color=GRAMMAR["artifact"], width=0.22, height=0.16)
    _box(ax, 0.50, 0.28, "event log\nstrokes, pauses,\nundo, replay", color=GRAMMAR["artifact"], width=0.22)
    _box(ax, 0.16, 0.25, "local context\nhome, clinic,\npark, studio", color=GRAMMAR["context"])
    _box(ax, 0.84, 0.25, "remote context\nplace, schedule,\nprivacy", color=GRAMMAR["context"])
    for start, end in [
        ((0.22, 0.68), (0.26, 0.55)),
        ((0.78, 0.68), (0.74, 0.55)),
        ((0.36, 0.50), (0.39, 0.51)),
        ((0.64, 0.50), (0.61, 0.51)),
        ((0.50, 0.44), (0.50, 0.34)),
        ((0.24, 0.25), (0.39, 0.46)),
        ((0.76, 0.25), (0.61, 0.46)),
    ]:
        _arrow(ax, start, end)
    ax.text(0.50, 0.82, "awareness cues, consent rules, and latency policy shape every flow", ha="center", fontsize=8)
    _caveat(ax, "Conceptual system map: it specifies design relations, not measured effect sizes.")
    return _save(
        fig,
        out_dir,
        "conceptual_ecology.png",
        "fig:conceptual_ecology",
        "Actor-artifact-context ecology for DigiPPPiP shared drawing.",
    )


def generate_interaction_timeline(out_dir: Path) -> Path:
    """Render partner actions, awareness cues, and analysis windows on one timeline."""
    fig, ax = plt.subplots(figsize=(10.0, 4.8))
    ax.set_title("Dyadic interaction timeline for session instrumentation")
    ax.set_xlim(0, 60)
    ax.set_ylim(-0.75, 3.75)
    ax.set_xlabel("seconds")
    ax.set_yticks([3.0, 2.15, 1.25, 0.35], ["partner A", "partner B", "coordination", "analysis windows"])
    ax.grid(axis="x", alpha=0.25)
    intervals = {
        "partner A": [(2, 10), (16, 25), (35, 46), (50, 57)],
        "partner B": [(6, 14), (24, 32), (38, 49)],
    }
    for y, (name, spans) in zip([3.0, 2.15], intervals.items()):
        color = PALETTE["blue"] if name == "partner A" else PALETTE["orange"]
        for start, end in spans:
            ax.broken_barh(
                [(start, end - start)],
                (y - 0.19, 0.38),
                facecolors=color,
                alpha=0.82,
                edgecolors="#FFFFFF",
                linewidth=1.0,
            )
            ax.text((start + end) / 2, y, "stroke", ha="center", va="center", color="white", fontsize=7)
    coordination = [(4, 12, "overlap"), (23, 10, "tool handoff"), (36, 12, "joint repair"), (49, 8, "re-entry")]
    for start, width, label in coordination:
        ax.broken_barh(
            [(start, width)],
            (1.08, 0.34),
            facecolors=PALETTE["purple"],
            alpha=0.30,
            edgecolors=PALETTE["purple"],
            hatch="///",
        )
        ax.text(start + width / 2, 1.25, label, ha="center", va="center", fontsize=6.7, color=PALETTE["ink"])
    for center in [10, 20, 30, 40, 50]:
        ax.broken_barh([(center - 4, 8)], (0.18, 0.34), facecolors=PALETTE["green"], alpha=0.26)
        ax.text(center, 0.35, "sync\nwindow", ha="center", va="center", fontsize=6.6)
    ax.scatter([14, 33, 49], [1.72, 1.72, 1.72], color=PALETTE["red"], s=46, marker="X", label="repair / undo")
    ax.scatter([5, 28, 42], [3.45, 3.45, 3.45], color=PALETTE["purple"], s=44, marker="D", label="utterance")
    ax.scatter([24, 36, 50], [1.72, 1.72, 1.72], color=PALETTE["blue"], s=42, marker="s", label="tool control")
    ax.legend(loc="upper right", frameon=False, ncol=3, bbox_to_anchor=(1.0, 1.05))
    ax.text(
        30,
        -0.47,
        "Overlaps, handoffs, repairs, and delayed re-entry become auditable protocol events.",
        ha="center",
        fontsize=8,
    )
    return _save(
        fig,
        out_dir,
        "interaction_timeline.png",
        "fig:interaction_timeline",
        "Instrumented dyadic timeline linking visible actions to analysis windows.",
    )


def generate_parallel_sequential_patterns(out_dir: Path) -> Path:
    """Render parallel, alternating, and asynchronous mark-making patterns."""
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.6), sharey=True)
    patterns = {
        "parallel": ([0, 2, 4, 6, 8], [0.5, 2.3, 4.7, 6.2, 8.1]),
        "turn-taking": ([0, 3, 6, 9], [1.5, 4.5, 7.5, 10.5]),
        "asynchronous": ([0, 18, 38, 55], [9, 29, 48, 59]),
    }
    for ax, (name, (a_times, b_times)) in zip(axes, patterns.items()):
        ax.set_title(name)
        ax.eventplot(a_times, lineoffsets=1.0, linelengths=0.45, colors=PALETTE["blue"])
        ax.eventplot(b_times, lineoffsets=0.35, linelengths=0.45, colors=PALETTE["orange"])
        ax.set_xlabel("relative time")
        ax.set_yticks([1.0, 0.35], ["A", "B"])
        ax.set_ylim(0, 1.35)
        ax.grid(axis="x", alpha=0.2)
        ax.text(0.5, -0.30, _pattern_caption(name), ha="center", va="top", transform=ax.transAxes, fontsize=7)
    fig.suptitle("Parallel and sequential DigiPPPiP event patterns")
    return _save(
        fig,
        out_dir,
        "parallel_sequential_patterns.png",
        "fig:parallel_sequential_patterns",
        "Event-pattern comparison for parallel, turn-taking, and asynchronous sessions.",
    )


def _pattern_caption(name: str) -> str:
    captions = {
        "parallel": "overlap ratio high",
        "turn-taking": "alternation clear",
        "asynchronous": "delay is part of form",
    }
    return captions[name]


def generate_accessibility_features_overview(out_dir: Path) -> Path:
    """Render access features as design commitments rather than compliance claims."""
    fig, ax = plt.subplots(figsize=(8.8, 5))
    _setup_canvas(ax, "Accessibility features and accommodation mapping")
    features = [
        (0.25, 0.72, "input flexibility\nstylus, touch,\nkeyboard, switch", "actor"),
        (0.75, 0.72, "perceptual feedback\ncontrast, haptic,\naudio description", "signal"),
        (0.25, 0.42, "cognitive load\nplain language,\nlow distraction", "context"),
        (0.75, 0.42, "agency + privacy\nsave, delete,\nreplay control", "artifact"),
    ]
    for x, y, text, role in features:
        _box(ax, x, y, text, color=GRAMMAR[role], width=0.28, height=0.17, fontsize=8)
    _box(ax, 0.50, 0.22, "participatory validation\nwith disabled partners", color=GRAMMAR["caution"], width=0.32)
    for start in [(0.25, 0.64), (0.75, 0.64), (0.25, 0.34), (0.75, 0.34)]:
        _arrow(ax, start, (0.50, 0.28), color=GRAMMAR["caution"])
    _caveat(ax, "Accessibility is a documented capability set until evaluated with disabled users.")
    return _save(
        fig,
        out_dir,
        "accessibility_features_overview.png",
        "fig:accessibility_features_overview",
        "Accessibility feature map linking implementation supports to validation needs.",
    )


def generate_relational_microplaces(out_dir: Path) -> Path:
    """Render digital placemaking as recurring, situated canvas practice."""
    fig, ax = plt.subplots(figsize=(8.8, 5))
    _setup_canvas(ax, "Relational micro-places in DigiPPPiP")
    _box(ax, 0.50, 0.52, "persistent\nshared canvas", color=GRAMMAR["artifact"], width=0.22, height=0.16)
    places = [
        (0.18, 0.78, "kitchen\nritual"),
        (0.82, 0.78, "hospital\nroom"),
        (0.18, 0.26, "train\njourney"),
        (0.82, 0.26, "two-city\narchive"),
        (0.50, 0.84, "studio\npractice"),
    ]
    for x, y, label in places:
        _box(ax, x, y, label, color=GRAMMAR["context"], width=0.16, height=0.12)
        _arrow(ax, (x, y - 0.07 if y > 0.52 else y + 0.07), (0.50, 0.60 if y > 0.52 else 0.44))
    loop_x = np.linspace(0.37, 0.63, 40)
    loop_y = 0.52 + 0.18 * np.sin(np.linspace(0, 2 * np.pi, 40))
    ax.plot(loop_x, loop_y, color=PALETTE["green"], linestyle="--", alpha=0.8)
    ax.text(0.50, 0.14, "return visits, memory traces, and prompts make place persistent", ha="center", fontsize=8)
    return _save(
        fig,
        out_dir,
        "relational_microplaces.png",
        "fig:relational_microplaces",
        "Digital placemaking map for recurring DigiPPPiP relational micro-places.",
    )


def generate_hyperscanning_alignment(out_dir: Path) -> Path:
    """Render the alignment problem between behavior, physiology, and interpretation."""
    fig, axes = plt.subplots(3, 1, figsize=(8.8, 6), sharex=True)
    t = np.linspace(0, 60, 240)
    behavior = np.zeros_like(t)
    behavior[(t > 8) & (t < 18)] = 1
    behavior[(t > 30) & (t < 44)] = 1
    signal_a = 0.5 + 0.12 * np.sin(t / 4) + 0.05 * np.cos(t / 1.7)
    signal_b = 0.5 + 0.12 * np.sin((t - 1.8) / 4) + 0.04 * np.cos(t / 2.1)
    motion = np.exp(-0.5 * ((t - 34) / 1.3) ** 2) * 0.45
    axes[0].fill_between(t, 0, behavior, color=PALETTE["green"], alpha=0.35)
    axes[0].set_ylabel("event log")
    axes[0].set_title("A. behavior windows")
    axes[1].plot(t, signal_a + motion, color=PALETTE["blue"], label="partner A")
    axes[1].plot(t, signal_b + motion, color=PALETTE["orange"], label="partner B")
    axes[1].set_ylabel("raw proxy")
    axes[1].set_title("B. physiological channels with shared artifact")
    axes[1].legend(loc="upper right")
    axes[2].plot(t, signal_a, color=PALETTE["blue"])
    axes[2].plot(t, signal_b, color=PALETTE["orange"])
    axes[2].axvspan(32, 36, color=PALETTE["red"], alpha=0.16, label="motion exclusion")
    axes[2].set_ylabel("cleaned")
    axes[2].set_xlabel("seconds")
    axes[2].set_title("C. interpretation after artifact and permutation checks")
    axes[2].legend(loc="upper right")
    for ax in axes:
        ax.grid(alpha=0.2)
    return _save(
        fig,
        out_dir,
        "hyperscanning_alignment.png",
        "fig:hyperscanning_alignment",
        "Alignment schematic for behavior, physiology, artifact rejection, and cautious interpretation.",
    )


def generate_framework_template(out_dir: Path) -> Path:
    """Render the reusable visual grammar used by the conceptual framework."""
    fig, ax = plt.subplots(figsize=(9.8, 5.6))
    _setup_canvas(ax, "Reusable DigiPPPiP framework figure grammar")
    roles = [
        (0.14, 0.73, "actors\npartners, dyads", "actor", "label + position"),
        (0.38, 0.73, "artifacts\ncanvas, archive", "artifact", "central panel"),
        (0.62, 0.73, "signals\nstrokes, voice,\nphysiology", "signal", "arrow + tick"),
        (0.86, 0.73, "contexts\nplace, time,\naccess", "context", "boundary band"),
    ]
    for x, y, text, role, channel in roles:
        _box(ax, x, y, text, color=GRAMMAR[role], width=0.18, height=0.15, fontsize=8)
        ax.text(x, y - 0.12, channel, ha="center", fontsize=6.4, color=PALETTE["gray"])
    templates = [
        (0.14, 0.41, "architecture\nlayer map"),
        (0.38, 0.41, "protocol\ntimeline"),
        (0.62, 0.41, "diagnostic\nmetric plot"),
        (0.86, 0.41, "evidence\nclaim map"),
    ]
    for x, y, text in templates:
        _box(ax, x, y, text, color=PALETTE["sky"], width=0.18, height=0.14, fontsize=8, alpha=0.25)
    for x in [0.14, 0.38, 0.62, 0.86]:
        _arrow(ax, (x, 0.64), (x, 0.48))
        ax.plot([x - 0.055, x + 0.055], [0.31, 0.31], color=PALETTE["ink"], linewidth=1.2)
        ax.text(x, 0.27, "long description\nrequired", ha="center", fontsize=6.2, color=PALETTE["ink"])
    _box(
        ax,
        0.50,
        0.14,
        "caption + sidecar rule:\nencode what is shown, source/generator,\nclaim strength, reading order, and caveat",
        color=GRAMMAR["caution"],
        width=0.58,
        height=0.15,
    )
    return _save(
        fig,
        out_dir,
        "framework_template.png",
        "fig:framework_template",
        "Reusable visual grammar template for consistent DigiPPPiP figures and captions.",
    )


def generate_figure_generation_pipeline(out_dir: Path) -> Path:
    """Render the reproducible figure-generation method as an inspectable pipeline."""
    stages = figure_generation_stages()
    fig, ax = plt.subplots(figsize=(12.0, 5.9))
    _setup_canvas(ax, "Reproducible figure-generation method")
    ax.add_patch(plt.Rectangle((0.035, 0.565), 0.93, 0.25, facecolor=PALETTE["mist"], alpha=0.75, edgecolor="none"))
    ax.add_patch(plt.Rectangle((0.035, 0.235), 0.93, 0.255, facecolor="#FFF7E8", alpha=0.82, edgecolor="none"))
    xs = np.linspace(0.08, 0.92, len(stages))
    colors = [
        PALETTE["blue"],
        PALETTE["sky"],
        PALETTE["green"],
        PALETTE["orange"],
        PALETTE["sky"],
        PALETTE["purple"],
        PALETTE["green"],
        PALETTE["blue"],
        PALETTE["red"],
    ]
    for idx, (stage, x) in enumerate(zip(stages, xs)):
        ax.plot([x, x], [0.49, 0.565], color=colors[idx], linewidth=1.4, alpha=0.7)
        _box(
            ax,
            x,
            0.68,
            f"{stage.label}\n{stage.artifact}",
            color=colors[idx],
            width=0.112,
            height=0.18,
            fontsize=7,
            alpha=0.24,
        )
        gate = textwrap.fill(stage.quality_gate, width=17)
        _box(
            ax,
            x,
            0.34,
            gate,
            color=colors[idx],
            width=0.112,
            height=0.20,
            fontsize=5,
            alpha=0.16,
        )
        if idx < len(stages) - 1:
            _arrow(ax, (x + 0.055, 0.68), (xs[idx + 1] - 0.055, 0.68), color=colors[idx])
            _arrow(ax, (x + 0.055, 0.34), (xs[idx + 1] - 0.055, 0.34), color=PALETTE["gray"])
    ax.text(0.05, 0.805, "artifact chain", ha="left", fontsize=9, weight="bold", color=PALETTE["blue"])
    ax.text(0.05, 0.475, "quality gates", ha="left", fontsize=9, weight="bold", color=PALETTE["red"])
    ax.text(
        0.95,
        0.805,
        "ordered, tested, captioned, described, rendered",
        ha="right",
        fontsize=7.2,
        color=PALETTE["gray"],
    )
    _caveat(
        ax,
        "Visual intensity is governed: every figure must preserve claim status, source lineage, and accessible text.",
    )
    return _save(
        fig,
        out_dir,
        "figure_generation_pipeline.png",
        "fig:figure_generation_pipeline",
        "Pipeline from scoped manuscript claim to rendered, registered, and validated figure artifact.",
    )


def generate_method_source_bridge(out_dir: Path) -> Path:
    """Render the scholarship-to-method bridge behind generated figures."""
    families = figure_method_source_families()
    archetype_by_family = {item.source_family: item for item in composition_archetypes()}
    fig, ax = plt.subplots(figsize=(12.8, 7.0))
    _setup_canvas(ax, "Source-to-method bridge for generated figures")
    headers = ["method family", "composition archetype", "verified citekeys", "figure gate"]
    widths = [0.16, 0.29, 0.25, 0.26]
    x_lefts = np.cumsum([0.02, *widths[:-1]])
    row_height = 0.135
    for header, x, width in zip(headers, x_lefts, widths):
        rect = plt.Rectangle((x, 0.855), width, 0.085, facecolor=PALETTE["ink"], alpha=0.92, edgecolor=PALETTE["ink"])
        ax.add_patch(rect)
        ax.text(x + width / 2, 0.897, header, ha="center", va="center", fontsize=8, weight="bold", color="white")
    colors = [PALETTE["blue"], PALETTE["purple"], PALETTE["green"], PALETTE["sky"], PALETTE["orange"]]
    for row, family in enumerate(families):
        y = 0.76 - row * row_height
        archetype = archetype_by_family[family.key]
        source_text = ", ".join(family.source_keys)
        values = [
            family.label,
            f"{archetype.archetype}: {archetype.layout_rule}",
            f"{len(family.source_keys)} sources: {source_text}",
            family.quality_gate,
        ]
        for col, (value, x, width) in enumerate(zip(values, x_lefts, widths)):
            fill = colors[row % len(colors)] if col == 0 else "#FFFFFF"
            alpha = 0.34 if col == 0 else 0.88
            rect = plt.Rectangle(
                (x, y),
                width,
                row_height * 0.88,
                facecolor=fill,
                alpha=alpha,
                edgecolor=PALETTE["line"],
            )
            ax.add_patch(rect)
            if col == 2:
                ax.add_patch(
                    Circle(
                        (x + 0.025, y + row_height * 0.44),
                        0.020,
                        facecolor=colors[row % len(colors)],
                        edgecolor="#FFFFFF",
                        linewidth=0.8,
                    )
                )
                ax.text(
                    x + 0.025,
                    y + row_height * 0.44,
                    str(len(family.source_keys)),
                    ha="center",
                    va="center",
                    fontsize=6,
                    weight="bold",
                    color="#FFFFFF",
                )
                text_x = x + width / 2 + 0.018
            else:
                text_x = x + width / 2
            wrapped = textwrap.fill(value, width=17 if col == 0 else 35)
            ax.text(
                text_x,
                y + row_height * 0.44,
                wrapped,
                ha="center",
                va="center",
                fontsize=6.1,
                color=PALETTE["ink"],
            )
    ax.text(
        0.50,
        0.07,
        (
            "Perplexity can nominate sources, but this bridge uses only verified DOI, publisher, "
            "standard, or archival metadata."
        ),
        ha="center",
        fontsize=8,
        color=GRAMMAR["caution"],
    )
    return _save(
        fig,
        out_dir,
        "method_source_bridge.png",
        "fig:method_source_bridge",
        "Source-to-method bridge linking verified scholarship to generated-figure quality gates.",
    )


def generate_visual_encoding_matrix(out_dir: Path) -> Path:
    """Render the semantic role to visual-channel grammar."""
    channels = visual_encoding_channels()
    grammar_by_role = {rule.role: rule for rule in aesthetic_grammar_rules()}
    headers = ["role", "semantic target", "palette + non-color channel", "hierarchy + guardrail"]
    widths = [0.13, 0.27, 0.28, 0.28]
    x_lefts = np.cumsum([0.02, *widths[:-1]])
    row_height = 0.108
    fig, ax = plt.subplots(figsize=(12.0, 7.15))
    _setup_canvas(ax, "Visual encoding matrix for DigiPPPiP figures")
    for col, (header, x, width) in enumerate(zip(headers, x_lefts, widths)):
        rect = plt.Rectangle((x, 0.858), width, 0.082, facecolor=PALETTE["ink"], alpha=0.92, edgecolor=PALETTE["ink"])
        ax.add_patch(rect)
        ax.text(x + width / 2, 0.899, header, ha="center", va="center", fontsize=8, weight="bold", color="white")
    for row, channel in enumerate(channels):
        y = 0.78 - row * row_height
        rule = grammar_by_role[channel.role]
        role_color = rule.color_hex
        values = [
            channel.role,
            channel.semantic_target,
            f"{rule.palette_key}: {channel.visual_channel}; non-color: {rule.non_color_channel}",
            f"{rule.intensity_level} intensity; {rule.hierarchy_rule}; guardrail: {channel.guardrail}",
        ]
        for col, (value, x, width) in enumerate(zip(values, x_lefts, widths)):
            fill = role_color if col == 0 else "#FFFFFF"
            alpha = 0.35 if col == 0 else 0.88
            rect = plt.Rectangle(
                (x, y),
                width,
                row_height * 0.86,
                facecolor=fill,
                alpha=alpha,
                edgecolor=PALETTE["line"],
            )
            ax.add_patch(rect)
            if col == 2:
                ax.add_patch(
                    plt.Rectangle(
                        (x + 0.012, y + row_height * 0.22),
                        0.022,
                        row_height * 0.38,
                        facecolor=role_color,
                        edgecolor=PALETTE["gray"],
                        linewidth=0.4,
                    )
                )
                ax.plot(
                    [x + 0.045, x + 0.088],
                    [y + row_height * 0.31, y + row_height * 0.56],
                    color=role_color,
                    linewidth=1.8,
                )
                text_x = x + width / 2 + 0.014
            else:
                text_x = x + width / 2
            wrapped = textwrap.fill(value, width=14 if col == 0 else 34)
            ax.text(
                text_x,
                y + row_height * 0.43,
                wrapped,
                ha="center",
                va="center",
                fontsize=6.15,
                color=PALETTE["ink"],
            )
    ax.text(
        0.50,
        0.07,
        "The matrix is a design grammar: visual force must remain label-backed, contrast-aware, and claim-bounded.",
        ha="center",
        fontsize=8,
        color=GRAMMAR["caution"],
    )
    return _save(
        fig,
        out_dir,
        "visual_encoding_matrix.png",
        "fig:visual_encoding_matrix",
        "Semantic role to visual-channel matrix for generated DigiPPPiP framework figures.",
    )


def generate_figure_method_audit(out_dir: Path) -> Path:
    """Render the project-level audit over generated figure methods."""
    criteria = figure_audit_criteria()
    labels = [criterion.label for criterion in criteria]
    scores = np.array([criterion.score for criterion in criteria], dtype=float)
    y = np.arange(len(criteria))
    fig, ax = plt.subplots(figsize=(10.0, 6.0))
    colors = [PALETTE["blue"], PALETTE["sky"], PALETTE["green"], PALETTE["purple"], PALETTE["orange"], PALETTE["red"]]
    ax.barh(y, scores, color=[colors[index % len(colors)] for index in y], alpha=0.82, edgecolor="#FFFFFF")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("audit score")
    ax.set_title(
        f"Generated-figure method contract: mean criterion score {figure_method_score():.2f}",
        pad=14,
        color=PALETTE["ink"],
    )
    for idx, criterion in enumerate(criteria):
        ax.text(
            0.03,
            idx,
            textwrap.shorten(criterion.rationale, width=70, placeholder="..."),
            va="center",
            fontsize=6.8,
            color="white",
            weight="bold",
        )
        ax.text(1.02, idx, criterion.status, va="center", fontsize=7, color=PALETTE["ink"], weight="bold")
    ax.text(
        0.50,
        -0.18,
        textwrap.fill("Caption contract: " + "; ".join(caption_contract_items()), width=120),
        ha="center",
        va="top",
        fontsize=7,
        color=GRAMMAR["caution"],
        transform=ax.transAxes,
    )
    return _save(
        fig,
        out_dir,
        "figure_method_audit.png",
        "fig:figure_method_audit",
        "Audit of deterministic inputs, registry entries, captions, claim boundaries, accessibility text, "
        "and references.",
    )


GENERATORS: tuple[FigureGenerator, ...] = (
    generate_evolution_timeline,
    generate_conceptual_ecology,
    generate_cyberphysical_spectrum,
    generate_cpss_architecture,
    generate_dyadic_task_matrix,
    generate_interaction_timeline,
    generate_parallel_sequential_patterns,
    generate_taxonomy_matrix,
    generate_event_logging_schema,
    generate_active_inference_mapping,
    generate_active_inference_loop,
    generate_network_analysis_pipeline,
    generate_ibs_phase_plot,
    generate_accessibility_audit_radar,
    generate_geometric_hyperscanning_plot,
    generate_hyperscanning_alignment,
    generate_source_quality_map,
    generate_claim_boundary_matrix,
    generate_claim_ledger_matrix,
    generate_source_verification_readiness,
    generate_study_readiness_matrix,
    generate_narrative_information_plot,
    generate_multilevel_outcome_model,
    generate_epistemic_arc_plot,
    generate_neuroergonomics_flow_plot,
    generate_accessibility_features_overview,
    generate_evidence_synthesis_plot,
    generate_relational_microplaces,
    generate_framework_template,
    generate_figure_generation_pipeline,
    generate_method_source_bridge,
    generate_visual_encoding_matrix,
    generate_figure_method_audit,
    generate_validation_ladder,
    generate_research_agenda_plot,
)


def _validate_generator_catalog() -> None:
    actual = tuple(generator.__name__ for generator in GENERATORS)
    if actual != FIGURE_GENERATOR_NAMES:
        raise RuntimeError("figure generator catalog is out of sync with src/figures.py")


def _write_long_description_sidecars(out_dir: Path) -> None:
    sidecar_dir = out_dir / "long_descriptions"
    sidecar_dir.mkdir(parents=True, exist_ok=True)
    for filename, description in figure_long_description_map().items():
        (sidecar_dir / f"{Path(filename).stem}.md").write_text(description)


def main(project_root: Path | None = None) -> list[Path]:
    """Generate all registered figures and the metrics JSON."""
    root = Path.cwd() if project_root is None else Path(project_root)
    apply_visualization_style()
    _validate_generator_catalog()
    FIGURE_REGISTRY.clear()
    out_dir = root / "output" / "figures"
    data_dir = root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    paths = [generator(out_dir) for generator in GENERATORS]
    _write_long_description_sidecars(out_dir)
    (out_dir / "figure_registry.json").write_text(json.dumps(FIGURE_REGISTRY, indent=2, sort_keys=True) + "\n")
    manuscript_text = "\n".join(path.read_text() for path in sorted((root / "manuscript").glob("[0-9][0-9]_*.md")))
    artifact_audit = audit_figure_artifacts(FIGURE_REGISTRY, out_dir, manuscript_text)
    (out_dir / "figure_artifact_audit.json").write_text(
        json.dumps(audit_to_dict(artifact_audit), indent=2, sort_keys=True) + "\n"
    )
    metrics = compute_all_metrics(_load_experiment(root))
    (data_dir / "digippppip_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    write_provenance_manifest(root)
    return paths


if __name__ == "__main__":
    main()
