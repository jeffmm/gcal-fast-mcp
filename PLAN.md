# Google Calendar Fast MCP Server — Build Plan

## Overview

A Google Calendar MCP server for Claude Code, following the same patterns as the sibling
`gmail-fast-mcp`, `slack-fast-mcp`, and `granola-fast-mcp` servers. Provides read/write
access to Google Calendar via the Google Calendar API v3.

**Use the `/create-mcp-server` and `/python-projects` skills when building this.**

## Project Structure

```
google-calendar-fast-mcp/
├── pyproject.toml              # ✅ Done
├── .python-version             # ✅ Done (3.13)
├── PLAN.md                     # ✅ This file
├── src/
│   └── google_calendar_fast_mcp/
│       ├── __init__.py         # ✅ Done
│       ├── __main__.py         # Entry point: calls mcp.run()
│       ├── server.py           # FastMCP instance + lifespan + tool imports
│       ├── config.py           # Pydantic Settings config
│       ├── types.py            # Pydantic models for Calendar/Event data
│       ├── auth.py             # OAuth 2.0 flow (browser-based, like gmail-fast-mcp)
│       ├── calendar_service.py # Google Calendar API client (lazy singleton w/ token refresh)
│       └── tools/
│           ├── __init__.py     # ✅ Done
│           ├── calendar_ops.py # List/get calendars
│           ├── event_ops.py    # List/get/create/update/delete events
│           └── freebusy_ops.py # Free/busy queries
└── tests/
    ├── __init__.py             # ✅ Done
    ├── test_event_ops.py
    └── test_types.py
```

## Authentication

Follow the exact same pattern as `gmail-fast-mcp/auth.py`:

### OAuth Config
- Config directory: `~/.google-calendar-mcp/`
- OAuth keys file: `~/.google-calendar-mcp/gcp-oauth.keys.json`
- Credentials file: `~/.google-calendar-mcp/credentials.json`
- Both paths overridable via env vars: `GCAL_OAUTH_PATH`, `GCAL_CREDENTIALS_PATH`

### Scopes
```python
SCOPES = [
    "https://www.googleapis.com/auth/calendar",          # Full calendar access
    "https://www.googleapis.com/auth/calendar.events",    # Event CRUD
]
```

### Auth Flow
1. User downloads OAuth client credentials JSON from Google Cloud Console
2. Places it at `~/.google-calendar-mcp/gcp-oauth.keys.json` (or in project root as `gcp-oauth.keys.json`)
3. Runs: `uv run python -m google_calendar_fast_mcp auth`
4. Browser opens, user authorizes, tokens saved to `credentials.json`
5. Tokens auto-refresh on expiry (same as gmail-fast-mcp)

### Google Cloud Setup (document in README)
1. Go to https://console.cloud.google.com
2. Create project (or reuse the one from gmail-fast-mcp)
3. Enable "Google Calendar API"
4. Create OAuth 2.0 credentials → Desktop Application
5. Download the JSON file

**Important:** The user likely already has a GCP project with OAuth configured for gmail-fast-mcp.
They can reuse the same project — just enable the Calendar API and download the same (or new)
OAuth client credentials. The scopes will be different so a new auth flow is needed.

## Service Layer (`calendar_service.py`)

Follow gmail-fast-mcp's `gmail_service.py` pattern:

```python
# Lazy singleton, auto-refreshing credentials
_service = None

def get_calendar_service():
    global _service
    if _service is not None:
        return _service
    # Load credentials, refresh if expired, build service
    _service = build("calendar", "v3", credentials=creds)
    return _service
```

## Config (`config.py`)

Use pydantic-settings like granola-fast-mcp:

```python
class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GCAL_")

    oauth_path: str = "~/.google-calendar-mcp/gcp-oauth.keys.json"
    credentials_path: str = "~/.google-calendar-mcp/credentials.json"
    default_calendar: str = "primary"  # Which calendar to query by default
    max_results: int = 50              # Default max events to return
```

## Tools to Implement

### 1. `calendar_ops.py` — Calendar Management

#### `list_calendars`
- List all calendars the user has access to
- Returns: id, summary, description, timeZone, primary flag
- Read-only

#### `get_calendar`
- Get details of a specific calendar by ID
- Read-only

### 2. `event_ops.py` — Event CRUD (most important)

#### `list_events` (PRIMARY TOOL for daily briefing)
- List events from a calendar within a time range
- Parameters:
  - `calendar_id: str = "primary"`
  - `time_min: str` — ISO 8601 datetime (default: start of today)
  - `time_max: str` — ISO 8601 datetime (default: end of today)
  - `max_results: int = 50`
  - `query: str | None = None` — Free-text search
  - `single_events: bool = True` — Expand recurring events
  - `order_by: str = "startTime"` — Sort order
- Returns: event summary, start/end time, location, attendees, description, hangout/meet link, status
- Read-only
- **This is the most critical tool for the daily briefing workflow**

