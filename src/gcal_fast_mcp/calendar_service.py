"""Lazy singleton for the authenticated Google Calendar API service."""

from __future__ import annotations

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from .config import Config

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

_config = Config()
CONFIG_DIR = Path(_config.credentials_path).parent
OAUTH_PATH = Path(_config.oauth_path)
CREDENTIALS_PATH = Path(_config.credentials_path)

_service = None


def get_calendar_service():
    """Return a cached Calendar API service, creating it on first call."""
    global _service
    if _service is not None:
        return _service

    if not CREDENTIALS_PATH.exists():
        raise RuntimeError(
            f"No credentials found at {CREDENTIALS_PATH}. "
            "Run 'uv run python -m gcal_fast_mcp auth' first."
        )

    token_data = json.loads(CREDENTIALS_PATH.read_text())

    # Merge client_id/client_secret from OAuth keys if missing in token
    if "client_id" not in token_data and OAUTH_PATH.exists():
        oauth_keys = json.loads(OAUTH_PATH.read_text())
        client_info = oauth_keys.get("installed") or oauth_keys.get("web", {})
        token_data["client_id"] = client_info.get("client_id", "")
        token_data["client_secret"] = client_info.get("client_secret", "")

    creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        CREDENTIALS_PATH.write_text(creds.to_json())

    from googleapiclient.discovery import build

    _service = build("calendar", "v3", credentials=creds)
    return _service
