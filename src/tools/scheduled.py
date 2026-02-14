"""Tool that lists scheduled events in Calendly"""
import json
from typing import Any

from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient


class ListCalendlyScheduledEventsTool(BaseTool):
    name: str = "list_calendly_scheduled_events"
    description: str = (
        "List Calendly scheduled events. Event specifics should only be shared with their invitees.\n"
        "Invitees can be obtained using a separate tool. Input should be a JSON string with keys:\n"
        "- 'user': user URI\n"
        "- 'organization': organization URI\n"
    )
    calendly_client: CalendlyClient

    def __init__(self, calendly_client: CalendlyClient, **data: Any) -> None:
        super().__init__(calendly_client=calendly_client, **data)

    def _run(self, input_str: str) -> list[dict[str, Any]]:
        try:
            data = json.loads(input_str) if input_str else {}
        except json.JSONDecodeError:
            data = {}

        user = data.get("user")
        org = data.get("organization")
        return self.calendly_client.list_scheduled_events(
            user=user,
            organization=org,
            count=20,
            status="active",
        )

    async def _arun(self, input_str: str) -> Any:
        raise NotImplementedError("Async not implemented")


class MockListCalendlyScheduledEventsTool(ListCalendlyScheduledEventsTool):
    def _run(self, input_str: str) -> list[dict[str, Any]]:
        return [
            {
                "uri": "https://api.calendly.com/scheduled_events/ABC123",
                "event_name": "Dental",
                "status": "active",
                "start_time": "2026-02-14T10:00:00Z",
                "end_time": "2026-02-14T10:30:00Z",
                "location": {"type": "zoom", "join_url": "https://zoom.example/mock"},
                "created_at": "2026-02-01T09:00:00Z",
                "updated_at": "2026-02-01T09:00:00Z",
            }
        ]
