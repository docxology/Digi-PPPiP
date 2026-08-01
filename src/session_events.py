"""Session-event primitives for DigiPPPiP protocol design.

The module models timestamped drawing, speech, AI-assist, and consent events
without depending on any rendering or infrastructure code. It is used by the
methods/protocol section to keep temporal claims reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class SessionEvent:
    """One timestamped event in a DigiPPPiP session log."""

    timestamp_s: float
    actor: str
    action: str
    channel: str


@dataclass(frozen=True)
class EventLogSummary:
    """Compact summary of a validated session event log."""

    event_count: int
    actor_count: int
    duration_s: float
    mean_interval_s: float
    temporal_mode: str
    turn_balance: float


def validate_events(events: list[SessionEvent]) -> list[SessionEvent]:
    """Return events sorted by timestamp after validating required invariants."""
    if not events:
        raise ValueError("events must be non-empty")
    for event in events:
        if event.timestamp_s < 0:
            raise ValueError("event timestamps must be non-negative")
        if not event.actor.strip():
            raise ValueError("event actors must be non-empty")
        if not event.action.strip():
            raise ValueError("event actions must be non-empty")
        if not event.channel.strip():
            raise ValueError("event channels must be non-empty")
    return sorted(events, key=lambda event: event.timestamp_s)


def inter_event_intervals(events: list[SessionEvent]) -> list[float]:
    """Return consecutive event intervals in seconds."""
    ordered = validate_events(events)
    return [
        ordered[index].timestamp_s - ordered[index - 1].timestamp_s
        for index in range(1, len(ordered))
    ]


def session_duration(events: list[SessionEvent]) -> float:
    """Return elapsed seconds between first and last event."""
    ordered = validate_events(events)
    return float(ordered[-1].timestamp_s - ordered[0].timestamp_s)


def turn_balance(events: list[SessionEvent], partner_actors: set[str] | None = None) -> float:
    """Return a dyadic balance score in ``[0, 1]``.

    The value is one when the two most active actors contribute equally and
    approaches zero as one actor dominates. Pass ``partner_actors`` (the two
    human dyad members) so that extra actors — an AI prompt source, a
    facilitator, a third cue — are excluded from the balance denominator, as
    the module documents. When ``partner_actors`` is omitted, the top two most
    active actors overall are used (legacy behavior).
    """
    ordered = validate_events(events)
    counts: dict[str, int] = {}
    for event in ordered:
        if partner_actors is not None and event.actor not in partner_actors:
            continue
        counts[event.actor] = counts.get(event.actor, 0) + 1
    if partner_actors is not None:
        counts = {actor: counts.get(actor, 0) for actor in partner_actors}
    top_two = sorted(counts.values(), reverse=True)[:2]
    if len(top_two) < 2:
        return 0.0
    high, low = top_two[0], top_two[1]
    return float(low / high) if high else 0.0


def classify_temporal_mode(
    events: list[SessionEvent],
    synchronous_threshold_s: float = 5.0,
    asynchronous_threshold_s: float = 300.0,
) -> str:
    """Classify a log as synchronous, semisynchronous, or asynchronous.

    The classifier uses the mean interval between events. Very short intervals
    imply a live shared session; long intervals imply a persistent artifact
    revisited over time; middle intervals imply turn-taking or bursty exchange.
    """
    if synchronous_threshold_s <= 0 or asynchronous_threshold_s <= synchronous_threshold_s:
        raise ValueError("thresholds must satisfy 0 < synchronous < asynchronous")
    intervals = inter_event_intervals(events)
    if not intervals:
        return "synchronous"
    avg = mean(intervals)
    if avg <= synchronous_threshold_s:
        return "synchronous"
    if avg >= asynchronous_threshold_s:
        return "asynchronous"
    return "semisynchronous"


def summarize_event_log(events: list[SessionEvent]) -> EventLogSummary:
    """Return a deterministic protocol summary for a session log."""
    ordered = validate_events(events)
    intervals = inter_event_intervals(ordered)
    actors = {event.actor for event in ordered}
    return EventLogSummary(
        event_count=len(ordered),
        actor_count=len(actors),
        duration_s=session_duration(ordered),
        mean_interval_s=float(mean(intervals)) if intervals else 0.0,
        temporal_mode=classify_temporal_mode(ordered),
        turn_balance=turn_balance(ordered),
    )


def example_protocol_events() -> list[SessionEvent]:
    """Return a small protocol trace used by figures, metrics, and tests."""
    return [
        SessionEvent(0.0, "partner_a", "stroke", "stylus"),
        SessionEvent(2.0, "partner_b", "stroke", "stylus"),
        SessionEvent(5.0, "partner_a", "voice_reflection", "audio"),
        SessionEvent(9.0, "partner_b", "stroke", "stylus"),
        SessionEvent(14.0, "partner_a", "consent_marker", "interface"),
        SessionEvent(20.0, "partner_b", "archive_annotation", "text"),
    ]
