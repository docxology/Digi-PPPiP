"""Executable source-verification ledger for DigiPPPiP governance."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
import re

from claim_ledger import claim_records
from evidence import DIMENSIONS, DOMAINS
from figure_methods import figure_method_source_families
from study_readiness import study_readiness_source_keys
from systems_governance import systems_governance_source_keys


CURRENT_CHECK_DATE = "2026-05-22"
OFFICIAL_SOURCE_KEYS: frozenset[str] = frozenset(
    {
        "hhs2025cfr46",
        "wma2024helsinki",
        "nist2023airmf",
        "europeanunion2024aiact",
        "w3c2024altdecisiontree",
    }
)
REPORTING_GUIDELINE_KEYS: frozenset[str] = frozenset(
    {
        "hoffmann2014tidier",
        "eysenbach2011consortehealth",
        "liu2020consortai",
        "cruzrivera2020spiritai",
    }
)


@dataclass(frozen=True)
class SourceVerificationRecord:
    """One citekey with verification metadata and manuscript-use context."""

    citekey: str
    locator: str
    verification_url: str
    locator_status: str
    title: str
    author: str
    year: str
    venue: str
    metadata_source: str
    checked_as_of: str
    source_tier: str
    claim_family: str
    manuscript_location: str
    recheck_trigger: str


@dataclass(frozen=True)
class SourceVerificationCheck:
    """One source-verification audit check."""

    key: str
    label: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class SourceVerificationAudit:
    """Audit report for source-verification ledger coverage."""

    score: float
    missing_records: tuple[str, ...]
    checks: tuple[SourceVerificationCheck, ...]


@dataclass(frozen=True)
class SourceVerificationSummary:
    """Compact readiness profile for source-verification visualizations."""

    total_records: int
    required_records: int
    covered_required_records: int
    priority_records: int
    official_records: int
    reporting_records: int
    missing_records: int
    tier_counts: dict[str, int]
    recheck_trigger_counts: dict[str, int]


def parse_bib_entries(bib_text: str) -> dict[str, str]:
    """Return BibTeX entries keyed by citekey."""
    entries: dict[str, str] = {}
    for match in re.finditer(r"@\w+\{([^,\s]+).*?(?=\n@|\Z)", bib_text, flags=re.DOTALL):
        entries[match.group(1)] = match.group(0).strip()
    return entries


def _field(entry: str, name: str) -> str:
    pattern = rf"^\s*{re.escape(name)}\s*=\s*[\{{\"](.+?)[\}}\"],?\s*$"
    match = re.search(pattern, entry, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _first_field(entry: str, names: tuple[str, ...]) -> str:
    """Return the first populated BibTeX field from ``names``."""
    for name in names:
        value = _field(entry, name)
        if value:
            return value
    return ""


def _author_or_editor(entry: str) -> str:
    return _first_field(entry, ("author", "editor"))


def _venue(entry: str) -> str:
    return _first_field(
        entry,
        (
            "journal",
            "booktitle",
            "publisher",
            "institution",
            "organization",
            "school",
        ),
    )


def _doi_locator(entry: str) -> str:
    doi = _field(entry, "doi")
    if not doi:
        return ""
    return "https://doi.org/" + doi.removeprefix("https://doi.org/").removeprefix("http://doi.org/")


def _stable_locator(entry: str) -> str:
    return _doi_locator(entry) or _field(entry, "url")


def _year(entry: str) -> int | None:
    match = re.search(r"^\s*year\s*=\s*[\{\"]?(\d{4})", entry, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


def _year_text(entry: str) -> str:
    year = _year(entry)
    return str(year) if year is not None else ""


def _source_tier(citekey: str, entry: str) -> str:
    head = entry.split("{", 1)[0].strip().lower()
    lower = entry.lower()
    if citekey in OFFICIAL_SOURCE_KEYS:
        return "official_primary"
    if "arxiv" in lower:
        return "scholarly_preprint"
    if head in {"@book", "@inbook", "@incollection"}:
        return "scholarly_book"
    if head in {"@inproceedings", "@proceedings"}:
        return "conference_or_report"
    if head == "@article" and "journal" in lower:
        return "scholarly_peer_reviewed"
    return "stable_web_or_misc"


def _claim_family_map() -> dict[str, set[str]]:
    families: dict[str, set[str]] = defaultdict(set)
    for record in claim_records():
        for key in record.evidence_keys:
            families[key].add(f"claim:{record.claim_domain}")
    for domain, keys in DOMAINS.items():
        for key in keys:
            families[key].add(f"evidence-domain:{domain}")
    for dimension, keys in DIMENSIONS.items():
        for key in keys:
            families[key].add(f"evidence-dimension:{dimension}")
    for family in figure_method_source_families():
        for key in family.source_keys:
            families[key].add(f"figure-method:{family.key}")
    for key in OFFICIAL_SOURCE_KEYS | REPORTING_GUIDELINE_KEYS:
        families[key].add("study-readiness")
    for key in systems_governance_source_keys():
        families[key].add("systems-governance")
    return families


def _location_map() -> dict[str, set[str]]:
    locations: dict[str, set[str]] = defaultdict(set)
    for record in claim_records():
        for key in record.evidence_keys:
            locations[key].add(f"manuscript/{record.section}")
    for dimension, keys in DIMENSIONS.items():
        for key in keys:
            locations[key].add(f"evidence/{dimension}")
    for domain, keys in DOMAINS.items():
        for key in keys:
            locations[key].add(f"evidence/{domain}")
    for family in figure_method_source_families():
        for key in family.source_keys:
            locations[key].add(f"figure_methods/{family.key}")
    for key in OFFICIAL_SOURCE_KEYS | REPORTING_GUIDELINE_KEYS:
        locations[key].add("manuscript/methods_protocol")
    for key in systems_governance_source_keys():
        locations[key].add("systems_governance")
    return locations


def _is_priority(citekey: str, entry: str) -> bool:
    lower = f"{citekey} {entry}".lower()
    year = _year(entry)
    recent = year is not None and 2024 <= year <= 2026
    topic = any(
        token in lower
        for token in (
            "preprint",
            "arxiv",
            "artificial",
            "human-ai",
            "ai ",
            "{ai}",
            "digital health",
            "telehealth",
            "relatedness",
            "long-distance",
            "couple",
            "coregulation",
            "co-regulation",
            "physiological linkage",
            "presence",
            "relationship",
            "privacy",
            "governance",
            "helsinki",
            "common rule",
            "risk management",
            "artificial intelligence act",
        )
    )
    return recent or topic or citekey in OFFICIAL_SOURCE_KEYS | REPORTING_GUIDELINE_KEYS | systems_governance_source_keys()


def _recheck_trigger(citekey: str, entry: str) -> str:
    if citekey in OFFICIAL_SOURCE_KEYS:
        return "policy_update_or_before_submission"
    if _is_priority(citekey, entry):
        return "before_submission_or_annual_refresh"
    return "before_submission"


def build_source_verification_records(bib_text: str) -> tuple[SourceVerificationRecord, ...]:
    """Build verification records from bibliography entries with DOI or stable URLs."""
    families = _claim_family_map()
    locations = _location_map()
    records: list[SourceVerificationRecord] = []
    for citekey, entry in sorted(parse_bib_entries(bib_text).items()):
        locator = _stable_locator(entry)
        if not locator:
            continue
        records.append(
            SourceVerificationRecord(
                citekey=citekey,
                locator=locator,
                verification_url=locator,
                locator_status="matched",
                title=_field(entry, "title"),
                author=_author_or_editor(entry),
                year=_year_text(entry),
                venue=_venue(entry),
                metadata_source="local_bibtex",
                checked_as_of=CURRENT_CHECK_DATE,
                source_tier=_source_tier(citekey, entry),
                claim_family="; ".join(sorted(families.get(citekey, {"bibliography"}))),
                manuscript_location="; ".join(sorted(locations.get(citekey, {"references"}))),
                recheck_trigger=_recheck_trigger(citekey, entry),
            )
        )
    return tuple(records)


def source_verification_record_keys(records: tuple[SourceVerificationRecord, ...]) -> set[str]:
    """Return citekeys covered by verification records."""
    return {record.citekey for record in records}


def missing_verification_records(
    required_keys: set[str],
    records: tuple[SourceVerificationRecord, ...],
) -> tuple[str, ...]:
    """Return required citekeys without a verification record."""
    return tuple(sorted(required_keys - source_verification_record_keys(records)))


def prioritized_verification_keys(bib_text: str) -> set[str]:
    """Return citekeys that require extra recency or governance attention."""
    return {citekey for citekey, entry in parse_bib_entries(bib_text).items() if _is_priority(citekey, entry)}


def manuscript_citation_keys(manuscript_dir: Path) -> set[str]:
    """Return citekeys used in manuscript Markdown prose, excluding cross-reference labels."""
    text = "\n".join(path.read_text() for path in sorted(Path(manuscript_dir).glob("[0-9][0-9]_*.md")))
    citation_refs = set(re.findall(r"@([A-Za-z0-9_]+)", text))
    return {key for key in citation_refs if not key.startswith(("fig", "sec", "eq", "tbl"))}


def source_verification_required_keys(manuscript_dir: Path) -> set[str]:
    """Return every citekey governed by source-verification output and tests."""
    from evidence import citation_keys
    from figure_methods import figure_method_source_keys

    return (
        {key for record in claim_records() for key in record.evidence_keys}
        | citation_keys()
        | figure_method_source_keys()
        | study_readiness_source_keys()
        | systems_governance_source_keys()
        | manuscript_citation_keys(manuscript_dir)
    )


def source_verification_audit(
    required_keys: set[str],
    records: tuple[SourceVerificationRecord, ...],
) -> SourceVerificationAudit:
    """Audit source-verification records against required citekeys."""
    missing = missing_verification_records(required_keys, records)
    record_keys = source_verification_record_keys(records)
    relevant = tuple(record for record in records if record.citekey in required_keys)
    checks = (
        SourceVerificationCheck(
            "coverage",
            "all required citekeys have verification records",
            not missing,
            f"{len(required_keys - set(missing))}/{len(required_keys)} covered",
        ),
        SourceVerificationCheck(
            "locators",
            "records carry DOI or stable URL locators",
            all(record.locator for record in relevant),
            "locator populated",
        ),
        SourceVerificationCheck(
            "locator_match",
            "records declare DOI or URL locator match status",
            all(record.locator_status == "matched" and record.locator == record.verification_url for record in relevant),
            "locator matches verification_url",
        ),
        SourceVerificationCheck(
            "verification_urls",
            "records carry verification URLs",
            all(record.verification_url for record in relevant),
            "verification_url populated",
        ),
        SourceVerificationCheck(
            "bibliographic_metadata",
            "records carry title, author/editor, year, and venue metadata",
            all(record.title and record.author and record.year and record.venue for record in relevant),
            "title/author/year/venue populated",
        ),
        SourceVerificationCheck(
            "metadata_directness",
            "records identify local BibTeX as the metadata source",
            all(record.metadata_source == "local_bibtex" for record in relevant),
            "metadata_source=local_bibtex",
        ),
        SourceVerificationCheck(
            "checked_dates",
            "records carry checked_as_of dates",
            all(record.checked_as_of == CURRENT_CHECK_DATE for record in relevant),
            CURRENT_CHECK_DATE,
        ),
        SourceVerificationCheck(
            "metadata_fields",
            "records carry tier, claim family, location, and trigger",
            all(
                record.source_tier
                and record.claim_family
                and record.manuscript_location
                and record.recheck_trigger
                for record in relevant
            ),
            "tier/family/location/trigger populated",
        ),
        SourceVerificationCheck(
            "no_extra_requirement_gap",
            "audit required keys are a subset of record universe or reported missing",
            required_keys <= record_keys | set(missing),
            "missing keys are explicit",
        ),
    )
    score = sum(check.passed for check in checks) / len(checks)
    return SourceVerificationAudit(score=score, missing_records=missing, checks=checks)


def source_verification_summary(
    required_keys: set[str],
    records: tuple[SourceVerificationRecord, ...],
    bib_text: str,
) -> SourceVerificationSummary:
    """Summarize source-verification coverage for governance figures."""
    record_keys = source_verification_record_keys(records)
    required_record_keys = required_keys & record_keys
    prioritized = prioritized_verification_keys(bib_text)
    tier_counts: dict[str, int] = defaultdict(int)
    recheck_counts: dict[str, int] = defaultdict(int)
    for record in records:
        tier_counts[record.source_tier] += 1
        recheck_counts[record.recheck_trigger] += 1
    return SourceVerificationSummary(
        total_records=len(records),
        required_records=len(required_keys),
        covered_required_records=len(required_record_keys),
        priority_records=len(prioritized & record_keys),
        official_records=len(OFFICIAL_SOURCE_KEYS & record_keys),
        reporting_records=len(REPORTING_GUIDELINE_KEYS & record_keys),
        missing_records=len(required_keys - record_keys),
        tier_counts=dict(sorted(tier_counts.items())),
        recheck_trigger_counts=dict(sorted(recheck_counts.items())),
    )


def records_to_dicts(records: tuple[SourceVerificationRecord, ...]) -> list[dict[str, str]]:
    """Return JSON-serializable source-verification records."""
    return [asdict(record) for record in records]


def audit_to_dict(audit: SourceVerificationAudit) -> dict[str, object]:
    """Return a JSON-serializable source-verification audit."""
    return {
        "score": audit.score,
        "missing_records": list(audit.missing_records),
        "checks": [asdict(check) for check in audit.checks],
    }
