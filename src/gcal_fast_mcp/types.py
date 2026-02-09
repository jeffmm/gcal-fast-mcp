"""Pydantic models for Google Calendar API responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CalendarInfo(BaseModel):
    id: str = Field(description="Calendar identifier")
    summary: str = Field(description="Calendar title")
    description: str = Field(default="", description="Calendar description")
    time_zone: str = Field(default="", alias="timeZone", description="IANA time zone")
    primary: bool = Field(default=False, description="Whether this is the primary calendar")

    model_config = {"populate_by_name": True}


class Attendee(BaseModel):
    email: str = Field(description="Attendee email address")
    display_name: str = Field(default="", alias="displayName", description="Attendee display name")
    response_status: str = Field(
        default="",
        alias="responseStatus",
        description="RSVP status: needsAction, declined, tentative, accepted",
    )
    organizer: bool = Field(default=False, description="Whether this attendee is the organizer")

    model_config = {"populate_by_name": True}


class Event(BaseModel):
    id: str = Field(description="Event identifier")
    summary: str = Field(default="", description="Event title")
    description: str = Field(default="", description="Event description")
    location: str = Field(default="", description="Event location")
    start: str = Field(description="Start time (ISO 8601)")
    end: str = Field(description="End time (ISO 8601)")
    all_day: bool = Field(default=False, description="Whether this is an all-day event")
    status: str = Field(default="", description="Event status: confirmed, tentative, cancelled")
    attendees: list[Attendee] = Field(default_factory=list, description="Event attendees")
    hangout_link: str = Field(
        default="", alias="hangoutLink", description="Google Meet / Hangout link"
    )
    html_link: str = Field(
        default="", alias="htmlLink", description="Link to the event in Google Calendar"
    )
    creator_email: str = Field(default="", description="Email of the event creator")
    organizer_email: str = Field(default="", description="Email of the event organizer")
    recurring_event_id: str | None = Field(
        default=None, alias="recurringEventId", description="ID of the recurring event series"
    )
    calendar_id: str = Field(default="", description="Calendar this event belongs to")

    model_config = {"populate_by_name": True}


class FreeBusySlot(BaseModel):
    start: str = Field(description="Busy period start (ISO 8601)")
    end: str = Field(description="Busy period end (ISO 8601)")
