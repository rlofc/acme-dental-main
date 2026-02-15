"""Integration Tests"""

import logging
from pprint import pformat

import pytest
from agentevals.trajectory.llm import (
    TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE,
    create_trajectory_llm_as_judge,
)
from agentevals.trajectory.match import create_trajectory_match_evaluator
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.agent import create_acme_dental_agent
from src.api.calendly import CalendlyClient
from src.tools import (
    build_cancelling_tools_for_tests,
    build_questions_tools_for_tests,
    build_rescheduling_tools_for_tests,
    build_reviewing_tools_for_tests,
    build_scheduling_tools_for_tests,
)


@pytest.fixture
def calendly_agent():
    load_dotenv()
    calendly_client = CalendlyClient()
    intent_tool_sets = {
        "question": build_questions_tools_for_tests(),
        "schedule": build_scheduling_tools_for_tests(calendly_client),
        "review": build_reviewing_tools_for_tests(calendly_client),
        "reschedule": build_rescheduling_tools_for_tests(calendly_client),
        "cancel": build_cancelling_tools_for_tests(calendly_client),
        "leave": {},
    }
    return create_acme_dental_agent(intent_tool_sets=intent_tool_sets, greet=False)


@pytest.fixture
def trajectory_llm_evaluator():
    return create_trajectory_llm_as_judge(
        prompt=TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE,
        model="openai:o3-mini",
    )


@pytest.fixture
def trajectory_match_evaluator():
    return create_trajectory_match_evaluator(
        trajectory_match_mode="strict",
        tool_args_match_mode="exact",
    )


def run_trajectory_test(agent, evaluator, user_message, reference_trajectory):
    config = {"configurable": {"thread_id": "approval-123"}}
    ai_msg = agent.invoke({"messages": [HumanMessage(role="user", content=user_message)]}, config=config)
    logging.debug(f"{pformat(ai_msg)}")

    evaluation = evaluator(
        outputs=ai_msg["messages"],
        reference_outputs=reference_trajectory,
    )
    logging.debug(f"{pformat(evaluation)}")

    assert evaluation["score"]


@pytest.mark.asyncio
async def test_naive_user_appointments_check_flow(calendly_agent, trajectory_match_evaluator):
    """
    Verify a naive trajectory when the user is asking to be reminded
    of their appointments.

    No tools should be invoked in this scenario.
    """
    reference_trajectory = [
        HumanMessage(content=""),
        AIMessage(content="", tool_calls=[]),
    ]

    run_trajectory_test(
        calendly_agent,
        trajectory_match_evaluator,
        user_message="What are my appointments?",
        reference_trajectory=reference_trajectory,
    )


@pytest.mark.asyncio
async def test_naive_appointment_scheduling_flow_with_appointment_type(calendly_agent, trajectory_llm_evaluator):
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
        trajectory_llm_evaluator,
        user_message="Do you have a free appointment slot on January 1st 2030 for a Dental checkup",
        reference_trajectory=reference_trajectory,
    )


@pytest.mark.asyncio
async def test_naive_rescheduling_flow(calendly_agent, trajectory_llm_evaluator):
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
            content=(
                "I'd like to cancel my appointment on January 1st, 2030."
                "My name is 'Test Test' and my email is 'test@foo.com'"
            ),
            role="user",
        ),
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
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_4",
                    "name": "list_calendly_event_type_available_times",
                    "args": {"input_str": '{"event_uuid": "ABC123"}'},
                }
            ],
        ),
        ToolMessage(content="", tool_call_id="call_4"),
        AIMessage(
            content="",
            tool_calls=[
                {"id": "call_5", "name": "create_calendly_invitee", "args": {"input_str": '{"event_uuid": "ABC123"}'}}
            ],
        ),
        ToolMessage(content="", tool_call_id="call_5"),
        AIMessage(
            content="",
            tool_calls=[
                {"id": "call_6", "name": "cancel_calendly_event", "args": {"input_str": '{"event_uuid": "ABC123"}'}}
            ],
        ),
        ToolMessage(content="", tool_call_id="call_6"),
        AIMessage(content="", tool_calls=[]),
    ]

    run_trajectory_test(
        calendly_agent,
        trajectory_llm_evaluator,
        user_message=(
            "I'd like to reschedule my January 1st 10:30 appointment to 11am on the same day."
            " My email is 'test@foo.com'"
        ),
        reference_trajectory=reference_trajectory,
    )


@pytest.mark.asyncio
async def test_cancel_appointment_flow(calendly_agent, trajectory_llm_evaluator):
    """
    Verify, using an LLM-as-judge evaluation, a cancel trajectory when the user
    is asking to cancel their specific appointment.

    - Evaluation is done via llm-as-judge against the reference trajectory:
      * get_calendly_current_user
      * list_calendly_scheduled_events
      * list_calendly_event_invitees
      * cancel_calendly_event
    """
    reference_trajectory = [
        HumanMessage(
            content=(
                "I'd like to cancel my appointment on January 1st, 2030."
                "My name is 'Test Test' and my email is 'test@foo.com'"
            ),
            role="user",
        ),
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
        AIMessage(
            content="",
            tool_calls=[
                {"id": "call_4", "name": "cancel_calendly_event", "args": {"input_str": '{"event_uuid": "ABC123"}'}}
            ],
        ),
        ToolMessage(content="", tool_call_id="call_4"),
        AIMessage(content="", tool_calls=[]),
    ]

    run_trajectory_test(
        calendly_agent,
        trajectory_llm_evaluator,
        user_message=(
            "I'd like to cancel my appointment on January 1st, 2030."
            " My name is 'Test Test' and my email is 'test@foo.com'"
        ),
        reference_trajectory=reference_trajectory,
    )


@pytest.mark.asyncio
async def test_random_question_flow(calendly_agent, trajectory_llm_evaluator):
    """
    Verify, using an LLM-as-judge evaluation, a random question trajectory when the user
    is asking a quesion we can answer on from our knowledge-base.

    - Evaluation is done via llm-as-judge against the reference trajectory:
      * check_other_questions_we_can_answer
      * get_predefined_answer_to_other_questions
    """
    reference_trajectory = [
        HumanMessage(
            content="Can I just come in to the clinic without an appointment?",
            role="user",
        ),
        AIMessage(content="", tool_calls=[{"id": "call_1", "name": "check_other_questions_we_can_answer", "args": {}}]),
        ToolMessage(content="", tool_call_id="call_1"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_2",
                    "name": "get_predefined_answer_to_other_questions",
                    "args": {"question": "Do you accept walk-ins?"},
                }
            ],
        ),
        ToolMessage(content="", tool_call_id="call_2"),
        AIMessage(content="", tool_calls=[]),
    ]

    run_trajectory_test(
        calendly_agent,
        trajectory_llm_evaluator,
        user_message="Can I just come in to the clinic without an appointment?",
        reference_trajectory=reference_trajectory,
    )
