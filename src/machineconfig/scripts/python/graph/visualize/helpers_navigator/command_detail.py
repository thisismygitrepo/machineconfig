"""
Command detail widget for displaying command information.
"""

from typing import Optional
from textual.widgets import Static
from rich.text import Text
from rich.panel import Panel
from rich.console import Group
from rich.table import Table
from rich import box
from machineconfig.scripts.python.helpers.helpers_navigator.data_models import CommandInfo


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

        if command_info.is_group:
            self.update(self._render_group(command_info))
            return

        self.update(self._render_command(command_info))

    def _render_group(self, command_info: CommandInfo) -> Panel:
        content = Text()
        content.append("Group: ", style="bold cyan")
        content.append(f"{command_info.name}\n\n", style="bold yellow")

        content.append("Description: ", style="bold green")
        content.append(f"{command_info.long_description or command_info.description}\n\n", style="white")

        content.append("Command: ", style="bold blue")
        content.append(f"{command_info.command}\n\n", style="bold white")

        if command_info.module_path:
            content.append("Module: ", style="bold red")
            content.append(f"{command_info.module_path}\n", style="white")

        return Panel(content, title=f"[bold]{command_info.name}[/bold]", border_style="blue")

    def _render_command(self, command_info: CommandInfo) -> Panel:
        renderables = []
        usage_text = Text()
        usage_text.append("Usage: ", style="bold cyan")
        usage_text.append(self._format_usage(command_info), style="white")
        renderables.append(usage_text)

        description = command_info.long_description or command_info.description
        if description:
            renderables.append(Text(description, style="green"))

        arguments = command_info.arguments or []
        positional_args = [arg for arg in arguments if arg.is_positional]
        option_args = [arg for arg in arguments if not arg.is_positional]

        if positional_args:
            renderables.append(self._build_arguments_table(positional_args))

        renderables.append(self._build_options_table(option_args))

        if command_info.module_path:
            renderables.append(Text(f"Module: {command_info.module_path}", style="dim"))

        content = Group(*renderables)
        return Panel(content, title=f"[bold]{command_info.name}[/bold]", border_style="blue")

    def _format_usage(self, command_info: CommandInfo) -> str:
        arguments = command_info.arguments or []
        positional_args = [arg for arg in arguments if arg.is_positional]
        option_args = [arg for arg in arguments if not arg.is_positional]

        parts = [command_info.command or command_info.name]
        if option_args:
            parts.append("[OPTIONS]")

        for arg in positional_args:
            placeholder = self._placeholder(arg)
            token = placeholder if arg.is_required else f"[{placeholder}]"
            parts.append(token)

        usage = " ".join(parts).strip()
        return usage or command_info.help_text or command_info.name

    def _build_arguments_table(self, arguments) -> Table:  # type: ignore
        table = Table(box=box.MINIMAL, show_header=False, pad_edge=False)
        table.add_column("Argument", style="bold cyan", no_wrap=True)
        table.add_column("Description", style="white")

        for arg in arguments:
            placeholder = self._placeholder(arg)
            token = f"{arg.name} {placeholder}" if arg.is_required else f"{arg.name} [{placeholder}]"
            table.add_row(token, arg.description or "")

        table.title = "Arguments"
        table.title_style = "bold green"
        return table

    def _build_options_table(self, options) -> Table:  # type: ignore
        table = Table(box=box.MINIMAL, show_header=False, pad_edge=False)
        table.add_column("Option", style="bold cyan", no_wrap=True)
        table.add_column("Description", style="white")

        for opt in options:
            flag_text = self._format_option_flags(opt)
            if not opt.is_flag:
                placeholder = self._placeholder(opt)
                flag_text = f"{flag_text} <{placeholder}>"
            table.add_row(flag_text, opt.description or "")

        table.add_row("--help", "Show this message and exit.")
        table.title = "Options"
        table.title_style = "bold magenta"
        return table

    def _format_option_flags(self, arg) -> str:  # type: ignore
        parts = []
        if arg.long_flags:
            parts.append(self._combine_flags(arg.long_flags))
        if arg.short_flags:
            parts.append(self._combine_flags(arg.short_flags))

        if not parts:
            if arg.flag and arg.negated_flag:
                parts.append(f"{arg.flag} / {arg.negated_flag}")
            elif arg.flag:
                parts.append(arg.flag)
            else:
                parts.append(f"--{arg.name.replace('_', '-')}")

        return ", ".join(parts)

    def _combine_flags(self, flags) -> str:  # type: ignore
        if len(flags) == 2 and self._is_negative_flag(flags[1]) and not self._is_negative_flag(flags[0]):
            return f"{flags[0]} / {flags[1]}"
        return ", ".join(flags)

    def _is_negative_flag(self, flag: str) -> bool:
        token = flag.lstrip("-")
        return token.startswith("no-")

    def _placeholder(self, arg) -> str:  # type: ignore
        return (arg.placeholder or arg.name).upper()
