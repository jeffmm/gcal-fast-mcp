"""Free/busy operations: check availability."""

from __future__ import annotations

import json
from typing import Annotated

from gcal_fast_mcp.calendar_service import get_calendar_service
from gcal_fast_mcp.server import mcp
from gcal_fast_mcp.types import FreeBusySlot

_READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}


@mcp.tool(annotations=_READ_ONLY)
def check_availability(
    time_min: Annotated[str, "Start of availability window (ISO 8601)."],
    time_max: Annotated[str, "End of availability window (ISO 8601)."],
    calendars: Annotated[
        list[str] | None, "Calendar IDs to check. Defaults to ['primary']."
    ] = None,
) -> str:
    """Check free/busy status for one or more calendars. Returns busy time ranges per calendar."""
    service = get_calendar_service()
    calendar_ids = calendars or ["primary"]

    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": cal_id} for cal_id in calendar_ids],
    }

    result = service.freebusy().query(body=body).execute()
    calendars_busy = result.get("calendars", {})

    output: dict[str, list[dict]] = {}
    for cal_id, info in calendars_busy.items():
        slots = [
            FreeBusySlot(start=slot["start"], end=slot["end"]).model_dump()
            for slot in info.get("busy", [])
        ]
        output[cal_id] = slots

    return json.dumps(output, ensure_ascii=False)
