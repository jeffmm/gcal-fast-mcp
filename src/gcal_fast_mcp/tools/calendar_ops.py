"""Calendar operations: list and get calendars."""

from __future__ import annotations

import json
from typing import Annotated

from gcal_fast_mcp.calendar_service import get_calendar_service
from gcal_fast_mcp.server import mcp
from gcal_fast_mcp.types import CalendarInfo

_READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}


@mcp.tool(annotations=_READ_ONLY)
def list_calendars() -> str:
    """List all calendars the user has access to. Returns JSON array."""
    service = get_calendar_service()
    result = service.calendarList().list().execute()
    items = result.get("items", [])

    calendars = [
        CalendarInfo(
            id=cal.get("id", ""),
            summary=cal.get("summary", ""),
            description=cal.get("description", ""),
            time_zone=cal.get("timeZone", ""),
            primary=cal.get("primary", False),
        )
        for cal in items
    ]

    return json.dumps(
        [c.model_dump(by_alias=True) for c in calendars],
        ensure_ascii=False,
    )


@mcp.tool(annotations=_READ_ONLY)
def get_calendar(
    calendar_id: Annotated[str, "Calendar ID to retrieve."] = "primary",
) -> str:
    """Get details of a specific calendar."""
    service = get_calendar_service()
    cal = service.calendarList().get(calendarId=calendar_id).execute()

    info = CalendarInfo(
        id=cal.get("id", ""),
        summary=cal.get("summary", ""),
        description=cal.get("description", ""),
        time_zone=cal.get("timeZone", ""),
        primary=cal.get("primary", False),
    )

    return json.dumps(info.model_dump(by_alias=True), ensure_ascii=False)
