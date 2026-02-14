"""Tool that can list event types in Calendly"""
import json
from typing import Any

from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient


class ListCalendlyEventTypesTool(BaseTool):
    name: str = "list_calendly_event_types"
    description: str = (
        "List Calendly event types for a user or organization. "
        "Input should be a JSON string with mandatory keys 'user' and 'organization' "
        "containing their URIs."
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
        return self.calendly_client.list_event_types(organization=org, user=user)

    async def _arun(self, input_str: str) -> dict[str, Any]:
        raise NotImplementedError("Async not implemented")


class MockListCalendlyEventTypesTool(ListCalendlyEventTypesTool):
    def _run(self, input_str: str) -> list[dict[str, Any]]:
        return [
            {
                "event_type": "1",
                "event_name": "Dental",
            }
        ]
