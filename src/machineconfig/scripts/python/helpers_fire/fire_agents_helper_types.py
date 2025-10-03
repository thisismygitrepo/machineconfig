
from typing import Literal, TypeAlias, TypedDict


AGENTS: TypeAlias = Literal["cursor-agent", "gemini", "crush", "q", "opencode"]
MATCHINE: TypeAlias = Literal["local", "docker"]
PROVIDER: TypeAlias = Literal["azure", "google", "aws", "openai", "anthropic", "openrouter"]
MODEL: TypeAlias = Literal["zai/glm-4.6", "anthropic/sonnet-4.5", "google/gemini-2.5-pro", "openai/gpt-5-codex",
                           "openrouter/supernova", "xi/grok-4-fast:free"]

class AI_SPEC(TypedDict):
    provider: PROVIDER
    model: MODEL
    agent: AGENTS
    machine: MATCHINE    


AGENT_NAME_FORMATTER = "agent_{idx}_cmd.sh"  # e.g., agent_0_cmd.sh
SEARCH_STRATEGIES: TypeAlias = Literal["file_path", "keyword_search", "filename_pattern"]

