
from typing import Literal, TypeAlias


AGENTS: TypeAlias = Literal[
    "cursor-agent", "gemini", "crush", "q"
    # warp terminal
]
AGENT_NAME_FORMATTER = "agent_{idx}_cmd.sh"  # e.g., agent_0_cmd.sh

SEARCH_STRATEGIES: TypeAlias = Literal["file_path", "keyword_search", "filename_pattern"]

