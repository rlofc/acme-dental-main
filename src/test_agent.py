"""Integration Tests"""
import pytest
from agentevals.trajectory.llm import TRAJECTORY_ACCURACY_PROMPT, create_trajectory_llm_as_judge
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.agent import create_acme_dental_agent
from src.api.calendly import CalendlyClient
from src.tools import build_testing_tools_dict


@pytest.fixture
def calendly_agent():
    load_dotenv()
    calendly_client = CalendlyClient()
    return create_acme_dental_agent(tools=build_testing_tools_dict(calendly_client))


@pytest.fixture
def trajectory_evaluator():
    return create_trajectory_llm_as_judge(
        prompt=TRAJECTORY_ACCURACY_PROMPT,
        model="openai:o3-mini",
    )


def run_trajectory_test(agent, evaluator, user_message, reference_trajectory):
    ai_msg = agent.invoke({"messages": [HumanMessage(role="user", content=user_message)]})

    evaluation = evaluator(
        outputs=ai_msg["messages"],
        reference_outputs=reference_trajectory,
    )

    assert evaluation["score"]


@pytest.mark.asyncio
async def test_naive_user_appointments_check_flow(calendly_agent, trajectory_evaluator):
    """
    Verify a naive trajectory when the user is asking to be reminded
    of their appointments.

    - The reference tranjectory is:
      * get_calendly_current_user
      * list_calendly_scheduled_events
      * list_calendly_event_invitees

    Evaluation is done using llm-as-judge
    """
    reference_trajectory = [
        HumanMessage(content=""),
        AIMessage(content="", tool_calls=[{"id": "call_1", "name": "get_calendly_current_user", "args": {}}]),
        ToolMessage(content="", tool_call_id="call_1"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_2",
                    "name": "list_calendly_scheduled_events",
                    "args": {"input_str": '{"user": "xyz", "organization": "xyz"}'},
                }
            ],
        ),
        ToolMessage(content="", tool_call_id="call_2"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_3",
                    "name": "list_calendly_event_invitees",
                    "args": {"event_uri": "https://api.calendly.com/scheduled_events/ABC123"},
                }
            ],
        ),
        ToolMessage(content="", tool_call_id="call_3"),
        AIMessage(content="", tool_calls=[]),
    ]

    run_trajectory_test(
        calendly_agent,
        trajectory_evaluator,
        user_message="What are my appointments?",
        reference_trajectory=reference_trajectory,
    )


@pytest.mark.asyncio
async def test_naive_appointment_scheduling_flow_with_appointment_type(calendly_agent, trajectory_evaluator):
    """
    Verify, using an LLM-as-judge evaluation, a naive trajectory when the user
    is asking for a free appointment slot for a dental checkup on a specific date.

    - Evaluation is done via llm-as-judge against the reference trajectory:
      * get_calendly_current_user
      * list_calendly_event_types
      * list_calendly_event_type_available_times
    """
    reference_trajectory = [
        HumanMessage(
            content="Do you have a free appointment slot on January 1st 2030 for a Dental checkup", role="user"
        ),
        AIMessage(content="", tool_calls=[{"id": "call_1", "name": "get_calendly_current_user", "args": {}}]),
        ToolMessage(content="", tool_call_id="call_1"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_2",
                    "name": "list_calendly_event_types",
                    "args": {"input_str": '{"user": "xyz", "organization": "xyz"}'},
                }
            ],
        ),
        ToolMessage(content="", tool_call_id="call_2"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_3",
                    "name": "list_calendly_event_type_available_times",
                    "args": {
                        "input_str": (
                            '{"event_type": "1", "start_time": '
                            '"2030-01-01T00:00:00Z", "end_time": "2030-01-01T23:59:59Z"}'
                        )
                    },
                }
            ],
        ),
        ToolMessage(content="", tool_call_id="call_3"),
        AIMessage(content="", tool_calls=[]),
    ]

    run_trajectory_test(
        calendly_agent,
        trajectory_evaluator,
        user_message="Do you have a free appointment slot on January 1st 2030 for a Dental checkup",
        reference_trajectory=reference_trajectory,
    )
