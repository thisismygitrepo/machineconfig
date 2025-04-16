"""
playwright install
sudo nala install libavif13
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"

from langchain_ollama import ChatOllama
from browser_use import Agent
import asyncio


# Create agent with the model
async def main():
    print(f"""
╔{'═' * 70}╗
║ 🌐 Browser Automation Agent
╚{'═' * 70}╝
""")

    print("🔄 Initializing LLM model (llama3.1:8b)...")
    llm = ChatOllama(model="llama3.1:8b")
    print("✅ LLM model initialized")
    
    print(f"""
╭{'─' * 70}╮
│ 🤖 Task: Open https://chat.openai.com/ and ask how many r's in  │
│       rrraaararewey, use Thinking Button and type the answer    │
╰{'─' * 70}╯
""")
    
    print("🚀 Creating and launching browser agent...")
    agent = Agent(
        task="open https://chat.openai.com/ and ask how many r's in rrraaararewey, use Thinking Button and type the answer",
        llm=llm
    )

    print("🏃‍♂️ Running agent task...")
    await agent.run()
    
    print(f"""
╔{'═' * 70}╗
║ ✅ Browser automation task completed
╚{'═' * 70}╝
""")


if __name__ == "__main__":
    asyncio.run(main())

