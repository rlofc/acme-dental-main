"""Agent tools module"""

from langchain.tools import BaseTool

from src.api.calendly import CalendlyClient
from src.tools.availability import ListCalendlyEventTypeAvailableTimesTool, MockListCalendlyEventTypeAvailableTimesTool
from src.tools.cancel import CancelCalendlyEventTool, MockCancelCalendlyEventTool
from src.tools.event_invitees import ListCalendlyEventInviteesTool, MockListCalendlyEventInviteesTool
from src.tools.event_types import ListCalendlyEventTypesTool, MockListCalendlyEventTypesTool
from src.tools.invitee import CreateCalendlyInviteeTool, MockCreateCalendlyInviteeTool
from src.tools.kb import CheckWhatOtherQuestionsCanWeAnswer, GetReadyAnswerToQuestions
from src.tools.scheduled import ListCalendlyScheduledEventsTool, MockListCalendlyScheduledEventsTool
from src.tools.user import GetCalendlyUserTool, MockGetCalendlyUserTool


def build_scheduling_tools(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        GetCalendlyUserTool,
        ListCalendlyEventTypesTool,
        ListCalendlyEventTypeAvailableTimesTool,
        CreateCalendlyInviteeTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools


def build_scheduling_tools_for_tests(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        MockGetCalendlyUserTool,
        MockListCalendlyEventTypesTool,
        MockListCalendlyEventTypeAvailableTimesTool,
        MockCreateCalendlyInviteeTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools


def build_reviewing_tools(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        GetCalendlyUserTool,
        ListCalendlyEventTypesTool,
        ListCalendlyScheduledEventsTool,
        ListCalendlyEventInviteesTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools


def build_reviewing_tools_for_tests(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        MockGetCalendlyUserTool,
        MockListCalendlyEventTypesTool,
        MockListCalendlyScheduledEventsTool,
        MockListCalendlyEventInviteesTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools


def build_rescheduling_tools(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        GetCalendlyUserTool,
        ListCalendlyEventTypesTool,
        ListCalendlyScheduledEventsTool,
        ListCalendlyEventInviteesTool,
        ListCalendlyEventTypeAvailableTimesTool,
        CreateCalendlyInviteeTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools


def build_rescheduling_tools_for_tests(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        MockGetCalendlyUserTool,
        MockListCalendlyEventTypesTool,
        MockListCalendlyScheduledEventsTool,
        MockListCalendlyEventInviteesTool,
        MockListCalendlyEventTypeAvailableTimesTool,
        MockCreateCalendlyInviteeTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools


def build_cancelling_tools(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        GetCalendlyUserTool,
        ListCalendlyScheduledEventsTool,
        ListCalendlyEventInviteesTool,
        CancelCalendlyEventTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools


def build_cancelling_tools_for_tests(calendly_client: CalendlyClient) -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        MockGetCalendlyUserTool,
        MockListCalendlyScheduledEventsTool,
        MockListCalendlyEventInviteesTool,
        MockCancelCalendlyEventTool,
    ]:
        instance = cls(calendly_client)
        tools[instance.name] = instance
    return tools


def build_questions_tools() -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        CheckWhatOtherQuestionsCanWeAnswer,
        GetReadyAnswerToQuestions,
    ]:
        instance = cls()
        tools[instance.name] = instance
    return tools


def build_questions_tools_for_tests() -> dict[str, BaseTool]:
    tools: dict[str, BaseTool] = {}
    for cls in [
        CheckWhatOtherQuestionsCanWeAnswer,
        GetReadyAnswerToQuestions,
    ]:
        instance = cls()
        tools[instance.name] = instance
    return tools
