"""Agent tools module"""
from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient
from src.tools.availability import ListCalendlyEventTypeAvailableTimesTool, MockListCalendlyEventTypeAvailableTimesTool
from src.tools.cancel import CancelCalendlyEventTool
from src.tools.event_invitees import ListCalendlyEventInviteesTool, MockListCalendlyEventInviteesTool
from src.tools.event_types import ListCalendlyEventTypesTool, MockListCalendlyEventTypesTool
from src.tools.invitee import CreateCalendlyInviteeTool
from src.tools.kb import CheckWhatOtherQuestionsCanWeAnswer, GetReadyAnswerToQuestions
from src.tools.scheduled import ListCalendlyScheduledEventsTool, MockListCalendlyScheduledEventsTool
from src.tools.user import GetCalendlyUserTool, MockGetCalendlyUserTool


def build_tools_dict(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        GetCalendlyUserTool,
        ListCalendlyEventTypesTool,
        ListCalendlyScheduledEventsTool,
        ListCalendlyEventInviteesTool,
        ListCalendlyEventTypeAvailableTimesTool,
        CreateCalendlyInviteeTool,
        CancelCalendlyEventTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    for cls in [
        CheckWhatOtherQuestionsCanWeAnswer,
        GetReadyAnswerToQuestions,
    ]:
        instance = cls()
        tools[instance.name] = instance
    return tools


def build_testing_tools_dict(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        MockGetCalendlyUserTool,
        MockListCalendlyScheduledEventsTool,
        MockListCalendlyEventInviteesTool,
        MockListCalendlyEventTypeAvailableTimesTool,
        MockListCalendlyEventTypesTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools
