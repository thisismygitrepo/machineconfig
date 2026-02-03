"""
Main TUI application for navigating machineconfig commands.
"""

import subprocess
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Tree
from textual.binding import Binding
from machineconfig.scripts.python.helpers.helpers_navigator.command_builder import CommandBuilderScreen
from machineconfig.scripts.python.helpers.helpers_navigator.command_tree import CommandTree
from machineconfig.scripts.python.helpers.helpers_navigator.command_detail import CommandDetail
from machineconfig.scripts.python.helpers.helpers_navigator.search_bar import SearchBar
from machineconfig.scripts.python.helpers.helpers_navigator.data_models import CommandInfo


class CommandNavigatorApp(App[None]):
    """TUI application for navigating machineconfig commands."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-rows: auto 1fr auto;
        grid-columns: 1fr 1fr;
        height: 100%;
        width: 100%;
    }

    Header {
        column-span: 2;
        background: $boost;
        color: $text;
        width: 100%;
    }

    #search-bar {
        column-span: 2;
        padding: 1;
        background: $surface;
        height: auto;
        width: 100%;
    }

    .search-label {
        width: auto;
        padding-right: 1;
    }

    #search-input {
        width: 1fr;
    }

    #command-tree {
        row-span: 1;
        border: solid $primary;
        padding: 1;
        width: 100%;
        height: 100%;
    }

    #command-detail {
        row-span: 1;
        border: solid $primary;
        padding: 1;
        width: 100%;
        height: 100%;
    }

    Footer {
        column-span: 2;
        background: $boost;
        width: 100%;
    }

    Button {
        margin: 1;
    }

    CommandBuilderScreen {
        align: center middle;
    }

    CommandBuilderScreen > VerticalScroll {
        width: 80;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    CommandBuilderScreen .title {
        margin-bottom: 1;
    }

    CommandBuilderScreen Label {
        margin-top: 1;
        margin-bottom: 0;
    }

    CommandBuilderScreen Input {
        margin-bottom: 1;
    }

    CommandBuilderScreen .buttons {
        margin-top: 2;
        height: auto;
        align: center middle;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("c", "copy_command", "Copy Command"),
        Binding("/", "focus_search", "Search"),
        Binding("?", "help", "Help"),
        Binding("r", "run_command", "Run Command"),
        Binding("b", "build_command", "Build Command"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield SearchBar(id="search-bar")
        yield CommandTree("📚 machineconfig Commands", id="command-tree")
        yield CommandDetail(id="command-detail")
        yield Footer()

    def on_mount(self) -> None:
        """Actions when app is mounted."""
        self.title = "machineconfig Command Navigator"
        self.sub_title = "Navigate and explore all available commands"
        tree = self.query_one(CommandTree)
        tree.focus()

    def on_tree_node_selected(self, event: Tree.NodeSelected[CommandInfo]) -> None:
        """Handle tree node selection."""
        command_info = event.node.data
        detail_widget = self.query_one("#command-detail", CommandDetail)
        detail_widget.update_command(command_info)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id != "search-input":
            return

        search_term = event.value.lower()
        tree = self.query_one(CommandTree)

        if not search_term:
            # Show all nodes - expand all root children
            for node in tree.root.children:
                node.expand()
            return

        # Filter nodes based on search term
        def filter_tree(node):  # type: ignore
            if node.data and not node.data.is_group:
                match = (search_term in node.data.name.lower() or
                        search_term in node.data.description.lower() or
                        search_term in node.data.command.lower())
                return match
            return False

        # Expand parents of matching nodes by walking through all nodes
        def walk_nodes(node):  # type: ignore
            """Recursively walk through tree nodes."""
            yield node
            for child in node.children:
                yield from walk_nodes(child)

        for node in walk_nodes(tree.root):
            if filter_tree(node):
                parent = node.parent
                while parent and parent != tree.root:
                    parent.expand()
                    parent = parent.parent  # type: ignore

    def action_copy_command(self) -> None:
        """Copy the selected command to clipboard."""
        tree = self.query_one(CommandTree)
        if tree.cursor_node and tree.cursor_node.data:
            command = tree.cursor_node.data.command
            try:
                import pyperclip  # type: ignore
                pyperclip.copy(command)
                self.notify(f"Copied: {command}", severity="information")
            except ImportError:
                self.notify("Install pyperclip to enable clipboard support", severity="warning")

    def action_run_command(self) -> None:
        """Run the selected command without arguments."""
        tree = self.query_one(CommandTree)
        if tree.cursor_node and tree.cursor_node.data:
            command_info = tree.cursor_node.data
            if command_info.is_group:
                self.notify("Cannot run command groups directly", severity="warning")
                return

            self._execute_command(command_info.command)

    def action_build_command(self) -> None:
        """Open command builder for selected command."""
        tree = self.query_one(CommandTree)
        if tree.cursor_node and tree.cursor_node.data:
            command_info = tree.cursor_node.data
            if command_info.is_group:
                self.notify("Cannot build command for groups", severity="warning")
                return

            self.push_screen(CommandBuilderScreen(command_info), self._handle_builder_result)

    def _handle_builder_result(self, result: str | None) -> None:
        """Handle result from command builder."""
        if not result:
            return

        if result.startswith("EXECUTE:"):
            command = result[8:]
            self._execute_command(command)
        elif result.startswith("COPY:"):
            command = result[5:]
            self._copy_to_clipboard(command)

    def _execute_command(self, command: str) -> None:
        """Execute a shell command."""
        try:
            self.notify(f"Executing: {command}", severity="information")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    self.notify(f"Success: {output[:100]}...", severity="information", timeout=5)
                else:
                    self.notify("Command executed successfully", severity="information")
            else:
                error = result.stderr.strip() or "Unknown error"
                self.notify(f"Error: {error[:100]}...", severity="error", timeout=10)
        except subprocess.TimeoutExpired:
            self.notify("Command timed out after 30 seconds", severity="warning")
        except Exception as e:
            self.notify(f"Failed to execute: {str(e)}", severity="error")

    def _copy_to_clipboard(self, command: str) -> None:
        """Copy command to clipboard."""
        try:
            import pyperclip  # type: ignore
            pyperclip.copy(command)
            self.notify(f"Copied: {command}", severity="information")
        except ImportError:
            self.notify("Install pyperclip to enable clipboard support", severity="warning")

    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()

    def action_help(self) -> None:
        """Show help information."""
        help_text = """
        Navigation:
        - ↑↓: Navigate tree
        - Enter: Expand/collapse node
        - /: Focus search
        - c: Copy command to clipboard
        - r: Run command directly (no args)
        - b: Build command with arguments
        - q: Quit
        - ?: Show this help
        """
        self.notify(help_text, severity="information", timeout=10)