"""Simple AI Agent for the Acme Dental Clinic."""

import logging
import operator
import os
from pprint import pformat
from string import Template
from typing import Annotated, Literal

from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, SystemMessage, ToolMessage
from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

from src.api.calendly import CalendlyClient
from src.tools import (
    build_cancelling_tools,
    build_questions_tools,
    build_rescheduling_tools,
    build_reviewing_tools,
    build_scheduling_tools,
)


class IntentClassification(TypedDict):
    intent: Literal["question", "schedule", "review", "reschedule", "cancel", "unclear", "leave"]
    topic: str
    summary: str


class AssistantState(TypedDict):
    request_content: str
    intent: IntentClassification | None
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


def build_intent_detector(model: BaseChatModel, prompt: str):
    """Returns a configured closure for the llm_calls in the graph"""
    intent_model = model.with_structured_output(IntentClassification)

    def llm_call(state: AssistantState):
        """LLM decides whether to call a tool or not"""

        logging.debug(f"{pformat(state)}")
        intent = intent_model.invoke([SystemMessage(content=prompt)] + state["messages"])
        logging.debug(f"{pformat(intent)}")

        return Command(update={"intent": intent}, goto=intent["intent"])

    return llm_call


def build_llm_call(model_with_tools: BaseChatModel, prompt: str):
    """Returns a configured closure for the llm_calls in the graph"""

    def llm_call(state: AssistantState):
        """LLM decides whether to call a tool or not"""

        logging.debug(f"{pformat(state)}")
        return {
            "messages": [model_with_tools.invoke([SystemMessage(content=prompt)] + state["messages"])],
        }

    return llm_call


def build_tool_node(tools_by_name: dict[str, BaseTool]):
    """Returns a configured closure for the tool_node calls in the graph"""

    def tool_node(state: AssistantState):
        """Performs the tool call"""
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            try:
                observation = tool.invoke(tool_call["args"])
            except Exception as e:
                logging.error(f"{e}")
                observation = "tool failed"  # TODO: handle errors better
            wrapper = {"result": observation, "type": "json"}
            result.append(ToolMessage(content=wrapper, tool_call_id=tool_call["id"]))
        return {"messages": result}

    return tool_node


def build_user_input_node():
    """Returns a configured closure for a user_input node in the graph"""

    def user_input_node(state: AssistantState):
        """Break out using an interrupt to get more input"""

        logging.debug(f"{pformat(state)}")
        result = interrupt(
            {
                "messages": state["messages"],
            }
        )
        return result

    return user_input_node


def build_should_continue(tool_node_name: str):
    def should_continue(state: AssistantState) -> Literal[tool_node_name, END]:
        """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

        messages = state["messages"]
        last_message = messages[-1]

        if last_message.tool_calls:
            return tool_node_name

        return "user_input"

    return should_continue


def load_prompt(name: str, config: dict) -> str:
    """
    Load prompts/<name>.txt and substitute placeholders using the provided config dict.
    """
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "prompts", f"{name}.txt")

    with open(path, encoding="utf-8") as f:
        content = f.read()

    tmpl = Template(content)
    return tmpl.safe_substitute(config)


def create_acme_dental_agent(
    openai_api_key: str | None = None,
    calendly_api_token: str | None = None,
    intent_tool_sets: dict[str, dict[str, BaseTool]] | None = None,
    greet: bool = True,
):
    """
    Build a LangChain agent that can reason about and call Calendly tools.
    """

    model = init_chat_model("claude-sonnet-4-5-20250929", temperature=0)

    calendly_client = CalendlyClient(api_token=calendly_api_token)

    if not intent_tool_sets:
        intent_tool_sets = {
            "question": build_questions_tools(),
            "schedule": build_scheduling_tools(calendly_client),
            "review": build_reviewing_tools(calendly_client),
            "reschedule": build_rescheduling_tools(calendly_client),
            "cancel": build_cancelling_tools(calendly_client),
            "greet": {},
            "leave": {},
        }

    agent_builder = StateGraph(AssistantState)
    agent_builder.add_node("detect_intent", build_intent_detector(model, load_prompt("intent", {})))

    agent_builder.add_node(
        "unclear", build_llm_call(model.bind_tools(build_questions_tools().values()), load_prompt("agent", {}))
    )

    for intent in intent_tool_sets:
        agent_builder.add_node(
            intent,
            build_llm_call(
                model.bind_tools(intent_tool_sets[intent].values()),
                load_prompt(intent, {"agent_prompt": load_prompt("agent", {})}),
            ),
        )
        agent_builder.add_node(f"{intent}_tools_node", build_tool_node(intent_tool_sets[intent]))
        agent_builder.add_conditional_edges(
            intent, build_should_continue(f"{intent}_tools_node"), [f"{intent}_tools_node", "user_input"]
        )
        agent_builder.add_edge(f"{intent}_tools_node", intent)

    agent_builder.add_node("user_input", build_user_input_node())
    if greet:
        agent_builder.add_edge(START, "greet")
        agent_builder.add_edge("greet", "user_input")
    else:
        agent_builder.add_edge(START, "detect_intent")
    agent_builder.add_edge("user_input", "detect_intent")
    agent_builder.add_edge("unclear", "user_input")
    agent_builder.add_edge("leave", END)

    memory = MemorySaver()
    agent = agent_builder.compile(checkpointer=memory)

    return agent
