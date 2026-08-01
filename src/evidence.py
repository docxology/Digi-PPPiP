"""Evidence-synthesis graph: original PPPiP domains → DigiPPPiP dimensions.

Operationalizes the framework's synthesis: the five evidence domains of the
foundational PPPiP paper extend into the new DigiPPPiP dimensions. Nodes carry
BibTeX citation keys (all present in ``manuscript/references.bib``); the
domain→dimension layer is a bipartite DAG. Pure (numpy + stdlib).
"""

from __future__ import annotations

import numpy as np

# Original PPPiP evidence domains and their citation keys.
DOMAINS: dict[str, list[str]] = {
    "art_therapy": ["mikhailova2018pppip"],
    "neural_synchrony": ["czeszumski2020hyperscanning", "czeszumski2022cooperative", "azhari2025online"],
    "partner_improvisation": ["mikhailova2018pppip"],
    "controlled_novelty": ["mikhailova2018pppip"],
    "free_energy_principle": ["friston2010fep", "friston2023simpler"],
}

# DigiPPPiP dimensions and their citation keys.
DIMENSIONS: dict[str, list[str]] = {
    "cyberphysical": [
        "sobb2023cpss",
        "tang1991collaborativework",
        "erickson2000socialtranslucence",
        "gutwin2002workspaceawareness",
        "ishii1993clearboard",
        "jansen2021cocreative",
        "shneiderman2007creativity",
        "scott2004territoriality",
        "heer2008collaborativeva",
        "horvitz1999mixedinitiative",
        "amershi2019humanai",
        "deterding2017mixedinitiative",
        "sun2011pentablet",
        "close2024codesign",
    ],
    "temporal": [
        "lagera2023asynchronous",
        "olson2000distance",
        "clark1991grounding",
        "sebanz2006joint",
        "oittinen2025videodrawing",
    ],
    "active_inference": [
        "friston2017process",
        "parr2022activeinference",
        "dacosta2020discrete",
        "friston2023simpler",
        "vasil2020communication",
        "schilbach2013secondperson",
        "redcay2019secondperson",
        "bolis2024secondperson",
        "bouizegarene2024narrative",
    ],
    "neuroergonomics": [
        "ayaz2019neuroergonomics",
        "dehais2020grand",
        "moffat2024mobilefnirs",
        "csikszentmihalyi1989flow",
        "mcdaniel2016technoference",
    ],
    "phenomenology": [
        "merleauponty2012phenomenology",
        "lombard1997presence",
        "biocca1997cyborg",
        "lee2004presence",
        "atuk2024bodiesonline",
        "oittinen2025videodrawing",
    ],
    "accessibility": [
        "zubala2021digitalarttherapy",
        "reitere2024telehealth",
        "frauenberger2011participatory",
        "shinohara2016socialaccess",
        "wobbrock2011ability",
        "w3c2023wcag22",
        "w3c2021coga",
        "datlen2020whatsapp",
        "morris2016pictures",
        "branham2015collaborativeaccess",
        "elavsky2024datanavigator",
        "jones2024customization",
    ],
    "relational_aesthetics": [
        "bourriaud2002relational",
        "bishop2004antagonism",
        "vaisvaser2024neurodynamics",
        "snir2013joint",
        "butler2012coregulation",
        "timmons2015physiologicallinkage",
        "paley2022familycoregulation",
        "yoon2025phygital",
    ],
    "place_based": [
        "gordon2011netlocality",
        "lewicka2011place",
        "dourish2006respace",
        "foth2015digitalcity",
        "canelas2025placemaking",
    ],
    "dyadic_health": [
        "shaffer2022dyadic",
        "wilson2024dyadichealth",
        "benmessaoud2023dyadicmodule",
        "blair2024remoteddp",
        "kernova2025relationship",
        "hassenzahl2012love",
        "neustaedter2012intimacy",
        "vetere2005mediating",
        "kaye2006clicked",
        "mcveighschultz2015couple",
        "wenhart2025relatedness",
        "jiang2025ipillowpal",
        "nissenbaum2011contextualprivacy",
        "palen2003privacy",
        "petronio2020cpm",
        "kassam2023digitalconsent",
        "pendse2024consentforward",
        "dourish2006collectiveprivacy",
        "shilton2012values",
        "won2026venus",
        "malfacini2025companionai",
        "potash2020pandemics",
        "miller2020onlinearttherapy",
        "datlen2020whatsapp",
        "haywood2022hexagonal",
        "kaimal2016cortisol",
        "zubala2021digitalarttherapy",
    ],
    "systems_governance": [
        "friston2010fep",
        "ramstead2020two",
        "nissenbaum2011contextualprivacy",
        "dourish2006collectiveprivacy",
        "shilton2012values",
        "hoffmann2014tidier",
        "hhs2025cfr46",
        "wma2024helsinki",
        "amershi2019humanai",
        "nist2023airmf",
    ],
    "geometric_hyperscanning": [
        "cui2012nirs",
        "czeszumski2020hyperscanning",
        "tachtsidis2016fnirs",
        "hamilton2021hyperscanning",
        "nam2020hyperscanningreview",
        "provenzi2022translational",
        "zimmermann2024methodological",
        "hinrichs2025geometric",
        "forman2003bochner",
        "weber2016forman",
    ],
    "narrative_information": ["schulz2024narrativeinfo", "shannon1948mathematical"],
    "figure_methods": [
        "wilkinson2005grammar",
        "cleveland1984graphical",
        "wickham2010layered",
        "munzner2009nested",
        "kelleher2011guidelines",
        "rougier2014figures",
        "wilson2017goodenough",
        "lundgard2022accessible",
        "elavsky2024datanavigator",
        "jones2024customization",
        "bostock2011d3",
        "satyanarayan2017vegalite",
        "ragan2016provenance",
        "rule2019jupyter",
        "weibel2012digitalpen",
        "lebaron2025remoteviz",
        "zimmerman2007rtd",
        "gaver2012expectrtd",
        "gaver2012annotated",
        "dalsgaard2012documentation",
        "heer2012interactive",
        "stodden2014reproducible",
    ],
}

