"""Tests for Pydantic models in types.py."""

from __future__ import annotations

from gcal_fast_mcp.types import Attendee, CalendarInfo, Event, FreeBusySlot


class TestCalendarInfo:
    def test_minimal(self):
        cal = CalendarInfo(id="primary", summary="My Calendar")
        assert cal.id == "primary"
        assert cal.summary == "My Calendar"
        assert cal.description == ""
        assert cal.time_zone == ""
        assert cal.primary is False

    def test_full(self):
        cal = CalendarInfo(
            id="abc@group.calendar.google.com",
            summary="Work",
            description="Work calendar",
            time_zone="America/New_York",
            primary=True,
        )
        dumped = cal.model_dump(by_alias=True)
        assert dumped["timeZone"] == "America/New_York"
        assert dumped["primary"] is True

    def test_alias_construction(self):
        cal = CalendarInfo(id="x", summary="X", time_zone="US/Eastern")
        assert cal.time_zone == "US/Eastern"


class TestAttendee:
    def test_minimal(self):
        att = Attendee(email="user@example.com")
        assert att.email == "user@example.com"
        assert att.display_name == ""
        assert att.response_status == ""
        assert att.organizer is False

    def test_from_alias(self):
        att = Attendee(
            email="a@b.com",
            display_name="Alice",
            response_status="accepted",
        )
        assert att.display_name == "Alice"
        assert att.response_status == "accepted"


class TestEvent:
    def test_minimal(self):
        ev = Event(id="e1", start="2025-01-15T09:00:00Z", end="2025-01-15T10:00:00Z")
        assert ev.id == "e1"
        assert ev.summary == ""
        assert ev.all_day is False
        assert ev.attendees == []
        assert ev.recurring_event_id is None

    def test_full_roundtrip(self):
        ev = Event(
            id="e2",
            summary="Lunch",
            description="Team lunch",
            location="Cafe",
            start="2025-01-15T12:00:00Z",
            end="2025-01-15T13:00:00Z",
            all_day=False,
            status="confirmed",
            attendees=[Attendee(email="x@y.com", response_status="accepted")],
            hangout_link="https://meet.google.com/abc",
            html_link="https://calendar.google.com/event?eid=e2",
            creator_email="x@y.com",
            organizer_email="x@y.com",
            recurring_event_id="recur_1",
            calendar_id="primary",
        )
        dumped = ev.model_dump(by_alias=True)
        assert dumped["hangoutLink"] == "https://meet.google.com/abc"
        assert dumped["recurringEventId"] == "recur_1"
        assert len(dumped["attendees"]) == 1


class TestFreeBusySlot:
    def test_basic(self):
        slot = FreeBusySlot(start="2025-01-15T09:00:00Z", end="2025-01-15T10:00:00Z")
        assert slot.start == "2025-01-15T09:00:00Z"
        dumped = slot.model_dump()
        assert "start" in dumped and "end" in dumped
