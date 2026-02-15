"""Main entry point for the Acme Dental AI Agent."""

import argparse
import logging
from datetime import datetime
from typing import Any

import pytz
from dotenv import load_dotenv
from langchain.messages import HumanMessage
from langchain_core.language_models import BaseChatModel
from langgraph.types import Command

from src.agent import create_acme_dental_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG logging level")
    return parser.parse_args()


def configure_logging(debug: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s"
    )


def get_current_timezone_string():
    current_time = datetime.now(pytz.utc)
    timezone = current_time.tzinfo
    return str(timezone) if timezone else "UTC"


def invoke_and_print(agent: BaseChatModel, input_data: dict[str, Any], config: dict):
    result = agent.invoke(input_data, config=config)
    new_messages = result.get("messages", [])
    if not new_messages:
        print("Agent: No response generated.\n")
        return None
    last_message = new_messages[-1]
    print(f"Agent: {last_message.content}\n")
    return result


def main():
    config = {"configurable": {"thread_id": "approval-123"}}
    args = parse_args()
    configure_logging(args.debug)
    logging.debug("Debug logging is enabled.")
    logging.info("Application started.")
    load_dotenv()
    agent = create_acme_dental_agent()
    waiting_for_user_input = False
    timezone = get_current_timezone_string()
    input_data = {"messages": [HumanMessage(role="user", content=f"hello, my timezone is {timezone}")]}
    result = invoke_and_print(agent, input_data, config)
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        try:
            user_message = [HumanMessage(role="user", content=user_input)]
            invoke_input = (
                Command(resume={"messages": user_message}) if waiting_for_user_input else {"messages": user_message}
            )
            result = invoke_and_print(agent, invoke_input, config)
            waiting_for_user_input = "__interrupt__" in result if result else False
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
