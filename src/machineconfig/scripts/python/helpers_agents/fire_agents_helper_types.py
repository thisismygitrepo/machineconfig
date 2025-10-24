
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
MODEL: TypeAlias = Literal["zai/glm-4.6", "anthropic/sonnet-4.5", "google/gemini-2.5-pro", "openai/gpt-5-codex",
                           "openrouter/supernova", "x-ai/grok-4-fast:free",
                           ]
PROVIDER2MODEL: dict[PROVIDER, list[MODEL]] = {
    "azure": ["zai/glm-4.6"],
    "google": ["google/gemini-2.5-pro"],
    "aws": [],
    "openai": ["openai/gpt-5-codex"],
    "anthropic": ["anthropic/sonnet-4.5"],
    "openrouter": ["openrouter/supernova"],
    "xai": ["x-ai/grok-4-fast:free"]
}

class AI_SPEC(TypedDict):
    provider: PROVIDER
    model: MODEL
    agent: AGENTS
    machine: HOST    


AGENT_NAME_FORMATTER = "agent_{idx}_cmd.sh"  # e.g., agent_0_cmd.sh
SEARCH_STRATEGIES: TypeAlias = Literal["file_path", "keyword_search", "filename_pattern"]