# Domain → dimension lineage. Every dimension is a target of ≥1 edge so
# evidence_coverage() == 1.0; the layered structure is acyclic by construction.
_EDGES: list[tuple[str, str]] = [
    ("art_therapy", "relational_aesthetics"),
    ("art_therapy", "accessibility"),
    ("art_therapy", "place_based"),
    ("neural_synchrony", "geometric_hyperscanning"),
    ("neural_synchrony", "neuroergonomics"),
    ("neural_synchrony", "temporal"),
    ("neural_synchrony", "cyberphysical"),
    ("partner_improvisation", "active_inference"),
    ("partner_improvisation", "narrative_information"),
    ("controlled_novelty", "phenomenology"),
    ("controlled_novelty", "dyadic_health"),
    ("controlled_novelty", "systems_governance"),
    ("free_energy_principle", "active_inference"),
    ("free_energy_principle", "systems_governance"),
    ("free_energy_principle", "geometric_hyperscanning"),
    ("free_energy_principle", "narrative_information"),
    ("controlled_novelty", "figure_methods"),
]


def build_evidence_graph() -> dict[str, object]:
    """Return the evidence graph: nodes (with citations) and lineage edges."""
    nodes: dict[str, list[str]] = {**DOMAINS, **DIMENSIONS}
    return {
        "domains": list(DOMAINS),
        "dimensions": list(DIMENSIONS),
        "nodes": nodes,
        "edges": list(_EDGES),
    }


def domain_dimension_edges() -> list[tuple[str, str]]:
    """Return the domain→dimension edges, validated for referential integrity.

    Raises:
        ValueError: if any edge endpoint is not a declared node.
    """
    for src, dst in _EDGES:
        if src not in DOMAINS:
            raise ValueError(f"edge source {src!r} is not a declared domain")
        if dst not in DIMENSIONS:
            raise ValueError(f"edge target {dst!r} is not a declared dimension")
    return list(_EDGES)


def evidence_coverage() -> float:
    """Fraction of DigiPPPiP dimensions with ≥1 supporting citation (``[0,1]``)."""
    covered = sum(1 for keys in DIMENSIONS.values() if len(keys) >= 1)
    return covered / len(DIMENSIONS)


def citation_keys() -> set[str]:
    """All BibTeX keys referenced by the evidence graph (must exist in the .bib)."""
    keys: set[str] = set()
    for ks in DOMAINS.values():
        keys.update(ks)
    for ks in DIMENSIONS.values():
        keys.update(ks)
    return keys


def is_acyclic(edges: list[tuple[str, str]] | None = None) -> bool:
    """True iff the domain→dimension edge layer is acyclic (Kahn's algorithm).

    ``edges`` defaults to the module-level ``_EDGES`` layer; pass an explicit
    edge list to test arbitrary (including cyclic) graphs.
    """
    edge_list = _EDGES if edges is None else edges
    nodes = list(DOMAINS) + list(DIMENSIONS)
    indeg = {n: 0 for n in nodes}
    for _, dst in edge_list:
        indeg[dst] += 1
    queue = [n for n in nodes if indeg[n] == 0]
    visited = 0
    while queue:
        n = queue.pop()
        visited += 1
        for src, dst in edge_list:
            if src == n:
                indeg[dst] -= 1
                if indeg[dst] == 0:
                    queue.append(dst)
    return visited == len(nodes)


def adjacency() -> np.ndarray:
    """Symmetric 0/1 adjacency of the undirected projection over all nodes."""
    nodes = list(DOMAINS) + list(DIMENSIONS)
    index = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    adj = np.zeros((n, n), dtype=float)
    for src, dst in _EDGES:
        i, j = index[src], index[dst]
        adj[i, j] = 1.0
        adj[j, i] = 1.0
    return adj
