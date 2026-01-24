
import asyncio
from typing import Any

from copilot import CopilotClient, MessageOptions, SessionConfig


async def main() -> None:
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
        elif event_type == "assistant.reasoning_delta":
            delta = getattr(getattr(event, "data", None), "delta_content", "") or ""
            print(delta, end="", flush=True)
        elif event_type == "assistant.message":
            content = getattr(getattr(event, "data", None), "content", "") or ""
            if content:
                print(f"""\n--- Final message ---\n{content}""")
        elif event_type == "assistant.reasoning":
            content = getattr(getattr(event, "data", None), "content", "") or ""
            if content:
                print(f"""\n--- Reasoning ---\n{content}""")
        elif event_type == "session.idle":
            done.set()
        else:
            print(f"""\n[{event_type}] {getattr(event, "data", None)}""")

    session.on(on_event)

    msg = MessageOptions(
        prompt="could you please cd to ~/code/machineconfig and git status, add all text-like files to the staging area, write appropriate commit message based on the git diff you see, and push to origin main?",
    )
    await session.send(msg)
    await done.wait()
    await session.destroy()
    await client.stop()


asyncio.run(main())
