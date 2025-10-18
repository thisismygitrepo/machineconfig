"""
Command detail widget for displaying command information.
"""

from typing import Optional
from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text
from machineconfig.scripts.python.helpers_navigator.data_models import CommandInfo


class CommandDetail(Static):
    """Widget for displaying command details."""

    def __init__(self, *, id: str) -> None:  # type: ignore
        super().__init__(id=id)
        self.command_info: Optional[CommandInfo] = None

    def update_command(self, command_info: Optional[CommandInfo]) -> None:
        """Update displayed command information."""
        self.command_info = command_info
        if command_info is None:
            self.update("Select a command to view details")
            return

        content = Text()
        content.append(f"{'🗂️  Group' if command_info.is_group else '⚡ Command'}: ", style="bold cyan")
        content.append(f"{command_info.name}\n\n", style="bold yellow")

        content.append("Description: ", style="bold green")
        content.append(f"{command_info.description}\n\n", style="white")

        content.append("Command: ", style="bold blue")
        content.append(f"{command_info.command}\n\n", style="bold white")

        if command_info.help_text:
            content.append("Usage: ", style="bold magenta")
            content.append(f"{command_info.help_text}\n\n", style="white")

        if command_info.module_path:
            content.append("Module: ", style="bold red")
            content.append(f"{command_info.module_path}\n", style="white")

        self.update(Panel(content, title=f"[bold]{command_info.name}[/bold]", border_style="blue"))