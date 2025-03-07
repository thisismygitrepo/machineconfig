

"""
playwright install
sudo nala install libavif13
"""

import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"

from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama3.1:8b")
# llm.invoke("hi")

from browser_use import Agent
from pydantic import SecretStr
import asyncio



# Create agent with the model
async def main():

    agent = Agent(
        task="open https://chat.openai.com/ and ask how many r's in rrraaararewey, use Thinking Button and type the answer",
        llm=llm
    )

    await agent.run()


asyncio.run(main())

