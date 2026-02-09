"""Tests for event operations tools."""

from __future__ import annotations

import json

from gcal_fast_mcp.tools.event_ops import (
    _parse_event,
    delete_event,
    get_event,
    list_events,
)


class TestParseEvent:
    def test_timed_event(self, sample_event_raw):
        event = _parse_event(sample_event_raw, "primary")
        assert event.id == "evt_123"
        assert event.summary == "Team standup"
        assert event.all_day is False
        assert event.start == "2025-01-15T09:00:00-05:00"
        assert event.end == "2025-01-15T09:30:00-05:00"
        assert event.location == "Conference Room A"
        assert event.hangout_link == "https://meet.google.com/abc-defg-hij"
        assert event.creator_email == "alice@example.com"
        assert event.calendar_id == "primary"
        assert len(event.attendees) == 2
        assert event.attendees[0].email == "alice@example.com"
        assert event.attendees[0].organizer is True
        assert event.attendees[1].response_status == "needsAction"

    def test_allday_event(self, sample_allday_event_raw):
        event = _parse_event(sample_allday_event_raw)
        assert event.all_day is True
        assert event.start == "2025-01-20"
        assert event.end == "2025-01-21"
        assert event.summary == "Company holiday"
        assert event.attendees == []

    def test_empty_event(self):
        raw = {"id": "empty", "start": {}, "end": {}}
        event = _parse_event(raw)
        assert event.id == "empty"
        assert event.start == ""
        assert event.end == ""
        assert event.summary == ""

    def test_serialization(self, sample_event_raw):
        event = _parse_event(sample_event_raw, "primary")
        dumped = json.dumps(event.model_dump(by_alias=True))
        parsed = json.loads(dumped)
        assert parsed["id"] == "evt_123"
        assert parsed["hangoutLink"] == "https://meet.google.com/abc-defg-hij"
        assert len(parsed["attendees"]) == 2


class TestListEvents:
    def test_list_events_returns_json(self, mock_calendar_service, sample_event_raw):
        mock_calendar_service.events().list().execute.return_value = {"items": [sample_event_raw]}

        result = list_events.fn(calendar_id="primary")
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "evt_123"

    def test_list_events_empty(self, mock_calendar_service):
        mock_calendar_service.events().list().execute.return_value = {"items": []}

        result = list_events.fn(calendar_id="primary")
        assert json.loads(result) == []


class TestGetEvent:
    def test_get_event(self, mock_calendar_service, sample_event_raw):
        mock_calendar_service.events().get().execute.return_value = sample_event_raw

        result = get_event.fn(event_id="evt_123", calendar_id="primary")
        data = json.loads(result)
        assert data["id"] == "evt_123"
        assert data["summary"] == "Team standup"


class TestDeleteEvent:
    def test_delete_event(self, mock_calendar_service):
        mock_calendar_service.events().delete().execute.return_value = None

        result = delete_event.fn(event_id="evt_123", calendar_id="primary")
        assert "evt_123" in result
        assert "deleted" in result.lower()
