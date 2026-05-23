"""Reusable figure-generation method primitives for DigiPPPiP.

The plotting workflow in ``src/figures.py`` is intentionally coverage-omitted,
so this module holds the tested method contract behind the manuscript's figure
system: stages, audit criteria, encoding roles, and caption requirements.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class FigureGenerationStage:
    """One reproducible stage in the figure-generation pipeline."""

    key: str
    label: str
    artifact: str
    quality_gate: str
    score: float


@dataclass(frozen=True)
class FigureAuditCriterion:
    """One yes/no or scored criterion for generated manuscript figures."""

    key: str
    label: str
    rationale: str
    status: str
    score: float


@dataclass(frozen=True)
class VisualEncodingChannel:
    """Mapping from manuscript semantics to visual encodings and guardrails."""

    role: str
    semantic_target: str
    visual_channel: str
    guardrail: str


@dataclass(frozen=True)
class FigureMethodSourceFamily:
    """Mapping from method scholarship to one figure-generation gate."""

    key: str
    label: str
    method_role: str
    source_keys: tuple[str, ...]
    quality_gate: str


@dataclass(frozen=True)
class AestheticGrammarRule:
    """One semantic role in the governed visual style."""

    role: str
    palette_key: str
    color_hex: str
    non_color_channel: str
    intensity_level: str
    hierarchy_rule: str
    accessibility_constraint: str


@dataclass(frozen=True)
class FigureCompositionArchetype:
    """Composition pattern tied to a figure-method source family."""

    source_family: str
    archetype: str
    layout_rule: str
    annotation_density: str
    intensity_level: str
    accessibility_constraint: str


@dataclass(frozen=True)
class ContrastRequirement:
    """Minimum contrast contract for figure foreground/background pairs."""

    key: str
    foreground: str
    background: str
    minimum_ratio: float
    usage: str
    non_color_backup: str


AESTHETIC_PALETTE: dict[str, str] = {
    "paper": "#F8FBFF",
    "mist": "#EAF3FF",
    "line": "#C7D7EA",
    "ink": "#17202A",
    "gray": "#334155",
    "blue": "#174EA6",
    "sky": "#2BA7D8",
    "green": "#007C72",
    "orange": "#D99A00",
    "red": "#C94C02",
    "purple": "#B44D8B",
    "violet": "#5B4DB8",
}


FIGURE_GENERATION_STAGES: tuple[FigureGenerationStage, ...] = (
    FigureGenerationStage(
        key="claim_scope",
        label="claim scope",
        artifact="section argument",
        quality_gate="status marked as conceptual, protocol, audit, analytic simulation, or empirical placeholder",
        score=1.0,
    ),
    FigureGenerationStage(
        key="method_lineage",
        label="method lineage",
        artifact="source-to-method bridge",
        quality_gate="scholarship mapped to the figure gate it warrants",
        score=1.0,
    ),
    FigureGenerationStage(
        key="tested_primitive",
        label="tested primitive",
        artifact="src module",
        quality_gate="source logic covered by unit tests or explicitly conceptual",
        score=1.0,
    ),
    FigureGenerationStage(
        key="visual_encoding",
        label="visual encoding",
        artifact="role and channel map",
        quality_gate="roles use stable palette keys, non-colour channels, labels, and colourblind-safe hues",
        score=1.0,
    ),
    FigureGenerationStage(
        key="deterministic_render",
        label="deterministic render",
        artifact="PNG artifact",
        quality_gate="fixed data, deterministic layout, 300 dpi output",
        score=1.0,
    ),
    FigureGenerationStage(
        key="registry",
        label="registry",
        artifact="figure_registry.json",
        quality_gate="label, file, generator, and description all present",
        score=1.0,
    ),
    FigureGenerationStage(
        key="caption_reference",
        label="caption reference",
        artifact="Pandoc figure block",
        quality_gate="caption states generator, claim status, and manuscript role",
        score=1.0,
    ),
    FigureGenerationStage(
        key="accessibility_description",
        label="accessibility description",
        artifact="caption and alt text",
        quality_gate="caption explains marks, axes, reading order, and interpretation limits",
        score=1.0,
    ),
    FigureGenerationStage(
        key="render_validation",
        label="render validation",
        artifact="tests and PDF/HTML",
        quality_gate="references resolve and rendered files contain no unresolved tokens",
        score=1.0,
    ),
)


FIGURE_AUDIT_CRITERIA: tuple[FigureAuditCriterion, ...] = (
    FigureAuditCriterion(
        key="deterministic_inputs",
        label="deterministic inputs",
        rationale="Figures should be reproducible from tracked code and configuration.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="registry_entry",
        label="registry entry",
        rationale="Every manuscript figure needs a machine-readable label and file path.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="caption_contract",
        label="caption contract",
        rationale="Captions carry provenance, meaning, claim status, and caveats.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="claim_boundary",
        label="claim boundary",
        rationale="Conceptual diagrams must not borrow authority from empirical sources.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="source_alignment",
        label="source alignment",
        rationale="Figure methods cite verified visualization and reproducibility scholarship.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="method_lineage",
        label="method lineage",
        rationale="Design, access, privacy, and reproducibility sources should warrant specific figure gates.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="accessibility_text",
        label="accessibility text",
        rationale="Captions and prose should expose the encoded content beyond the image.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="legend_axis_integrity",
        label="legend and axis integrity",
        rationale="Axes, legends, labels, and scales should identify how to read encoded values.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="aesthetic_accessibility",
        label="aesthetic accessibility",
        rationale="Visual intensity should come from hierarchy, layout, labels, and contrast rather than color alone.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="text_fit_readability",
        label="text-fit readability",
        rationale="Dense matrix and table figures should bound label length and protect text from patterned cells.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="render_resolution",
        label="render resolution",
        rationale="Generated PNGs should be legible in PDF and web outputs.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="auto_numbered_refs",
        label="auto-numbered refs",
        rationale="Manuscript references should resolve through Pandoc labels.",
        status="required",
        score=1.0,
    ),
    FigureAuditCriterion(
        key="claim_status_visible",
        label="visible claim status",
        rationale=(
            "Each rendered figure should visibly distinguish conceptual, protocol, audit, simulation, "
            "and placeholder status."
        ),
        status="required",
        score=1.0,
    ),
)


VISUAL_ENCODING_CHANNELS: tuple[VisualEncodingChannel, ...] = (
    VisualEncodingChannel(
        role="actors",
        semantic_target="partners, dyads, facilitators, and AI assistants",
        visual_channel="blue outlined role boxes, A/B labels, and left-right position",
        guardrail="never imply equivalence between humans and software agents",
    ),
    VisualEncodingChannel(
        role="artifacts",
        semantic_target="canvas, archive, event log, and generated output",
        visual_channel="green centered boxes, solid fills, and archive glyph labels",
        guardrail="distinguish shared artifacts from measured outcomes",
    ),
    VisualEncodingChannel(
        role="signals",
        semantic_target="strokes, pauses, voice, physiological channels, and awareness cues",
        visual_channel="orange arrows, tick marks, timelines, and directional labels",
        guardrail="mark signal processing requirements before interpretation",
    ),
    VisualEncodingChannel(
        role="contexts",
        semantic_target="place, schedule, access setting, and privacy boundary",
        visual_channel="purple peripheral layers, boundary bands, and location labels",
        guardrail="keep placemaking claims at micro-place scale unless directly studied",
    ),
    VisualEncodingChannel(
        role="evidence",
        semantic_target="claim strength, study gate, source class, and lineage",
        visual_channel="sky matrices, bars, ranks, and bipartite links",
        guardrail="separate conceptual support from empirical validation",
    ),
    VisualEncodingChannel(
        role="models",
        semantic_target="active inference, information theory, and multilevel outcomes",
        visual_channel="green or violet model lines, equations, and labelled components",
        guardrail="state when the model is illustrative rather than fitted",
    ),
    VisualEncodingChannel(
        role="caveats",
        semantic_target="risk boundaries, exclusions, and interpretation limits",
        visual_channel="red callouts, warning outlines, bottom notes, and status badges",
        guardrail="place limits inside the figure when they constrain interpretation",
    ),
)


AESTHETIC_GRAMMAR_RULES: tuple[AestheticGrammarRule, ...] = (
    AestheticGrammarRule(
        role="actors",
        palette_key="blue",
        color_hex=AESTHETIC_PALETTE["blue"],
        non_color_channel="role labels, left/right placement, and outlined nodes",
        intensity_level="high",
        hierarchy_rule="human actors occupy primary nodes before tools or agents",
        accessibility_constraint="actors must be readable from labels and position without relying on hue",
    ),
    AestheticGrammarRule(
        role="artifacts",
        palette_key="green",
        color_hex=AESTHETIC_PALETTE["green"],
        non_color_channel="solid central panels and artifact nouns",
        intensity_level="high",
        hierarchy_rule="shared artifacts sit at the compositional center when they mediate the relation",
        accessibility_constraint="artifact labels must distinguish canvas, archive, event log, and output",
    ),
    AestheticGrammarRule(
        role="signals",
        palette_key="orange",
        color_hex=AESTHETIC_PALETTE["orange"],
        non_color_channel="arrows, event ticks, and temporal ordering",
        intensity_level="medium",
        hierarchy_rule="signals connect actors to artifacts and should not dominate outcome claims",
        accessibility_constraint="signal meaning must be recoverable from arrow direction or axis labels",
    ),
    AestheticGrammarRule(
        role="contexts",
        palette_key="purple",
        color_hex=AESTHETIC_PALETTE["purple"],
        non_color_channel="peripheral bands, boundary outlines, and place labels",
        intensity_level="medium",
        hierarchy_rule="contexts frame the drawing event without becoming untested outcomes",
        accessibility_constraint="context scopes must be named in text, not encoded only by border color",
    ),
    AestheticGrammarRule(
        role="evidence",
        palette_key="sky",
        color_hex=AESTHETIC_PALETTE["sky"],
        non_color_channel="rank, bar length, matrix cell text, and link topology",
        intensity_level="high",
        hierarchy_rule="evidence figures foreground claim ceiling, source tier, or upgrade gate",
        accessibility_constraint="matrix and bar figures must include text values or labels for key cells",
    ),
    AestheticGrammarRule(
        role="models",
        palette_key="violet",
        color_hex=AESTHETIC_PALETTE["violet"],
        non_color_channel="line style, equations, and named latent components",
        intensity_level="medium",
        hierarchy_rule="model figures place variables and caveats before visual drama",
        accessibility_constraint="synthetic or illustrative status must appear in caption and figure stamp",
    ),
    AestheticGrammarRule(
        role="caveats",
        palette_key="red",
        color_hex=AESTHETIC_PALETTE["red"],
        non_color_channel="warning badges, lower-third notes, and outline weight",
        intensity_level="high",
        hierarchy_rule="caveats stay visible whenever they limit interpretation",
        accessibility_constraint="risk boundaries must be written as text, not only signaled by red",
    ),
)


FIGURE_COMPOSITION_ARCHETYPES: tuple[FigureCompositionArchetype, ...] = (
    FigureCompositionArchetype(
        source_family="shared_workspace",
        archetype="relational field",
        layout_rule="place partners, shared surface, and awareness cues in one spatial field",
        annotation_density="moderate",
        intensity_level="high",
        accessibility_constraint="actor and artifact labels must remain visible at manuscript scale",
    ),
    FigureCompositionArchetype(
        source_family="research_through_design",
        archetype="annotated artifact chain",
        layout_rule="show artifact, warrant, caveat, and claim status as a traceable chain",
        annotation_density="dense",
        intensity_level="high",
        accessibility_constraint="annotations must explain why the artifact is a research object",
    ),
    FigureCompositionArchetype(
        source_family="visualization_reproducibility",
        archetype="provenance pipeline",
        layout_rule="connect deterministic input, transformation, artifact, and validation gate",
        annotation_density="dense",
        intensity_level="medium",
        accessibility_constraint="process order must be clear from arrows or row/column ordering",
    ),
    FigureCompositionArchetype(
        source_family="accessible_visual_media",
        archetype="description-first audit surface",
        layout_rule="foreground what is encoded and how nonvisual reading remains possible",
        annotation_density="dense",
        intensity_level="medium",
        accessibility_constraint="every encoded role must have a text equivalent or label",
    ),
    FigureCompositionArchetype(
        source_family="privacy_values",
        archetype="governance matrix",
        layout_rule="pair participant control, conflict rule, and evidence boundary in the same view",
        annotation_density="dense",
        intensity_level="high",
        accessibility_constraint="privacy state must be named, not represented only by a color scale",
    ),
)


CONTRAST_REQUIREMENTS: tuple[ContrastRequirement, ...] = (
    ContrastRequirement(
        key="body_text",
        foreground=AESTHETIC_PALETTE["ink"],
        background=AESTHETIC_PALETTE["paper"],
        minimum_ratio=7.0,
        usage="primary annotation and table text",
        non_color_backup="font weight, labels, and positional grouping",
    ),
    ContrastRequirement(
        key="matrix_cell_label",
        foreground=AESTHETIC_PALETTE["ink"],
        background=AESTHETIC_PALETTE["paper"],
        minimum_ratio=7.0,
        usage="matrix cell labels on pale backing",
        non_color_backup="bounded wrapping, label backing, and numeric cell values",
    ),
    ContrastRequirement(
        key="blue_badge",
        foreground=AESTHETIC_PALETTE["blue"],
        background=AESTHETIC_PALETTE["paper"],
        minimum_ratio=4.5,
        usage="actor badges and source bars",
        non_color_backup="role label and outline shape",
    ),
    ContrastRequirement(
        key="green_badge",
        foreground=AESTHETIC_PALETTE["green"],
        background=AESTHETIC_PALETTE["paper"],
        minimum_ratio=4.5,
        usage="artifact and protocol badges",
        non_color_backup="central placement and label nouns",
    ),
    ContrastRequirement(
        key="caveat_badge",
        foreground=AESTHETIC_PALETTE["red"],
        background=AESTHETIC_PALETTE["paper"],
        minimum_ratio=3.0,
        usage="claim-status and caveat callouts",
        non_color_backup="warning text and heavier outline",
    ),
)


FIGURE_METHOD_SOURCE_FAMILIES: tuple[FigureMethodSourceFamily, ...] = (
    FigureMethodSourceFamily(
        key="shared_workspace",
        label="shared workspace",
        method_role="treat marks, gestures, gaze, and workspace state as interactional data",
        source_keys=(
            "tang1991collaborativework",
            "ishii1993clearboard",
            "gutwin2002workspaceawareness",
            "scott2004territoriality",
            "oittinen2025videodrawing",
        ),
        quality_gate="canvas figures must distinguish final marks from process and awareness cues",
    ),
    FigureMethodSourceFamily(
        key="research_through_design",
        label="research through design",
        method_role="let generated diagrams function as inspectable design-research artifacts",
        source_keys=(
            "zimmerman2007rtd",
            "gaver2012expectrtd",
            "gaver2012annotated",
            "dalsgaard2012documentation",
        ),
        quality_gate="each figure states its conceptual contribution and its documentation trail",
    ),
    FigureMethodSourceFamily(
        key="visualization_reproducibility",
        label="visual reproducibility",
        method_role="compose marks through explicit grammars and preserve computational provenance",
        source_keys=(
            "bostock2011d3",
            "satyanarayan2017vegalite",
            "ragan2016provenance",
            "heer2012interactive",
            "crameri2020colour",
            "rule2019jupyter",
            "stodden2014reproducible",
            "lebaron2025remoteviz",
        ),
        quality_gate="registry rows, render artifacts, and captions must be regenerable and traceable",
    ),
    FigureMethodSourceFamily(
        key="accessible_visual_media",
        label="accessible visual media",
        method_role="translate visual content into semantic descriptions and collaborative access supports",
        source_keys=(
            "morris2016pictures",
            "branham2015collaborativeaccess",
            "w3c2024altdecisiontree",
            "lundgard2022accessible",
            "elavsky2024datanavigator",
            "jones2024customization",
        ),
        quality_gate="captions, long descriptions, and navigable labels must expose visual structure and sequence",
    ),
    FigureMethodSourceFamily(
        key="privacy_values",
        label="privacy and values",
        method_role="treat persistence, export, deletion, and authorship as negotiated social practices",
        source_keys=(
            "nissenbaum2011contextualprivacy",
            "dourish2006collectiveprivacy",
            "petronio2020cpm",
            "shilton2012values",
            "kassam2023digitalconsent",
            "pendse2024consentforward",
        ),
        quality_gate="figures with archives, logs, or replay must surface consent and governance caveats",
    ),
)


CAPTION_CONTRACT_ITEMS: tuple[str, ...] = (
    "what the figure encodes",
    "which code module or data source generated it",
    "which method lineage warrants the figure form",
    "which manuscript argument it supports",
    "how to read the main marks, axes, or panels",
    "whether it is conceptual, protocol, audit, analytic simulation, or empirical placeholder",
    "which caveat limits interpretation",
    "what future evidence would upgrade the claim",
)


def figure_generation_stages() -> tuple[FigureGenerationStage, ...]:
    """Return the ordered figure-generation pipeline."""
    return FIGURE_GENERATION_STAGES


def figure_audit_criteria() -> tuple[FigureAuditCriterion, ...]:
    """Return the figure-audit criteria enforced by the project."""
    return FIGURE_AUDIT_CRITERIA


def visual_encoding_channels() -> tuple[VisualEncodingChannel, ...]:
    """Return the semantic role to visual channel grammar."""
    return VISUAL_ENCODING_CHANNELS


def aesthetic_palette() -> dict[str, str]:
    """Return the governed visual palette used by generated figures."""
    return dict(AESTHETIC_PALETTE)


def aesthetic_grammar_rules() -> tuple[AestheticGrammarRule, ...]:
    """Return the semantic visual style contract."""
    return AESTHETIC_GRAMMAR_RULES


def composition_archetypes() -> tuple[FigureCompositionArchetype, ...]:
    """Return method-family composition archetypes."""
    return FIGURE_COMPOSITION_ARCHETYPES


def contrast_requirements() -> tuple[ContrastRequirement, ...]:
    """Return minimum contrast requirements for rendered figures."""
    return CONTRAST_REQUIREMENTS


def figure_method_source_families() -> tuple[FigureMethodSourceFamily, ...]:
    """Return the source families that warrant the figure method gates."""
    return FIGURE_METHOD_SOURCE_FAMILIES


def figure_method_source_keys() -> set[str]:
    """Return all citekeys used by the figure-method source bridge."""
    keys: set[str] = set()
    for family in FIGURE_METHOD_SOURCE_FAMILIES:
        keys.update(family.source_keys)
    return keys


def caption_contract_items() -> tuple[str, ...]:
    """Return the required semantic elements for manuscript figure captions."""
    return CAPTION_CONTRACT_ITEMS


def figure_method_score() -> float:
    """Return the mean audit score for the current method contract."""
    return mean(criterion.score for criterion in FIGURE_AUDIT_CRITERIA)


def contrast_ratio(foreground: str, background: str) -> float:
    """Return the WCAG-style contrast ratio for two hex colors."""

    def channel(value: int) -> float:
        normalized = value / 255
        if normalized <= 0.03928:
            return normalized / 12.92
        return float(((normalized + 0.055) / 1.055) ** 2.4)

    def luminance(color: str) -> float:
        value = color.removeprefix("#")
        red, green, blue = (int(value[index:index + 2], 16) for index in (0, 2, 4))
        return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)

    fore_luminance = luminance(foreground)
    back_luminance = luminance(background)
    lighter = max(fore_luminance, back_luminance)
    darker = min(fore_luminance, back_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def figure_method_counts() -> dict[str, int]:
    """Return manuscript-bound counts for figure-method primitives."""
    return {
        "generation_stages": len(FIGURE_GENERATION_STAGES),
        "audit_criteria": len(FIGURE_AUDIT_CRITERIA),
        "visual_roles": len(VISUAL_ENCODING_CHANNELS),
        "aesthetic_roles": len(AESTHETIC_GRAMMAR_RULES),
        "composition_archetypes": len(FIGURE_COMPOSITION_ARCHETYPES),
        "contrast_requirements": len(CONTRAST_REQUIREMENTS),
        "method_source_families": len(FIGURE_METHOD_SOURCE_FAMILIES),
        "caption_contract_items": len(CAPTION_CONTRACT_ITEMS),
    }
