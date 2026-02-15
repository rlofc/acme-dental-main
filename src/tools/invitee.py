#!/usr/bin/env python3
from typing import Any

from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient


class CreateCalendlyInviteeTool(BaseTool):
    name: str = "create_calendly_invitee"
    description: str = (
        "Create (book) an invitee for a specific Calendly event type. event_type must be known \n"
        "and can be obtained using a tool given an an appointment type by the user or the default \n"
        "appointment type 'Dental Check Up' if none was given. \n"
        "Input should be a JSON string with keys:\n"
        "  - 'event_type' (required): event type URI or UUID\n"
        "  - 'start_time' (required): ISO8601 datetime string in UTC\n"
        "  - 'invitee' (required): object with invitee details, e.g.:\n"
        "      { 'name': 'John Smith', 'email': 'test@example.com', 'timezone': 'America/New_York', ... }"
        "  - 'location' (required): object with location kind and location location, e.g.:\n"
        "      { 'kind': 'physical', 'location': 'Acme Dental Lane' }"
    )
    calendly_client: CalendlyClient

    def __init__(self, calendly_client: CalendlyClient, **data: Any) -> None:
        super().__init__(calendly_client=calendly_client, **data)

    def _run(self, input_str: str) -> dict[str, Any]:
        import json

        try:
            payload = json.loads(input_str) if input_str else {}
        except json.JSONDecodeError:
            payload = {}

        event_type = payload.get("event_type")
        start_time = payload.get("start_time")
        invitee = payload.get("invitee")
        location = payload.get("location")

        if not event_type or not start_time or not invitee:
            raise ValueError(
                "Missing required fields: 'event_type', 'start_time', 'invitee', and 'location' are all required."
            )

        return self.calendly_client.create_invitee(
            event_type=event_type,
            start_time=start_time,
            invitee=invitee,
            location=location,
        )

    async def _arun(self, input_str: str) -> dict[str, Any]:
        raise NotImplementedError("Async not implemented")


class MockCreateCalendlyInviteeTool(CreateCalendlyInviteeTool):
    def _run(self, input_str: str) -> dict[str, Any]:
        return {"status": "Appointment scheduled"}
