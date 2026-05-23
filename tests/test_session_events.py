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
        classify_temporal_mode(events, synchronous_threshold_s=10, asynchronous_threshold_s=5)
