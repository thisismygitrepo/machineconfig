# """
# playwright install
# sudo nala install libavif13
# """

# import os
# os.environ["ANONYMIZED_TELEMETRY"] = "false"

# from langchain_ollama import ChatOllama
# from browser_use import Agent
# import asyncio
# from rich.panel import Panel
# from rich import print as rprint

# BOX_WIDTH = 150  # width for box drawing


# def _get_padding(text: str, padding_before: int = 2, padding_after: int = 1) -> str:
#     """Calculate the padding needed to align the box correctly.

#     Args:
#         text: The text to pad
#         padding_before: The space taken before the text (usually "║ ")
#         padding_after: The space needed after the text (usually " ║")

#     Returns:
#         A string of spaces for padding
#     """
#     # Count visible characters (might not be perfect for all Unicode characters)
#     text_length = len(text)
#     padding_length = BOX_WIDTH - padding_before - text_length - padding_after
#     return ' ' * max(0, padding_length)


# # Create agent with the model
# async def main():
#     # header for browser automation agent
#     title = "🌐 Browser Automation Agent"
#     rprint(Panel(title, title="Status", width=BOX_WIDTH))

#     rprint("🔄 Initializing LLM model (llama3.1:8b)...")
#     llm = ChatOllama(model="llama3.1:8b")
#     rprint("✅ LLM model initialized")

#     task_line1 = "🤖 Task: Open https://chat.openai.com/ and ask how many r's in"
#     task_line2 = "rrraaararewey, use Thinking Button and type the answer"
#     task_content = f"{task_line1}\n{task_line2}"
#     rprint(Panel(task_content, title="Task", width=BOX_WIDTH))

#     rprint("🚀 Creating and launching browser agent...")
#     agent = Agent(
#         task="open https://chat.openai.com/ and ask how many r's in rrraaararewey, use Thinking Button and type the answer",
#         llm=llm
#     )

#     rprint("🏃‍♂️ Running agent task...")
#     await agent.run()

#     # footer success box
#     title = "✅ Browser automation task completed"
#     rprint(Panel(title, title="Status", width=BOX_WIDTH))


# if __name__ == "__main__":
#     asyncio.run(main())

