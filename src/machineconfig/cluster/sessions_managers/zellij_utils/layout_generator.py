#!/usr/bin/env python3
"""
Zellij layout generation utilities for creating KDL layout files.
"""
import shlex
import random
import string
from typing import Dict, List, Tuple
from pathlib import Path
import logging

from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()


class LayoutGenerator:
    """Handles generation of Zellij KDL layout files."""

    LAYOUT_TEMPLATE = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""

    @staticmethod
    def generate_random_suffix(length: int = 8) -> str:
        """Generate a random string suffix for unique layout file names."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    @staticmethod
    def parse_command(command: str) -> Tuple[str, List[str]]:
        """Parse a command string into command and arguments."""
        try:
            parts = shlex.split(command)
            if not parts:
                raise ValueError("Empty command provided")
            return parts[0], parts[1:] if len(parts) > 1 else []
        except ValueError as e:
            logger.error(f"Error parsing command '{command}': {e}")
            parts = command.split()
            return parts[0] if parts else "", parts[1:] if len(parts) > 1 else []

    @staticmethod
    def format_args_for_kdl(args: List[str]) -> str:
        """Format command arguments for KDL syntax."""
        if not args:
            return ""
        formatted_args = []
        for arg in args:
            if ' ' in arg or '"' in arg or "'" in arg:
                escaped_arg = arg.replace('"', '\\"')
                formatted_args.append(f'"{escaped_arg}"')
            else:
                formatted_args.append(f'"{arg}"')
        return " ".join(formatted_args)

    @staticmethod
    def create_tab_section(tab_name: str, cwd: str, command: str) -> str:
        """Create a KDL tab section for the layout."""
        cmd, args = LayoutGenerator.parse_command(command)
        args_str = LayoutGenerator.format_args_for_kdl(args)
        tab_cwd = cwd or "~"
        escaped_tab_name = tab_name.replace('"', '\\"')

        tab_section = f'  tab name="{escaped_tab_name}" cwd="{tab_cwd}" {{\n'
        tab_section += f'    pane command="{cmd}" {{\n'
        if args_str:
            tab_section += f'      args {args_str}\n'
        tab_section += '    }\n  }\n'
        return tab_section

    @staticmethod
    def validate_tab_config(tab_config: Dict[str, Tuple[str, str]]) -> None:
        """Validate tab configuration format and content."""
        if not tab_config:
            raise ValueError("Tab configuration cannot be empty")
        for tab_name, (cwd, command) in tab_config.items():
            if not tab_name.strip():
                raise ValueError(f"Invalid tab name: {tab_name}")
            if not command.strip():
                raise ValueError(f"Invalid command for tab '{tab_name}': {command}")
            if not cwd.strip():
                raise ValueError(f"Invalid cwd for tab '{tab_name}': {cwd}")

    def generate_layout_content(self, tab_config: Dict[str, Tuple[str, str]]) -> str:
        """Generate complete KDL layout content."""
        self.validate_tab_config(tab_config)

        layout_content = self.LAYOUT_TEMPLATE
        for tab_name, (cwd, command) in tab_config.items():
            layout_content += "\n" + self.create_tab_section(tab_name, cwd, command)
        layout_content += "\n}\n"

        return layout_content

    def create_layout_file(self, tab_config: Dict[str, Tuple[str, str]],
                          output_dir: Path, session_name: str) -> str:
        """Create a layout file and return its absolute path."""
        self.validate_tab_config(tab_config)

        # Generate unique suffix for this layout
        random_suffix = self.generate_random_suffix()
        layout_content = self.generate_layout_content(tab_config)

        try:
            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)
            layout_file = output_dir / f"zellij_layout_{session_name}_{random_suffix}.kdl"

            # Write layout file
            layout_file.write_text(layout_content, encoding="utf-8")

            # Enhanced Rich logging
            console.print(f"[bold green]✅ Zellij layout file created:[/bold green] [cyan]{layout_file.absolute()}[/cyan]")
            return str(layout_file.absolute())

        except OSError as e:
            logger.error(f"Failed to create layout file: {e}")
            raise
