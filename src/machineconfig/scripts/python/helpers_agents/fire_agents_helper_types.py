
from typing import Literal, TypeAlias, TypedDict


# Vscode extensions for AI-assisted coding.
# Github copilot
# Roo
# Cline
# Kilocode
# Continue
# CodeGPT
# qodo (and cli)

# Editors based on AI
# Kiro
# Cursor
# Warp

AGENTS: TypeAlias = Literal["cursor-agent", "gemini", "qwen-code", "copilot", "crush", "q", "opencode", "kilocode", "cline", "auggie", "warp", "droid"]
HOST: TypeAlias = Literal["local", "docker"]
PROVIDER: TypeAlias = Literal["azure", "google", "aws", "openai", "anthropic", "openrouter", "xai"]

class AI_SPEC(TypedDict):
    provider: PROVIDER
    model: str
    agent: AGENTS
    machine: HOST
    api_key: str | None
    api_name: str


AGENT_NAME_FORMATTER = "agent_{idx}_cmd.sh"  # e.g., agent_0_cmd.sh
SEARCH_STRATEGIES: TypeAlias = Literal["file_path", "keyword_search", "filename_pattern"]

