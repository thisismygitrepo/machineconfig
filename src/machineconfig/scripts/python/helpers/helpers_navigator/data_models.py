"""
Data models for the command navigator.
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ArgumentInfo:
    """Information about a command argument."""
    name: str
    is_required: bool
    is_flag: bool
    placeholder: str = ""
    description: str = ""
    is_positional: bool = False
    flag: str = ""
    negated_flag: str = ""
    long_flags: list[str] = field(default_factory=list)
    short_flags: list[str] = field(default_factory=list)


@dataclass
class CommandInfo:
    """Information about a CLI command."""
    name: str
    description: str
    command: str
    parent: Optional[str] = None
    is_group: bool = False
    help_text: str = ""
    module_path: str = ""
    arguments: Optional[list[ArgumentInfo]] = None
    long_description: str = ""
