# gcal-fast-mcp

Google Calendar MCP server built with [FastMCP](https://github.com/jlowin/fastmcp). Provides 10 tools for calendar management, event CRUD, and availability queries via the Google Calendar API v3.

## Setup

### 1. Google OAuth Credentials

Place your Google Cloud OAuth client credentials at `~/.gcal-mcp/gcp-oauth.keys.json` (or in the project directory — they'll be copied automatically).

If you already have a GCP project configured for another Google API (e.g. gmail-fast-mcp), you can reuse the same OAuth client — just enable the Google Calendar API in that project.

### 2. Authenticate

```bash
uv run python -m gcal_fast_mcp auth
```

This opens a browser for the OAuth flow and saves tokens to `~/.gcal-mcp/credentials.json`.

For cloud environments with a custom callback URL:

```bash
uv run python -m gcal_fast_mcp auth https://your-domain.com/oauth2callback
```

### 3. Run the Server

```bash
uv run python -m gcal_fast_mcp
```

### MCP Client Configuration

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "uv",
      "args": ["--directory", "/path/to/gcal-fast-mcp", "run", "google-calendar-fast-mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `list_calendars` | List all calendars the user has access to |
| `get_calendar` | Get details of a specific calendar |
| `list_events` | List events within a time range (supports search, recurring expansion) |
| `get_event` | Get full details of a single event |
| `create_event` | Create a new event with attendees, location, etc. |
| `update_event` | Update an existing event (partial updates supported) |
| `delete_event` | Delete an event |
| `quick_add` | Create an event from natural language (e.g. "Lunch tomorrow at noon") |
| `check_availability` | Check free/busy status for one or more calendars |

## Configuration

Environment variables (prefix `GCAL_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GCAL_OAUTH_PATH` | `~/.gcal-mcp/gcp-oauth.keys.json` | OAuth client secrets file |
| `GCAL_CREDENTIALS_PATH` | `~/.gcal-mcp/credentials.json` | Saved OAuth tokens |
| `GCAL_DEFAULT_CALENDAR` | `primary` | Default calendar ID |
| `GCAL_MAX_RESULTS` | `50` | Default max events returned |

## Google Calendar API Scopes

- `calendar` — Full calendar access
- `calendar.events` — Event CRUD operations
