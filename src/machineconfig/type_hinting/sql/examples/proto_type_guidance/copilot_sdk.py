
import argparse
import asyncio
import json
from pprint import pformat
from typing import Any, TypedDict

from copilot import CopilotClient, MessageOptions, SessionConfig


class AppConfig(TypedDict):
    show_event_data: bool
    pretty_event_data: bool
    show_delta_data: bool


def parse_args() -> AppConfig:
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--show-event-data", action="store_true")
    # parser.add_argument("--pretty-event-data", action="store_true")
    # parser.add_argument("--show-delta-data", action="store_true")
    # args = parser.parse_args()
    # return {
    #     "show_event_data": bool(args.show_event_data),
    #     "pretty_event_data": bool(args.pretty_event_data),
    #     "show_delta_data": bool(args.show_delta_data),
    # }
    return {
        "show_event_data": True,
        "pretty_event_data": True,
        "show_delta_data": True,
    }


def prune_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: prune_none(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [prune_none(item) for item in value if item is not None]
    return value


def format_event_data(data: Any, pretty: bool) -> str:
    if data is None:
        return "None"

    payload: Any
    if hasattr(data, "model_dump"):
        payload = data.model_dump(exclude_none=True)
    elif isinstance(data, dict):
        payload = data
    else:
        try:
            payload = data.__dict__
        except AttributeError:
            return pformat(data)

    payload = prune_none(payload)
    if pretty:
        try:
            return json.dumps(payload, indent=2, ensure_ascii=False)
        except TypeError:
            return pformat(payload)
    return pformat(payload)


async def main() -> None:
    config = parse_args()
    client = CopilotClient()
    await client.start()

    done = asyncio.Event()
    sess_config = SessionConfig(model="claude-haiku-4.5", streaming=True)
    session = await client.create_session(config=sess_config)

    def on_event(event: Any) -> None:
        event_type = getattr(getattr(event, "type", None), "value", None) or getattr(event, "type", None)
        if event_type == "assistant.message_delta":
            delta = getattr(getattr(event, "data", None), "delta_content", "") or ""
            print(delta, end="", flush=True)
            if config["show_event_data"] and config["show_delta_data"]:
                formatted = format_event_data(getattr(event, "data", None), config["pretty_event_data"])
                print(f"""\n[assistant.message_delta]\n{formatted}""")
        elif event_type == "assistant.reasoning_delta":
            delta = getattr(getattr(event, "data", None), "delta_content", "") or ""
            print(delta, end="", flush=True)
            if config["show_event_data"] and config["show_delta_data"]:
                formatted = format_event_data(getattr(event, "data", None), config["pretty_event_data"])
                print(f"""\n[assistant.reasoning_delta]\n{formatted}""")
        elif event_type == "assistant.message":
            content = getattr(getattr(event, "data", None), "content", "") or ""
            if content:
                print(f"""\n--- Final message ---\n{content}""")
            if config["show_event_data"]:
                formatted = format_event_data(getattr(event, "data", None), config["pretty_event_data"])
                print(f"""\n[assistant.message]\n{formatted}""")
        elif event_type == "assistant.reasoning":
            content = getattr(getattr(event, "data", None), "content", "") or ""
            if content:
                print(f"""\n--- Reasoning ---\n{content}""")
            if config["show_event_data"]:
                formatted = format_event_data(getattr(event, "data", None), config["pretty_event_data"])
                print(f"""\n[assistant.reasoning]\n{formatted}""")
        elif event_type == "session.idle":
            done.set()
        else:
            print(f"""\n[{event_type}]""")
            if config["show_event_data"]:
                formatted = format_event_data(getattr(event, "data", None), config["pretty_event_data"])
                print(formatted)

    session.on(on_event)

    msg = MessageOptions(
        prompt="could you please cd to ~/code/machineconfig and git status, add all text-like files to the staging area, write appropriate commit message based on the git diff you see, and push to origin main?",
    )
    await session.send(msg)
    await done.wait()
    await session.destroy()
    await client.stop()


asyncio.run(main())
