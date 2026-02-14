"""Tool that can obtain the main user context in Calendly"""
from typing import Any

from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient


class GetCalendlyUserTool(BaseTool):
    name: str = "get_calendly_current_user"
    description: str = (
        "Get the current Calendly user profile, including their URI which is "
        "often needed to filter other Calendly queries."
    )

    calendly_client: CalendlyClient

    def __init__(self, calendly_client: CalendlyClient, **data: Any) -> None:
        super().__init__(calendly_client=calendly_client, **data)

    def _run(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self.calendly_client.get_current_user()

    async def _arun(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Async not implemented")


class MockGetCalendlyUserTool(GetCalendlyUserTool):
    def _run(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "user": "xyz",
            "organization": "xyz",
        }
