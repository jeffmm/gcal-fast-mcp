"""Event operations: list, get, create, update, delete, quick_add."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated

from gcal_fast_mcp.calendar_service import get_calendar_service
from gcal_fast_mcp.server import mcp
from gcal_fast_mcp.types import Attendee, Event

_READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}

_WRITE = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
}

_DELETE = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,
    "openWorldHint": False,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_event(raw: dict, calendar_id: str = "") -> Event:
    """Convert a raw Google Calendar API event dict into an Event model."""
    start_info = raw.get("start", {})
    end_info = raw.get("end", {})

    # All-day events use "date", timed events use "dateTime"
    all_day = "date" in start_info and "dateTime" not in start_info
    start = start_info.get("dateTime") or start_info.get("date", "")
    end = end_info.get("dateTime") or end_info.get("date", "")

    attendees = [
        Attendee(
            email=a.get("email", ""),
            display_name=a.get("displayName", ""),
            response_status=a.get("responseStatus", ""),
            organizer=a.get("organizer", False),
        )
        for a in raw.get("attendees", [])
    ]

    return Event(
        id=raw.get("id", ""),
        summary=raw.get("summary", ""),
        description=raw.get("description", ""),
        location=raw.get("location", ""),
        start=start,
        end=end,
        all_day=all_day,
        status=raw.get("status", ""),
        attendees=attendees,
        hangout_link=raw.get("hangoutLink", ""),
        html_link=raw.get("htmlLink", ""),
        creator_email=raw.get("creator", {}).get("email", ""),
        organizer_email=raw.get("organizer", {}).get("email", ""),
        recurring_event_id=raw.get("recurringEventId"),
        calendar_id=calendar_id,
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READ_ONLY)
def list_events(
    calendar_id: Annotated[str, "Calendar ID to query. Defaults to primary."] = "primary",
    time_min: Annotated[
        str, "Start of time range (ISO 8601). Defaults to start of today in UTC."
    ] = "",
    time_max: Annotated[str, "End of time range (ISO 8601). Defaults to end of today in UTC."] = "",
    max_results: Annotated[int, "Maximum number of events to return (1-2500)."] = 50,
    query: Annotated[str, "Free-text search terms to filter events."] = "",
    single_events: Annotated[bool, "Expand recurring events into individual instances."] = True,
    order_by: Annotated[
        str,
        "Sort order: 'startTime' (requires singleEvents=true) or 'updated'.",
    ] = "startTime",
) -> str:
    """List calendar events within a time range. Returns JSON array of events."""
    service = get_calendar_service()

    if not time_min:
        now = datetime.now(timezone.utc)
        time_min = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    if not time_max:
        now = datetime.now(timezone.utc)
        time_max = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

    kwargs: dict = {
        "calendarId": calendar_id,
        "timeMin": time_min,
        "timeMax": time_max,
        "maxResults": max_results,
        "singleEvents": single_events,
        "orderBy": order_by,
    }
    if query:
        kwargs["q"] = query

    result = service.events().list(**kwargs).execute()
    items = result.get("items", [])
    events = [_parse_event(e, calendar_id) for e in items]

    return json.dumps(
        [e.model_dump(by_alias=True) for e in events],
        ensure_ascii=False,
    )


@mcp.tool(annotations=_READ_ONLY)
def get_event(
    event_id: Annotated[str, "The event ID to retrieve."],
    calendar_id: Annotated[str, "Calendar ID. Defaults to primary."] = "primary",
) -> str:
    """Get full details of a single calendar event."""
    service = get_calendar_service()
    raw = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    event = _parse_event(raw, calendar_id)
    return json.dumps(event.model_dump(by_alias=True), ensure_ascii=False)


@mcp.tool(annotations=_WRITE)
def create_event(
    summary: Annotated[str, "Event title."],
    start: Annotated[str, "Start time in ISO 8601 format (e.g. 2025-01-15T09:00:00-05:00)."],
    end: Annotated[str, "End time in ISO 8601 format."],
    description: Annotated[str, "Event description."] = "",
    location: Annotated[str, "Event location."] = "",
    attendees: Annotated[list[str] | None, "List of attendee email addresses."] = None,
    calendar_id: Annotated[str, "Calendar ID. Defaults to primary."] = "primary",
) -> str:
    """Create a new calendar event."""
    service = get_calendar_service()

    body: dict = {
        "summary": summary,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
    }
    if description:
        body["description"] = description
    if location:
        body["location"] = location
    if attendees:
        body["attendees"] = [{"email": email} for email in attendees]

    raw = service.events().insert(calendarId=calendar_id, body=body).execute()
    event = _parse_event(raw, calendar_id)
    return json.dumps(event.model_dump(by_alias=True), ensure_ascii=False)


@mcp.tool(annotations=_WRITE)
def update_event(
    event_id: Annotated[str, "The event ID to update."],
    summary: Annotated[str | None, "New event title."] = None,
    start: Annotated[str | None, "New start time (ISO 8601)."] = None,
    end: Annotated[str | None, "New end time (ISO 8601)."] = None,
    description: Annotated[str | None, "New event description."] = None,
    location: Annotated[str | None, "New event location."] = None,
    attendees: Annotated[list[str] | None, "New list of attendee email addresses."] = None,
    calendar_id: Annotated[str, "Calendar ID. Defaults to primary."] = "primary",
) -> str:
    """Update an existing calendar event. Only provided fields are changed."""
    service = get_calendar_service()

    # Fetch current event to merge changes
    existing = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

    if summary is not None:
        existing["summary"] = summary
    if start is not None:
        existing["start"] = {"dateTime": start}
    if end is not None:
        existing["end"] = {"dateTime": end}
    if description is not None:
        existing["description"] = description
    if location is not None:
        existing["location"] = location
    if attendees is not None:
        existing["attendees"] = [{"email": email} for email in attendees]

    raw = service.events().update(calendarId=calendar_id, eventId=event_id, body=existing).execute()
    event = _parse_event(raw, calendar_id)
    return json.dumps(event.model_dump(by_alias=True), ensure_ascii=False)


@mcp.tool(annotations=_DELETE)
def delete_event(
    event_id: Annotated[str, "The event ID to delete."],
    calendar_id: Annotated[str, "Calendar ID. Defaults to primary."] = "primary",
) -> str:
    """Delete a calendar event."""
    service = get_calendar_service()
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return f"Event {event_id} deleted successfully."


@mcp.tool(annotations=_WRITE)
def quick_add(
    text: Annotated[
        str,
        "Natural language event description (e.g. 'Lunch with Sarah tomorrow at noon').",
    ],
    calendar_id: Annotated[str, "Calendar ID. Defaults to primary."] = "primary",
) -> str:
    """Create an event from a natural language string using Google's NLP parser."""
    service = get_calendar_service()
    raw = service.events().quickAdd(calendarId=calendar_id, text=text).execute()
    event = _parse_event(raw, calendar_id)
    return json.dumps(event.model_dump(by_alias=True), ensure_ascii=False)
