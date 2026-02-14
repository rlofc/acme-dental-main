"""Tool that can cancel a scheduled event in Calendly"""
import json
from typing import Any

from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient


class CancelCalendlyEventTool(BaseTool):
    name: str = "cancel_calendly_event"
    description: str = (
        "Cancels (deletes) an invitee event. "
        "Input should be a JSON string with keys:\n"
        "  - 'event_uuid' (required): event UUID obtained from previously listed appointments for the invitee."
    )
    calendly_client: CalendlyClient

    def __init__(self, calendly_client: CalendlyClient, **data: Any) -> None:
        super().__init__(calendly_client=calendly_client, **data)

    def _run(self, input_str: str) -> dict[str, Any]:
        try:
            payload = json.loads(input_str) if input_str else {}
        except json.JSONDecodeError:
            payload = {}

        event_uuid = payload.get("event_uuid")

        if not event_uuid:
            raise ValueError("Missing required fields: 'event_uuid' is required.")

        return self.calendly_client.cancel_event(
            event_uuid=event_uuid,
        )

    async def _arun(self, input_str: str) -> dict[str, Any]:
        raise NotImplementedError("Async not implemented")
