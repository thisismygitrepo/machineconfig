"""
playwright install
sudo nala install libavif13
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"

from langchain_ollama import ChatOllama
from browser_use import Agent
import asyncio

BOX_WIDTH = 150  # width for box drawing


def _get_padding(text: str, padding_before: int = 2, padding_after: int = 1) -> str:
    """Calculate the padding needed to align the box correctly.
    
    Args:
        text: The text to pad
        padding_before: The space taken before the text (usually "║ ")
        padding_after: The space needed after the text (usually " ║")
    
    Returns:
        A string of spaces for padding
    """
    # Count visible characters (might not be perfect for all Unicode characters)
    text_length = len(text)
    padding_length = BOX_WIDTH - padding_before - text_length - padding_after
    return ' ' * max(0, padding_length)


# Create agent with the model
async def main():
    # header for browser automation agent
    title = "🌐 Browser Automation Agent"
    print(f"""
╔{'═' * BOX_WIDTH}╗
║ {title}{_get_padding(title)}║
╚{'═' * BOX_WIDTH}╝
""")

    print("🔄 Initializing LLM model (llama3.1:8b)...")
    llm = ChatOllama(model="llama3.1:8b")
    print("✅ LLM model initialized")
    
    task_line1 = "🤖 Task: Open https://chat.openai.com/ and ask how many r's in"
    task_line2 = "rrraaararewey, use Thinking Button and type the answer"
    print(f"""
╭{'─' * BOX_WIDTH}╮
│ {task_line1}{_get_padding(task_line1)}│
│ {task_line2}{_get_padding(task_line2)}│
╰{'─' * BOX_WIDTH}╯
""")
    
    print("🚀 Creating and launching browser agent...")
    agent = Agent(
        task="open https://chat.openai.com/ and ask how many r's in rrraaararewey, use Thinking Button and type the answer",
        llm=llm
    )

    print("🏃‍♂️ Running agent task...")
    await agent.run()
    
    # footer success box
    title = "✅ Browser automation task completed"
    print(f"""
╔{'═' * BOX_WIDTH}╗
║ {title}{_get_padding(title)}║
╚{'═' * BOX_WIDTH}╝
""")


if __name__ == "__main__":
    asyncio.run(main())

