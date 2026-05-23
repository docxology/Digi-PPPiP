"""Single numeric authority for the DigiPPPiP manuscript.

EVERY scalar that reaches the manuscript (via ``manuscript_variables.py``) is
computed here, by composing the tested primitive layer — never in the
coverage-omitted ``figures.py``. This module IS coverage-enforced; its tests
pin closed-form ground truth. Pure (numpy + stdlib).
"""

from __future__ import annotations

from dataclasses import fields
from typing import Any

import numpy as np

from accessibility import CRITERIA, audit_capabilities
from active_inference import simulate_dyadic_session
from aesthetics import aha_magnitude, epistemic_arc, peak_step
from evidence import DOMAINS, DIMENSIONS, evidence_coverage
from figure_catalog import figure_count
from figure_methods import (
    FIGURE_AUDIT_CRITERIA,
    FIGURE_GENERATION_STAGES,
    FIGURE_METHOD_SOURCE_FAMILIES,
    VISUAL_ENCODING_CHANNELS,
    caption_contract_items,
    figure_method_score,
)
from hyperscanning import (
    curvature_entropy,
    detect_phase_transitions,
    forman_ricci_curvature,
    inter_brain_network,
    simulate_ibs_phases,
)
from outcomes import OUTCOME_MEASURES, design_claim_strength, outcome_domains
from session_events import EventLogSummary, example_protocol_events, summarize_event_log
from source_quality import CLAIM_BOUNDARIES, TYPE_STRENGTH, VALIDATION_LADDER
from systems_governance import governance_score, governance_summary
from taxonomy import SpatialConfig, TemporalMode, build_taxonomy, taxonomy_matrix

# metric name -> the primitive module that produces it (documentation + the
# integration-consistency test's audit that no metric originates in figures.py).
METRIC_SPECS: dict[str, str] = {
    "NUM_MODALITIES": "taxonomy",
    "NUM_TEMPORAL_MODES": "taxonomy",
    "NUM_SPATIAL_CONFIGS": "taxonomy",
    "TAXONOMY_PEAK_SYNCHRONY": "taxonomy",
    "COUPLED_FE_FINAL": "active_inference",
    "DECOUPLED_FE_FINAL": "active_inference",
    "FE_REDUCTION_ABS": "active_inference",
    "IBS_INITIATION_MEAN": "hyperscanning",
    "IBS_CONVERGENCE_MEAN": "hyperscanning",
    "IBS_GAIN": "hyperscanning",
    "CURVATURE_ENTROPY_MAX": "hyperscanning",
    "NUM_CURVATURE_TRANSITIONS": "hyperscanning",
    "NARRATIVE_MAX_ENTROPY_BITS": "narrative",
    "EPISTEMIC_AHA_MAGNITUDE": "aesthetics",
    "EPISTEMIC_PEAK_STEP": "aesthetics",
    "NUM_EVIDENCE_DOMAINS": "evidence",
    "NUM_EVIDENCE_DIMENSIONS": "evidence",
    "EVIDENCE_COVERAGE_PCT": "evidence",
    "NUM_EVENT_LOG_FIELDS": "session_events",
    "EVENT_LOG_MEAN_INTERVAL_S": "session_events",
    "EVENT_LOG_TURN_BALANCE": "session_events",
    "NUM_OUTCOME_MEASURES": "outcomes",
    "NUM_OUTCOME_DOMAINS": "outcomes",
    "DEFAULT_DESIGN_STRENGTH_SCORE": "outcomes",
    "NUM_ACCESSIBILITY_CRITERIA": "accessibility",
    "ACCESSIBILITY_AUDIT_SCORE": "accessibility",
    "NUM_SOURCE_QUALITY_TYPES": "source_quality",
    "NUM_CLAIM_BOUNDARY_DOMAINS": "source_quality",
    "NUM_VALIDATION_LADDER_STAGES": "source_quality",
    "NUM_SYSTEM_BOUNDARY_ELEMENTS": "systems_governance",
    "NUM_FEEDBACK_LOOPS": "systems_governance",
    "NUM_CAUSAL_ASSUMPTIONS": "systems_governance",
    "NUM_ETHICS_GATES": "systems_governance",
    "SYSTEM_GOVERNANCE_SCORE": "systems_governance",
    "NUM_FIGURE_METHOD_STAGES": "figure_methods",
    "NUM_FIGURE_AUDIT_CRITERIA": "figure_methods",
    "NUM_VISUAL_ENCODING_ROLES": "figure_methods",
    "NUM_FIGURE_METHOD_SOURCE_FAMILIES": "figure_methods",
    "NUM_CAPTION_CONTRACT_ITEMS": "figure_methods",
    "FIGURE_METHOD_SCORE": "figure_methods",
    "NUM_FIGURES": "figures",
}