#### `get_event`
- Get full details of a single event by ID
- Returns all event fields including full attendee list, attachments, reminders
- Read-only

#### `create_event`
- Create a new calendar event
- Parameters:
  - `summary: str` — Event title
  - `start: str` — ISO 8601 datetime
  - `end: str` — ISO 8601 datetime
  - `description: str | None`
  - `location: str | None`
  - `attendees: list[str] | None` — Email addresses
  - `calendar_id: str = "primary"`
- Returns: created event details

#### `update_event`
- Update an existing event
- Parameters: event_id + any fields to change
- Returns: updated event details

#### `delete_event`
- Delete an event by ID
- Parameters: event_id, calendar_id
- Returns: confirmation

#### `quick_add`
- Create event from natural language string (uses Google's NLP)
- Parameters: `text: str` (e.g., "Lunch with Sarah tomorrow at noon")
- Uses `events().quickAdd()` API
- Returns: created event details

### 3. `freebusy_ops.py` — Availability

#### `check_availability`
- Check free/busy status for one or more calendars
- Parameters:
  - `time_min: str` — Start of window
  - `time_max: str` — End of window
  - `calendars: list[str] = ["primary"]` — Calendar IDs to check
- Returns: busy time ranges
- Read-only
- **Useful for the daily briefing to show open time slots**

## Pydantic Types (`types.py`)

```python
class CalendarInfo(BaseModel):
    id: str
    summary: str
    description: str = ""
    time_zone: str = ""
    primary: bool = False

class Attendee(BaseModel):
    email: str
    display_name: str = ""
    response_status: str = ""  # needsAction, declined, tentative, accepted
    organizer: bool = False

class Event(BaseModel):
    id: str
    summary: str = ""
    description: str = ""
    location: str = ""
    start: str  # ISO 8601
    end: str    # ISO 8601
    all_day: bool = False
    status: str = ""  # confirmed, tentative, cancelled
    attendees: list[Attendee] = []
    hangout_link: str = ""
    html_link: str = ""
    creator_email: str = ""
    organizer_email: str = ""
    recurring_event_id: str | None = None
    calendar_id: str = ""

class FreeBusySlot(BaseModel):
    start: str
    end: str
```

## Server Setup (`server.py`)

Simple, synchronous — matching gmail-fast-mcp pattern (no lifespan needed since we use
a lazy singleton for the service):

```python
from fastmcp import FastMCP

mcp = FastMCP("Google Calendar")

from google_calendar_fast_mcp.tools import calendar_ops, event_ops, freebusy_ops
```

## Entry Point (`__main__.py`)

```python
import sys
from google_calendar_fast_mcp.auth import authenticate

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        redirect_uri = sys.argv[2] if len(sys.argv) > 2 else None
        authenticate(redirect_uri)
        return

    from google_calendar_fast_mcp.server import mcp
    mcp.run()

if __name__ == "__main__":
    main()
```

## Claude Code Configuration

Once built, add to `~/.claude.json` under `mcpServers`:

```json
"google-calendar": {
    "command": "uv",
    "args": [
        "--directory",
        "/Users/jeff/Projects/google-calendar-fast-mcp",
        "run",
        "google-calendar-fast-mcp"
    ]
}
```

## Tool Annotations

All read-only tools should have:
```python
_READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}
```

Write tools (create, update, delete) should have:
```python
_WRITE = {
    "readOnlyHint": False,
    "destructiveHint": False,  # True for delete_event
    "idempotentHint": False,
    "openWorldHint": False,
}
```

## Implementation Order

1. `auth.py` + `calendar_service.py` — Get auth working first
2. `config.py` + `types.py` — Data models
3. `server.py` + `__main__.py` — Server skeleton
4. `tools/event_ops.py` — `list_events` and `get_event` (most important for daily briefing)
5. `tools/calendar_ops.py` — `list_calendars`, `get_calendar`
6. `tools/freebusy_ops.py` — `check_availability`
7. `tools/event_ops.py` — `create_event`, `update_event`, `delete_event`, `quick_add`
8. Tests
9. README with setup instructions

## Key Reference Files

Study these files from sibling projects before implementing:

- **Auth pattern:** `/Users/jeff/Projects/gmail-fast-mcp/src/gmail_fast_mcp/auth.py`
- **Service singleton:** `/Users/jeff/Projects/gmail-fast-mcp/src/gmail_fast_mcp/gmail_service.py`
- **Tool registration:** `/Users/jeff/Projects/gmail-fast-mcp/src/gmail_fast_mcp/tools/email_ops.py`
- **Config pattern:** `/Users/jeff/Projects/granola-fast-mcp/src/granola_fast_mcp/config.py`
- **Types pattern:** `/Users/jeff/Projects/slack-fast-mcp/src/slack_fast_mcp/types.py`
- **Server setup:** `/Users/jeff/Projects/granola-fast-mcp/src/granola_fast_mcp/server.py`
