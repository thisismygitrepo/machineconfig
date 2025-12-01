"""
Data models for the command navigator.
"""

from typing import Optional
from dataclasses import dataclass


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


@dataclass
class ArgumentInfo:
    """Information about a command argument."""
    name: str
    is_required: bool
    is_flag: bool
    placeholder: str = ""
    description: str = ""