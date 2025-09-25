"""TypedDict definitions for fire_agents.py inputs.

This module defines the structured input types for the fire_agents main function,
capturing all user inputs collected during interactive execution.
"""

from pathlib import Path
from typing import TypedDict, Literal, NotRequired
from machineconfig.scripts.python.fire_agents_load_balancer import SPLITTING_STRATEGY
from machineconfig.scripts.python.fire_agents_help_launch import AGENTS

SEARCH_STRATEGIES = Literal["file_path", "keyword_search", "filename_pattern"]


class FilePathSearchInput(TypedDict):
    """Input for file_path search strategy."""

    file_path: str
    separator: str  # Default: "\n"


class KeywordSearchInput(TypedDict):
    """Input for keyword_search strategy."""

    keyword: str


class FilenamePatternSearchInput(TypedDict):
    """Input for filename_pattern search strategy."""

    pattern: str  # e.g., '*.py', '*test*', 'config.*'


class AgentCapSplittingInput(TypedDict):
    """Input for agent_cap splitting strategy."""

    agent_cap: int  # Default: 6


class TaskRowsSplittingInput(TypedDict):
    """Input for task_rows splitting strategy."""

    task_rows: int  # Default: 13


class FireAgentsMainInput(TypedDict):
    """Complete input structure for fire_agents main function."""

    # Core configuration
    repo_root: Path
    search_strategy: SEARCH_STRATEGIES
    splitting_strategy: SPLITTING_STRATEGY
    agent_selected: AGENTS
    prompt_prefix: str
    job_name: str  # Default: "AI_Agents"
    keep_material_in_separate_file: bool  # Default: False
    max_agents: int  # Default: 25

    # Search strategy specific inputs (only one will be present based on search_strategy)
    file_path_input: NotRequired[FilePathSearchInput]
    keyword_search_input: NotRequired[KeywordSearchInput]
    filename_pattern_input: NotRequired[FilenamePatternSearchInput]

    # Splitting strategy specific inputs (only one will be present based on splitting_strategy)
    agent_cap_input: NotRequired[AgentCapSplittingInput]
    task_rows_input: NotRequired[TaskRowsSplittingInput]


class FireAgentsRuntimeData(TypedDict):
    """Runtime data derived from inputs during execution."""

    prompt_material: str
    separator: str
    prompt_material_re_splitted: list[str]
    random_name: str  # 3-character random string for session naming
