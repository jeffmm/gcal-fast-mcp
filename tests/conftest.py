"""Shared test fixtures."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_calendar_service(monkeypatch):
    """Patch get_calendar_service to return a mock."""
    mock_svc = MagicMock()
    monkeypatch.setattr(
        "gcal_fast_mcp.calendar_service.get_calendar_service",
        lambda: mock_svc,
    )
    # Also patch in tool modules which import get_calendar_service
    monkeypatch.setattr(
        "gcal_fast_mcp.tools.event_ops.get_calendar_service",
        lambda: mock_svc,
    )
    monkeypatch.setattr(
        "gcal_fast_mcp.tools.calendar_ops.get_calendar_service",
        lambda: mock_svc,
    )
    monkeypatch.setattr(
        "gcal_fast_mcp.tools.freebusy_ops.get_calendar_service",
        lambda: mock_svc,
    )
    return mock_svc


@pytest.fixture
def sample_event_raw():
    """A raw Google Calendar API event dict."""
    return {
        "id": "evt_123",
        "summary": "Team standup",
        "description": "Daily sync",
        "location": "Conference Room A",
        "status": "confirmed",
        "start": {"dateTime": "2025-01-15T09:00:00-05:00"},
        "end": {"dateTime": "2025-01-15T09:30:00-05:00"},
        "attendees": [
            {
                "email": "alice@example.com",
                "displayName": "Alice",
                "responseStatus": "accepted",
                "organizer": True,
            },
            {
                "email": "bob@example.com",
                "displayName": "Bob",
                "responseStatus": "needsAction",
            },
        ],
        "hangoutLink": "https://meet.google.com/abc-defg-hij",
        "htmlLink": "https://calendar.google.com/event?eid=evt_123",
        "creator": {"email": "alice@example.com"},
        "organizer": {"email": "alice@example.com"},
    }


@pytest.fixture
def sample_allday_event_raw():
    """A raw all-day event dict."""
    return {
        "id": "evt_allday",
        "summary": "Company holiday",
        "status": "confirmed",
        "start": {"date": "2025-01-20"},
        "end": {"date": "2025-01-21"},
    }
