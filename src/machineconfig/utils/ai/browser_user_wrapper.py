"""
playwright install
sudo nala install libavif13
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"

from langchain_ollama import ChatOllama
from browser_use import Agent
import asyncio
from rich.panel import Panel
from rich import print as rprint

BOX_WIDTH = 150  # width for box drawing


# Create agent with the model
async def main():
    # header for browser automation agent
    title = "🌐 Browser Automation Agent"
    rprint(Panel(title, title="Status", width=BOX_WIDTH))

    rprint("🔄 Initializing LLM model (llama3.1:8b)...")
    llm = ChatOllama(model="llama3.1:8b")
    rprint("✅ LLM model initialized")
    
    task_line1 = "🤖 Task: Open https://chat.openai.com/ and ask how many r's in"
    task_line2 = "rrraaararewey, use Thinking Button and type the answer"
    task_content = f"{task_line1}\n{task_line2}"
    rprint(Panel(task_content, title="Task", width=BOX_WIDTH))
    
    rprint("🚀 Creating and launching browser agent...")
    agent = Agent(
        task="open https://chat.openai.com/ and ask how many r's in rrraaararewey, use Thinking Button and type the answer",
        llm=llm
    )

    rprint("🏃‍♂️ Running agent task...")
    await agent.run()
    
    # footer success box
    title = "✅ Browser automation task completed"
    rprint(Panel(title, title="Status", width=BOX_WIDTH))


if __name__ == "__main__":
    asyncio.run(main())

