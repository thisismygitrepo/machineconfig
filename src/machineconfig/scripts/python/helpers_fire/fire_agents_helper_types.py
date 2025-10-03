
from typing import Literal, TypeAlias


AGENTS: TypeAlias = Literal[
    "cursor-agent", "gemini", "crush", "q"
    # warp terminal
]
MATCHNE: TypeAlias = Literal["local", "docker"]
PROVIDER: TypeAlias = Literal["azure", "google", "aws", "openai", "anthropic", "openrouter"]
MODEL: TypeAlias = Literal["zai/glm-4.6", "anthropic/sonnet-4.5", "google/gemini-2.5-pro"]

AGENT_NAME_FORMATTER = "agent_{idx}_cmd.sh"  # e.g., agent_0_cmd.sh

SEARCH_STRATEGIES: TypeAlias = Literal["file_path", "keyword_search", "filename_pattern"]