NUM_FIGURES = figure_count()


def _defaults() -> dict[str, Any]:
    return {
        "random_seed": 0,
        "dyadic_steps": 60,
        "session_steps": 120,
        "prior_precision": 1.0,
        "likelihood_precision": 2.0,
        "network_nodes": 8,
        "curvature_transition_threshold": 0.15,
        "narrative_alphabet_size": 6,
        "epistemic_curiosity": 1.0,
        "epistemic_precision": 0.6,
    }


def compute_all_metrics(config: dict[str, Any] | None = None) -> dict[str, float | int]:
    """Compute every manuscript-bound scalar from the tested primitives.

    Deterministic given ``config`` (an ``experiment:`` block, or defaults).
    Returns JSON-serializable Python scalars.
    """
    cfg = _defaults()
    if config:
        cfg.update({k: v for k, v in config.items() if k in cfg})
    seed = int(cfg["random_seed"])

    # --- taxonomy ---
    modalities = build_taxonomy()
    sync_matrix = taxonomy_matrix("neural_synchrony")

    # --- active inference ---
    coupled = simulate_dyadic_session(
        steps=int(cfg["dyadic_steps"]), coupled=True, seed=seed,
        prior_prec=float(cfg["prior_precision"]), lik_prec=float(cfg["likelihood_precision"]),
    )["free_energy"]
    decoupled = simulate_dyadic_session(
        steps=int(cfg["dyadic_steps"]), coupled=False, seed=seed,
        prior_prec=float(cfg["prior_precision"]), lik_prec=float(cfg["likelihood_precision"]),
    )["free_energy"]
    fe_c, fe_d = float(coupled[-1]), float(decoupled[-1])
    # Absolute joint-free-energy reduction from coupling (denominator-robust,
    # unlike a percentage when decoupled FE is near zero).
    fe_reduction = fe_d - fe_c

    # --- hyperscanning ---
    sess = simulate_ibs_phases(steps=int(cfg["session_steps"]), seed=seed)
    ibs, phase = sess["ibs"], sess["phase"]
    ibs_init = float(ibs[phase == "initiation"].mean())
    ibs_conv = float(ibs[phase == "convergence"].mean())
    entropies = np.array(
        [curvature_entropy(forman_ricci_curvature(inter_brain_network(t, int(cfg["network_nodes"]), seed)))
         for t in range(int(cfg["session_steps"]))],
        dtype=float,
    )
    transitions = detect_phase_transitions(entropies, float(cfg["curvature_transition_threshold"]))

    # --- narrative ---
    narrative_hmax = float(np.log2(int(cfg["narrative_alphabet_size"])))

    # --- aesthetics ---
    arc = epistemic_arc(int(cfg["session_steps"]), float(cfg["epistemic_curiosity"]), float(cfg["epistemic_precision"]))

    # --- protocol, outcomes, accessibility, source quality ---
    event_summary = summarize_event_log(example_protocol_events())
    default_design = design_claim_strength(80, randomized=True, longitudinal=True)
    design_strength_score = {
        "descriptive": 1,
        "associational": 2,
        "comparative": 3,
        "causal_candidate": 4,
    }[default_design]
    accessibility_score = audit_capabilities(
        {
            "stylus",
            "touch",
            "keyboard",
            "switch",
            "voice",
            "high_contrast",
            "audio_description",
            "haptic_feedback",
            "plain_language",
            "low_distraction_mode",
            "save_consent",
            "delete_control",
            "replay_control",
            "assisted_drawing",
            "role_switching",
        }
    ).score
    governance = governance_summary()

    metrics: dict[str, float | int] = {
        "NUM_MODALITIES": len(modalities),
        "NUM_TEMPORAL_MODES": len(TemporalMode),
        "NUM_SPATIAL_CONFIGS": len(SpatialConfig),
        "TAXONOMY_PEAK_SYNCHRONY": round(float(sync_matrix.max()), 4),
        "COUPLED_FE_FINAL": round(fe_c, 6),
        "DECOUPLED_FE_FINAL": round(fe_d, 6),
        "FE_REDUCTION_ABS": round(fe_reduction, 6),
        "IBS_INITIATION_MEAN": round(ibs_init, 4),
        "IBS_CONVERGENCE_MEAN": round(ibs_conv, 4),
        "IBS_GAIN": round(ibs_conv - ibs_init, 4),
        "CURVATURE_ENTROPY_MAX": round(float(entropies.max()), 4),
        "NUM_CURVATURE_TRANSITIONS": int(transitions.size),
        "NARRATIVE_MAX_ENTROPY_BITS": round(narrative_hmax, 4),
        "EPISTEMIC_AHA_MAGNITUDE": round(aha_magnitude(arc), 6),
        "EPISTEMIC_PEAK_STEP": int(peak_step(arc)) + 1,
        "NUM_EVIDENCE_DOMAINS": len(DOMAINS),
        "NUM_EVIDENCE_DIMENSIONS": len(DIMENSIONS),
        "EVIDENCE_COVERAGE_PCT": round(100.0 * evidence_coverage(), 2),
        "NUM_EVENT_LOG_FIELDS": len(fields(EventLogSummary)),
        "EVENT_LOG_MEAN_INTERVAL_S": round(event_summary.mean_interval_s, 4),
        "EVENT_LOG_TURN_BALANCE": round(event_summary.turn_balance, 4),
        "NUM_OUTCOME_MEASURES": len(OUTCOME_MEASURES),
        "NUM_OUTCOME_DOMAINS": len(outcome_domains()),
        "DEFAULT_DESIGN_STRENGTH_SCORE": design_strength_score,
        "NUM_ACCESSIBILITY_CRITERIA": len(CRITERIA),
        "ACCESSIBILITY_AUDIT_SCORE": round(accessibility_score, 4),
        "NUM_SOURCE_QUALITY_TYPES": len(TYPE_STRENGTH),
        "NUM_CLAIM_BOUNDARY_DOMAINS": len(CLAIM_BOUNDARIES),
        "NUM_VALIDATION_LADDER_STAGES": len(VALIDATION_LADDER),
        "NUM_SYSTEM_BOUNDARY_ELEMENTS": governance["system_boundary_elements"],
        "NUM_FEEDBACK_LOOPS": governance["feedback_loops"],
        "NUM_CAUSAL_ASSUMPTIONS": governance["causal_assumptions"],
        "NUM_ETHICS_GATES": governance["ethics_gates"],
        "SYSTEM_GOVERNANCE_SCORE": round(governance_score(), 4),
        "NUM_FIGURE_METHOD_STAGES": len(FIGURE_GENERATION_STAGES),
        "NUM_FIGURE_AUDIT_CRITERIA": len(FIGURE_AUDIT_CRITERIA),
        "NUM_VISUAL_ENCODING_ROLES": len(VISUAL_ENCODING_CHANNELS),
        "NUM_FIGURE_METHOD_SOURCE_FAMILIES": len(FIGURE_METHOD_SOURCE_FAMILIES),
        "NUM_CAPTION_CONTRACT_ITEMS": len(caption_contract_items()),
        "FIGURE_METHOD_SCORE": round(figure_method_score(), 4),
        "NUM_FIGURES": NUM_FIGURES,
    }
    return metrics
