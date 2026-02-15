"""Main entry point for the Acme Dental AI Agent."""

import argparse
import logging

from dotenv import load_dotenv

from src.agent import create_acme_dental_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable DEBUG logging level")
    return parser.parse_args()


def configure_logging(debug: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s"
    )


def main():
    config = {"configurable": {"thread_id": "approval-123"}}
    args = parse_args()
    configure_logging(args.debug)
    logging.debug("Debug logging is enabled.")
    logging.info("Application started.")
    load_dotenv()
    agent = create_acme_dental_agent()
    messages = []
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        try:
            messages.append({"role": "user", "content": user_input})
            result = agent.invoke({"messages": messages}, config=config)
            new_messages = result.get("messages", [])
            if not new_messages:
                print("Agent: No response generated.\n")
                continue
            last_message = new_messages[-1]
            print(f"Agent: {last_message.content}\n")
            messages.append({"role": "assistant", "content": last_message.content})
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
