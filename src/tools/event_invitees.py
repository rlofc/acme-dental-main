"""Tool that can list event invitees in Calendly"""
from typing import Any

from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient


class ListCalendlyEventInviteesTool(BaseTool):
    name: str = "list_calendly_event_invitees"
    description: str = "List invitees for a specific Calendly scheduled event. Input must be the event URI string."
    calendly_client: CalendlyClient

    def __init__(self, calendly_client: CalendlyClient, **data: Any) -> None:
        super().__init__(calendly_client=calendly_client, **data)

    def _run(self, event_uri: str) -> list[dict[str, Any]]:
        return self.calendly_client.list_event_invitees(event_uri)

    async def _arun(self, event_uri: str) -> Any:
        raise NotImplementedError("Async not implemented")


class MockListCalendlyEventInviteesTool(ListCalendlyEventInviteesTool):
    def _run(self, event_uri: str) -> list[dict[str, Any]]:
        return [
            {
                "uri": "https://api.calendly.com/scheduled_events/ABC123",
                "email": "test@foo.com",
                "name": "Test Test",
                "status": "active",
            }
        ]
