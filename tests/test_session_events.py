import pytest

from session_events import (
    SessionEvent,
    classify_temporal_mode,
    example_protocol_events,
    inter_event_intervals,
    session_duration,
    summarize_event_log,
    turn_balance,
    validate_events,
)


def test_session_events_validate_sort_and_summarize():
    events = list(reversed(example_protocol_events()))
    ordered = validate_events(events)
    assert ordered[0].timestamp_s == 0.0
    assert session_duration(events) == 20.0
    assert inter_event_intervals(events) == [2.0, 3.0, 4.0, 5.0, 6.0]
    summary = summarize_event_log(events)
    assert summary.event_count == 6
    assert summary.actor_count == 2
    assert summary.temporal_mode == "synchronous"
    assert summary.turn_balance == 1.0


def test_temporal_classification_modes_are_thresholded():
    sync = [
        SessionEvent(0.0, "a", "stroke", "stylus"),
        SessionEvent(1.0, "b", "stroke", "stylus"),
    ]
    semi = [
        SessionEvent(0.0, "a", "stroke", "stylus"),
        SessionEvent(30.0, "b", "stroke", "stylus"),
    ]
    async_events = [
        SessionEvent(0.0, "a", "stroke", "stylus"),
        SessionEvent(600.0, "b", "stroke", "stylus"),
    ]
    assert classify_temporal_mode(sync) == "synchronous"
    assert classify_temporal_mode(semi) == "semisynchronous"
    assert classify_temporal_mode(async_events) == "asynchronous"


def test_turn_balance_and_invalid_events():
    events = [
        SessionEvent(0.0, "a", "stroke", "stylus"),
        SessionEvent(1.0, "a", "stroke", "stylus"),
        SessionEvent(2.0, "b", "stroke", "stylus"),
    ]
    assert turn_balance(events) == 0.5
    with pytest.raises(ValueError):
        validate_events([])
    with pytest.raises(ValueError):
        validate_events([SessionEvent(-1.0, "a", "stroke", "stylus")])
    with pytest.raises(ValueError):
        validate_events([SessionEvent(0.0, "  ", "stroke", "stylus")])
    with pytest.raises(ValueError):
        validate_events([SessionEvent(0.0, "a", "", "stylus")])
    with pytest.raises(ValueError):
        validate_events([SessionEvent(0.0, "a", "stroke", "  ")])
    with pytest.raises(ValueError):
        classify_temporal_mode(events, synchronous_threshold_s=10, asynchronous_threshold_s=5)


def test_turn_balance_ignores_non_partner_actors_when_specified():
    events = [
        SessionEvent(0.0, "partner_a", "stroke", "stylus"),
        SessionEvent(1.0, "partner_a", "stroke", "stylus"),
        SessionEvent(2.0, "ai_assist", "suggestion", "interface"),
        SessionEvent(3.0, "ai_assist", "suggestion", "interface"),
        SessionEvent(4.0, "ai_assist", "suggestion", "interface"),
    ]
    # Without partner_actors the AI dominates and balance is skewed.
    assert turn_balance(events) == 2.0 / 3.0
    # With partner_actors restricted to the human dyad, the AI is ignored and a
    # single human actor yields 0.0 (fewer than two dyad members present).
    assert turn_balance(events, partner_actors={"partner_a", "partner_b"}) == 0.0


def test_turn_balance_with_partner_actors_balances_human_dyad():
    events = [
        SessionEvent(0.0, "partner_a", "stroke", "stylus"),
        SessionEvent(1.0, "partner_a", "stroke", "stylus"),
        SessionEvent(2.0, "partner_b", "stroke", "stylus"),
        SessionEvent(3.0, "ai_assist", "suggestion", "interface"),
        SessionEvent(4.0, "ai_assist", "suggestion", "interface"),
    ]
    assert turn_balance(events, partner_actors={"partner_a", "partner_b"}) == 0.5
