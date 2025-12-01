"""TypedDict definitions for fire_agents.py inputs.

This module defines the structured input types for the fire_agents main function,
capturing all user inputs collected during interactive execution.
"""

from pathlib import Path
from typing import TypedDict, Literal, NotRequired
from machineconfig.scripts.python.helpers.helpers_agents.fire_agents_help_launch import AGENTS

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


class TasksPerPromptSplittingInput(TypedDict):
    """Input for tasks_per_prompt splitting strategy."""
    tasks_per_prompt: int  # Default: 13


class FireAgentsMainInput(TypedDict):
    """Complete input structure for fire_agents main function."""

    # Core configuration
    repo_root: Path
    search_strategy: SEARCH_STRATEGIES
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
    tasks_per_prompt: TasksPerPromptSplittingInput


class FireAgentsRuntimeData(TypedDict):
    """Runtime data derived from inputs during execution."""

    prompt_material: str
    separator: str
    prompt_material_re_splitted: list[str]
    random_name: str  # 3-character random string for session naming
