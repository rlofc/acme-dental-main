"""Tool that can list appointments availability in Calendly"""

import json
from typing import Any

from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient


class ListCalendlyEventTypeAvailableTimesTool(BaseTool):
    name: str = "list_calendly_event_type_available_times"
    description: str = (
        "List available time slots for a Calendly event type. "
        "Input should be a JSON string with keys:\n"
        "  - 'event_type' (required): the event type URI or UUID\n"
        "  - 'start_time' (required): ISO8601 start time\n"
        "  - 'end_time' (required): ISO8601 end time\n"
        # "  - 'timezone' (optional): IANA timezone name\n"
        "  - any other supported query parameters will be passed through."
    )
    calendly_client: CalendlyClient

    def __init__(self, calendly_client: CalendlyClient, **data: Any) -> None:
        super().__init__(calendly_client=calendly_client, **data)

    def _run(self, input_str: str) -> list[dict[str, Any]]:
        try:
            payload = json.loads(input_str) if input_str else {}
        except json.JSONDecodeError:
            payload = {}

        event_type = payload.get("event_type")
        start_time = payload.get("start_time")
        end_time = payload.get("end_time")
        timezone = None  # payload.get("timezone")

        if not event_type or not start_time or not end_time:
            # Mirror the pattern of lightweight tools: fail fast and clearly.
            raise ValueError("Missing required fields: 'event_type', 'start_time', and 'end_time' are all required.")

        # Remove known keys so the rest can be passed through as extra query params
        extra_params = {
            k: v for k, v in payload.items() if k not in {"event_type", "start_time", "end_time", "timezone"}
        }

        return self.calendly_client.list_event_type_available_times(
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            **extra_params,
        )

    async def _arun(self, input_str: str) -> dict[str, Any]:
        raise NotImplementedError("Async not implemented")


class MockListCalendlyEventTypeAvailableTimesTool(ListCalendlyEventTypeAvailableTimesTool):
    def _run(self, input_str: str) -> list[dict[str, Any]]:
        return [
            {
                "event_type": "1",
                "event_name": "Dental",
                "start_time": "2030-01-01T10:00:00Z",
                "end_time": "2030-01-01T10:30:00Z",
            },
            {
                "event_type": "1",
                "event_name": "Dental",
                "start_time": "2030-01-01T10:30:00Z",
                "end_time": "2030-01-01T11:00:00Z",
            },
        ]
