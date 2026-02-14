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
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from src.api.calendly import CalendlyClient
from src.tools import build_tools_dict


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


def build_llm_call(model_with_tools, prompt):
    """Returns a configured closure for the llm_calls in the graph"""
    def llm_call(state: dict):
        """LLM decides whether to call a tool or not"""

        logging.debug(f"{pformat(state)}")
        return {
            "messages": [model_with_tools.invoke([SystemMessage(content=prompt)] + state["messages"])],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    return llm_call


def build_tool_node(tools_by_name):
    """Returns a configured closure for the tool_node calls in the graph"""
    def tool_node(state: dict):
        """Performs the tool call"""
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            wrapper = {"result": observation, "type": "json"}
            result.append(ToolMessage(content=wrapper, tool_call_id=tool_call["id"]))
        return {"messages": result}

    return tool_node


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tool_node"

    return END


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
    tools: dict[str, BaseTool] | None | None = None,
):
    """
    Build a LangChain agent that can reason about and call Calendly tools.
    """

    model = init_chat_model("claude-sonnet-4-5-20250929", temperature=0)

    calendly_client = CalendlyClient(api_token=calendly_api_token)

    tools_by_name = None
    if tools is None:
        tools_by_name = build_tools_dict(calendly_client)
    else:
        tools_by_name = tools

    model = model.bind_tools(tools_by_name.values())

    agent_builder = StateGraph(MessagesState)
    agent_builder.add_node("llm_call", build_llm_call(model, load_prompt("agent", {})))
    agent_builder.add_node("tool_node", build_tool_node(tools_by_name))
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    agent_builder.add_edge("tool_node", "llm_call")

    agent = agent_builder.compile()

    return agent
