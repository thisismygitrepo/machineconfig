"""
Command builder screen for building commands with arguments.
"""

import re
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static, Input, Label, Button
from textual.screen import ModalScreen
from machineconfig.scripts.python.helpers.helpers_navigator.data_models import CommandInfo, ArgumentInfo


class CommandBuilderScreen(ModalScreen[str]):
    """Modal screen for building command with arguments."""

    def __init__(self, command_info: CommandInfo) -> None:
        super().__init__()
        self.command_info = command_info
        self.arguments = (
            command_info.arguments
            if command_info.arguments is not None
            else self._parse_arguments()
        )
        self.input_widgets: dict[str, Input] = {}

    def _parse_arguments(self) -> list[ArgumentInfo]:
        """Parse arguments from help_text."""
        args: list[ArgumentInfo] = []
        seen_names: set[str] = set()

        if not self.command_info.help_text:
            return args

        help_text = self.command_info.help_text

        optional_pattern = re.compile(r'--(\w+(?:-\w+)*)\s+<([^>]+)>')
        for match in optional_pattern.finditer(help_text):
            arg_name = match.group(1)
            placeholder = match.group(2)
            if arg_name not in seen_names:
                args.append(ArgumentInfo(
                    name=arg_name,
                    is_required=False,
                    is_flag=False,
                    placeholder=placeholder,
                    flag=f"--{arg_name}",
                    long_flags=[f"--{arg_name}"],
                ))
                seen_names.add(arg_name)

        flag_pattern = re.compile(r'--(\w+(?:-\w+)*)(?:\s|$)')
        for match in flag_pattern.finditer(help_text):
            arg_name = match.group(1)
            if arg_name not in seen_names:
                args.append(ArgumentInfo(
                    name=arg_name,
                    is_required=False,
                    is_flag=True,
                    flag=f"--{arg_name}",
                    long_flags=[f"--{arg_name}"],
                ))
                seen_names.add(arg_name)

        positional_pattern = re.compile(r'<(\w+)>(?!\s*>)')
        for match in positional_pattern.finditer(help_text):
            arg_name = match.group(1)
            if arg_name not in seen_names and not re.search(rf'--\w+\s+<{arg_name}>', help_text):
                args.append(ArgumentInfo(
                    name=arg_name,
                    is_required=True,
                    is_flag=False,
                    placeholder=arg_name,
                    is_positional=True,
                ))
                seen_names.add(arg_name)

        return args

    def compose(self) -> ComposeResult:
        """Compose the modal screen."""
        with VerticalScroll():
            yield Static(f"[bold cyan]Build Command: {self.command_info.command}[/bold cyan]\n", classes="title")

            if not self.arguments:
                yield Static("[yellow]No arguments needed for this command[/yellow]\n")
            else:
                for arg in self.arguments:
                    if arg.is_flag:
                        flag = arg.flag or f"--{arg.name}"
                        if arg.negated_flag:
                            label_text = f"{flag} / {arg.negated_flag} (flag, leave empty to skip)"
                        else:
                            label_text = f"{flag} (flag, leave empty to skip)"
                        yield Label(label_text)
                        input_widget = Input(placeholder="yes/no or leave empty", id=f"arg_{arg.name}")
                    elif arg.is_positional:
                        required_marker = "[red]*[/red]" if arg.is_required else "[dim](optional)[/dim]"
                        label_text = f"{arg.name} {required_marker}"
                        yield Label(label_text)
                        input_widget = Input(placeholder=arg.placeholder or arg.name, id=f"arg_{arg.name}")
                    else:
                        flag = arg.flag or f"--{arg.name}"
                        required_marker = "[red]*[/red]" if arg.is_required else "[dim](optional)[/dim]"
                        label_text = f"{flag} {required_marker}"
                        yield Label(label_text)
                        input_widget = Input(placeholder=arg.placeholder or arg.name, id=f"arg_{arg.name}")

                    self.input_widgets[arg.name] = input_widget
                    yield input_widget

            with Horizontal(classes="buttons"):
                yield Button("Execute", variant="primary", id="execute")
                yield Button("Copy", variant="success", id="copy")
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel":
            self.dismiss("")
            return

        built_command = self._build_command()

        if event.button.id == "execute":
            self.dismiss(f"EXECUTE:{built_command}")
        elif event.button.id == "copy":
            self.dismiss(f"COPY:{built_command}")

    def _build_command(self) -> str:
        """Build the complete command with arguments."""
        parts = [self.command_info.command]
        yes_values = {"yes", "y", "true", "1", "on"}
        no_values = {"no", "n", "false", "0", "off"}

        for arg in self.arguments:
            input_widget = self.input_widgets.get(arg.name)
            if input_widget:
                value = input_widget.value.strip()
                if value:
                    if arg.is_positional:
                        parts.append(value)
                        continue

                    if arg.is_flag:
                        flag_value = value.lower()
                        flag = arg.flag or f"--{arg.name}"
                        if flag_value in yes_values:
                            parts.append(flag)
                        elif flag_value in no_values:
                            if arg.negated_flag:
                                parts.append(arg.negated_flag)
                        elif value.startswith("-"):
                            parts.append(value)
                        continue

                    flag = arg.flag or f"--{arg.name}"
                    parts.append(f"{flag} {value}")

        return " ".join(parts)
