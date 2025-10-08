"""
TUI for navigating through machineconfig command structure using Textual.
"""

import re
import subprocess
from typing import Optional
from dataclasses import dataclass
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Tree, Static, Input, Label, Button
from textual.binding import Binding
from textual.screen import ModalScreen
from rich.panel import Panel
from rich.text import Text


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


class CommandBuilderScreen(ModalScreen[str]):
    """Modal screen for building command with arguments."""

    def __init__(self, command_info: CommandInfo) -> None:
        super().__init__()
        self.command_info = command_info
        self.arguments = self._parse_arguments()
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
                args.append(ArgumentInfo(name=arg_name, is_required=False, is_flag=False, placeholder=placeholder))
                seen_names.add(arg_name)
        
        flag_pattern = re.compile(r'--(\w+(?:-\w+)*)(?:\s|$)')
        for match in flag_pattern.finditer(help_text):
            arg_name = match.group(1)
            if arg_name not in seen_names:
                args.append(ArgumentInfo(name=arg_name, is_required=False, is_flag=True))
                seen_names.add(arg_name)
        
        positional_pattern = re.compile(r'<(\w+)>(?!\s*>)')
        for match in positional_pattern.finditer(help_text):
            arg_name = match.group(1)
            if arg_name not in seen_names and not re.search(rf'--\w+\s+<{arg_name}>', help_text):
                args.append(ArgumentInfo(name=arg_name, is_required=True, is_flag=False, placeholder=arg_name))
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
                        label_text = f"--{arg.name} (flag, leave empty to skip)"
                        yield Label(label_text)
                        input_widget = Input(placeholder="yes/no or leave empty", id=f"arg_{arg.name}")
                    else:
                        required_marker = "[red]*[/red]" if arg.is_required else "[dim](optional)[/dim]"
                        label_text = f"--{arg.name} {required_marker}"
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
        
        for arg in self.arguments:
            input_widget = self.input_widgets.get(arg.name)
            if input_widget:
                value = input_widget.value.strip()
                if value:
                    if arg.is_flag:
                        if value.lower() in ('yes', 'y', 'true', '1'):
                            parts.append(f"--{arg.name}")
                    else:
                        parts.append(f"--{arg.name} {value}")
        
        return " ".join(parts)


class CommandTree(Tree[CommandInfo]):
    """Tree widget for displaying command hierarchy."""

    def on_mount(self) -> None:
        """Build the command tree when mounted."""
        self.show_root = False
        self.guide_depth = 2
        self._build_command_tree()

    def _build_command_tree(self) -> None:
        """Build the hierarchical command structure."""
        
        # Main entry points
        devops_node = self.root.add("🛠️  devops - DevOps operations", data=CommandInfo(
            name="devops",
            description="DevOps operations",
            command="devops",
            is_group=True,
            module_path="machineconfig.scripts.python.devops"
        ))
        
        # devops subcommands
        devops_node.add("📦 install - Install essential packages", data=CommandInfo(
            name="install",
            description="Install essential packages",
            command="devops install",
            parent="devops",
            help_text="devops install --which <packages> --group <group> --interactive"
        ))
        
        repos_node = devops_node.add("📁 repos - Manage git repositories", data=CommandInfo(
            name="repos",
            description="Manage git repositories",
            command="devops repos",
            parent="devops",
            is_group=True,
            module_path="machineconfig.scripts.python.devops_helpers.cli_repos"
        ))
        
        # repos subcommands
        repos_node.add("🚀 push - Push changes across repositories", data=CommandInfo(
            name="push",
            description="Push changes across repositories",
            command="devops repos push",
            parent="repos",
            help_text="devops repos push --directory <dir> --recursive --no-sync"
        ))
        
        repos_node.add("⬇️ pull - Pull changes across repositories", data=CommandInfo(
            name="pull",
            description="Pull changes across repositories",
            command="devops repos pull",
            parent="repos",
            help_text="devops repos pull --directory <dir> --recursive --no-sync"
        ))
        
        repos_node.add("💾 commit - Commit changes across repositories", data=CommandInfo(
            name="commit",
            description="Commit changes across repositories",
            command="devops repos commit",
            parent="repos",
            help_text="devops repos commit --directory <dir> --recursive --no-sync"
        ))
        
        repos_node.add("🔄 sync - Sync changes across repositories", data=CommandInfo(
            name="sync",
            description="Pull, commit, and push changes across repositories",
            command="devops repos sync",
            parent="repos",
            help_text="devops repos sync --directory <dir> --recursive --no-sync"
        ))
        
        mirror_node = repos_node.add("🔄 mirror - Manage repository specifications", data=CommandInfo(
            name="mirror",
            description="Manage repository specifications and syncing",
            command="devops repos mirror",
            parent="repos",
            is_group=True
        ))
        
        mirror_node.add("📝 capture - Record repositories into repos.json", data=CommandInfo(
            name="capture",
            description="Record repositories into a repos.json specification",
            command="devops repos mirror capture",
            parent="mirror",
            help_text="devops repos mirror capture --directory <dir> --cloud <cloud>"
        ))
        
        mirror_node.add("📥 clone - Clone repositories from repos.json", data=CommandInfo(
            name="clone",
            description="Clone repositories described by repos.json",
            command="devops repos mirror clone",
            parent="mirror",
            help_text="devops repos mirror clone --directory <dir> --cloud <cloud>"
        ))
        
        mirror_node.add("🔀 checkout-to-commit - Check out specific commits", data=CommandInfo(
            name="checkout-to-commit",
            description="Check out specific commits listed in specification",
            command="devops repos mirror checkout-to-commit",
            parent="mirror",
            help_text="devops repos mirror checkout-to-commit --directory <dir> --cloud <cloud>"
        ))
        
        mirror_node.add("🔀 checkout-to-branch - Check out to main branch", data=CommandInfo(
            name="checkout-to-branch",
            description="Check out to the main branch defined in specification",
            command="devops repos mirror checkout-to-branch",
            parent="mirror",
            help_text="devops repos mirror checkout-to-branch --directory <dir> --cloud <cloud>"
        ))
        
        repos_node.add("🔍 analyze - Analyze repositories", data=CommandInfo(
            name="analyze",
            description="Analyze repositories in directory",
            command="devops repos analyze",
            parent="repos",
            help_text="devops repos analyze --directory <dir>"
        ))
        
        repos_node.add("🔐 secure - Securely sync git repository", data=CommandInfo(
            name="secure",
            description="Securely sync git repository to/from cloud with encryption",
            command="devops repos secure",
            parent="repos",
            help_text="devops repos secure <path> --cloud <cloud> --encrypt --decrypt"
        ))
        
        repos_node.add("🎬 viz - Visualize repository activity", data=CommandInfo(
            name="viz",
            description="Visualize repository activity using Gource",
            command="devops repos viz",
            parent="repos",
            help_text="devops repos viz --repo <path> --output <file> --resolution <res> --seconds-per-day <spd>"
        ))
        
        repos_node.add("🧹 cleanup - Clean repository directories", data=CommandInfo(
            name="cleanup",
            description="Clean repository directories from cache files",
            command="devops repos cleanup",
            parent="repos",
            help_text="devops repos cleanup --repo <path> --recursive"
        ))
        
        # config subcommands
        config_node = devops_node.add("⚙️  config - Configuration management", data=CommandInfo(
            name="config",
            description="Configuration subcommands",
            command="devops config",
            parent="devops",
            is_group=True
        ))
        
        config_node.add("🔗 private - Manage private configuration files", data=CommandInfo(
            name="private",
            description="Manage private configuration files",
            command="devops config private",
            parent="config",
            help_text="devops config private --method <symlink|copy> --on-conflict <action> --which <items> --interactive"
        ))
        
        config_node.add("🔗 public - Manage public configuration files", data=CommandInfo(
            name="public",
            description="Manage public configuration files",
            command="devops config public",
            parent="config",
            help_text="devops config public --method <symlink|copy> --on-conflict <action> --which <items> --interactive"
        ))
        
        config_node.add("🔗 dotfile - Manage dotfiles", data=CommandInfo(
            name="dotfile",
            description="Manage dotfiles",
            command="devops config dotfile",
            parent="config",
            help_text="devops config dotfile <file> --overwrite --dest <destination>"
        ))
        
        config_node.add("🔗 shell - Configure shell profile", data=CommandInfo(
            name="shell",
            description="Configure your shell profile",
            command="devops config shell",
            parent="config",
            help_text="devops config shell <copy|reference>"
        ))
        
        config_node.add("🔗 pwsh_theme - Configure PowerShell theme", data=CommandInfo(
            name="pwsh_theme",
            description="Configure your PowerShell theme",
            command="devops config pwsh_theme",
            parent="config",
            help_text="devops config pwsh_theme"
        ))
        
        # data subcommands
        data_node = devops_node.add("💾 data - Data operations", data=CommandInfo(
            name="data",
            description="Data subcommands",
            command="devops data",
            parent="devops",
            is_group=True
        ))
        
        data_node.add("💾 backup - Backup data", data=CommandInfo(
            name="backup",
            description="Backup data",
            command="devops data backup",
            parent="data",
            help_text="devops data backup"
        ))
        
        data_node.add("📥 retrieve - Retrieve data", data=CommandInfo(
            name="retrieve",
            description="Retrieve data from backup",
            command="devops data retrieve",
            parent="data",
            help_text="devops data retrieve"
        ))
        
        # network subcommands
        network_node = devops_node.add("🔐 network - Network operations", data=CommandInfo(
            name="network",
            description="Network subcommands",
            command="devops network",
            parent="devops",
            is_group=True
        ))
        
        network_node.add("📡 share-terminal - Share terminal via web", data=CommandInfo(
            name="share-terminal",
            description="Share terminal via web browser",
            command="devops network share-terminal",
            parent="network",
            help_text="devops network share-terminal"
        ))
        
        network_node.add("� install_ssh_server - Install SSH server", data=CommandInfo(
            name="install_ssh_server",
            description="Install SSH server",
            command="devops network install_ssh_server",
            parent="network",
            help_text="devops network install_ssh_server"
        ))
        
        network_node.add("� add_ssh_key - Add SSH public key", data=CommandInfo(
            name="add_ssh_key",
            description="Add SSH public key to this machine",
            command="devops network add_ssh_key",
            parent="network",
            help_text="devops network add_ssh_key --path <file> --choose --value --github <username>"
        ))
        
        network_node.add("�️  add_ssh_identity - Add SSH identity", data=CommandInfo(
            name="add_ssh_identity",
            description="Add SSH identity (private key) to this machine",
            command="devops network add_ssh_identity",
            parent="network",
            help_text="devops network add_ssh_identity"
        ))
        
        # self subcommands
        self_node = devops_node.add("🔄 self - SELF operations", data=CommandInfo(
            name="self",
            description="SELF operations subcommands",
            command="devops self",
            parent="devops",
            is_group=True
        ))
        
        self_node.add("🔄 update - Update essential repos", data=CommandInfo(
            name="update",
            description="Update essential repos",
            command="devops self update",
            parent="self",
            help_text="devops self update"
        ))
        
        self_node.add("🤖 interactive - Interactive configuration", data=CommandInfo(
            name="interactive",
            description="Interactive configuration of machine",
            command="devops self interactive",
            parent="self",
            help_text="devops self interactive"
        ))
        
        self_node.add("📊 status - Machine status", data=CommandInfo(
            name="status",
            description="Status of machine, shell profile, apps, symlinks, dotfiles, etc.",
            command="devops self status",
            parent="self",
            help_text="devops self status"
        ))
        
        self_node.add("📋 clone - Clone machineconfig", data=CommandInfo(
            name="clone",
            description="Clone machineconfig locally and incorporate to shell profile",
            command="devops self clone",
            parent="self",
            help_text="devops self clone"
        ))
        
        self_node.add("📚 navigate - Navigate command structure", data=CommandInfo(
            name="navigate",
            description="Navigate command structure with TUI",
            command="devops self navigate",
            parent="self",
            help_text="devops self navigate"
        ))
        
        # fire command
        self.root.add("🔥 fire - Fire jobs execution", data=CommandInfo(
            name="fire",
            description="Execute Python scripts with Fire",
            command="fire",
            is_group=False,
            module_path="machineconfig.scripts.python.fire_jobs",
            help_text="fire <path> [function] --ve <env> --interactive --jupyter --streamlit --debug --loop --remote --zellij_tab <name>"
        ))
        
        # agents command
        agents_node = self.root.add("🤖 agents - AI Agents management", data=CommandInfo(
            name="agents",
            description="AI Agents management subcommands",
            command="agents",
            is_group=True,
            module_path="machineconfig.scripts.python.agents"
        ))
        
        agents_node.add("✨ create - Create AI agent", data=CommandInfo(
            name="create",
            description="Create a new AI agent",
            command="agents create",
            parent="agents",
            help_text="agents create --context-path <file> --keyword-search <term> --filename-pattern <pattern> --agent <type> --machine <target> --model <model> --provider <provider> --prompt <text> --prompt-path <file> --job-name <name> --tasks-per-prompt <num> --separate-prompt-from-context --output-path <file> --agents-dir <dir>"
        ))
        
        agents_node.add("📦 collect - Collect agent data", data=CommandInfo(
            name="collect",
            description="Collect agent data",
            command="agents collect",
            parent="agents",
            help_text="agents collect --agent-dir <dir> --output-path <file> --separator <sep>"
        ))
        
        agents_node.add("📝 make-template - Create agent template", data=CommandInfo(
            name="make-template",
            description="Create a template for fire agents",
            command="agents make-template",
            parent="agents",
            help_text="agents make-template"
        ))
        
        agents_node.add("⚙️  make-config - Initialize AI configurations", data=CommandInfo(
            name="make-config",
            description="Initialize AI configurations in the current repository",
            command="agents make-config",
            parent="agents",
            help_text="agents make-config"
        ))
        
        agents_node.add("📝 make-todo - Generate todo markdown", data=CommandInfo(
            name="make-todo",
            description="Generate a markdown file listing all Python files in the repo",
            command="agents make-todo",
            parent="agents",
            help_text="agents make-todo"
        ))
        
        # sessions command
        sessions_node = self.root.add("🖥️  sessions - Session layouts management", data=CommandInfo(
            name="sessions",
            description="Layouts management subcommands",
            command="sessions",
            is_group=True,
            module_path="machineconfig.scripts.python.sessions"
        ))
        
        sessions_node.add("✨ create-from-function - Create layout from function", data=CommandInfo(
            name="create-from-function",
            description="Create layout from function",
            command="sessions create-from-function",
            parent="sessions",
            help_text="sessions create-from-function"
        ))
        
        sessions_node.add("▶️  run - Run session layout", data=CommandInfo(
            name="run",
            description="Run session layout",
            command="sessions run",
            parent="sessions",
            help_text="sessions run --layout-path <file> --max-tabs <num> --max-layouts <num> --sleep-inbetween <sec> --monitor --parallel --kill-upon-completion --choose <names> --choose-interactively"
        ))
        
        sessions_node.add("⚖️  balance-load - Balance load", data=CommandInfo(
            name="balance-load",
            description="Balance load across sessions",
            command="sessions balance-load",
            parent="sessions",
            help_text="sessions balance-load --layout-path <file> --max-thresh <num> --thresh-type <number|weight> --breaking-method <moreLayouts|combineTabs> --output-path <file>"
        ))
        
        # cloud command
        cloud_node = self.root.add("☁️  cloud - Cloud storage operations", data=CommandInfo(
            name="cloud",
            description="Cloud storage operations",
            command="cloud",
            is_group=True,
            module_path="machineconfig.scripts.python.cloud"
        ))
        
        cloud_node.add("🔄 sync - Synchronize with cloud", data=CommandInfo(
            name="sync",
            description="Synchronize files/folders between local and cloud storage",
            command="cloud sync",
            parent="cloud",
            help_text="cloud sync <source> <target> --cloud <provider> --recursive --exclude <patterns>"
        ))
        
        cloud_node.add("📤 copy - Copy to/from cloud", data=CommandInfo(
            name="copy",
            description="Copy files/folders to/from cloud storage",
            command="cloud copy",
            parent="cloud",
            help_text="cloud copy <source> <target> --cloud <provider> --recursive --exclude <patterns>"
        ))
        
        cloud_node.add("🔗 mount - Mount cloud storage", data=CommandInfo(
            name="mount",
            description="Mount cloud storage as local drive",
            command="cloud mount",
            parent="cloud",
            help_text="cloud mount <remote> <mount_point> --cloud <provider> --daemon --allow-other"
        ))
        
        # croshell command
        self.root.add("� croshell - Interactive shell", data=CommandInfo(
            name="croshell",
            description="Interactive shell with various options",
            command="croshell",
            is_group=False,
            module_path="machineconfig.scripts.python.croshell",
            help_text="croshell --python --fzf --ve <env> --profile <profile> --read <file> --jupyter --streamlit --visidata"
        ))
        
        # ftpx command
        self.root.add("📡 ftpx - File transfer", data=CommandInfo(
            name="ftpx",
            description="File transfer between machines",
            command="ftpx",
            is_group=False,
            module_path="machineconfig.scripts.python.ftpx",
            help_text="ftpx <source> <target> --recursive --zipFirst --cloud"
        ))
        
        # kill_process command
        self.root.add("💀 kill_process - Kill processes", data=CommandInfo(
            name="kill_process",
            description="Kill running processes",
            command="kill_process",
            is_group=False,
            module_path="machineconfig.utils.procs",
            help_text="kill_process"
        ))


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


class SearchBar(Horizontal):
    """Search bar widget."""
    
    def compose(self) -> ComposeResult:
        yield Label("🔍 Search: ", classes="search-label")
        yield Input(placeholder="Type to search commands...", id="search-input")


class CommandNavigatorApp(App[None]):
    """TUI application for navigating machineconfig commands."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-rows: auto 1fr auto;
    }
    
    Header {
        column-span: 2;
        background: $boost;
        color: $text;
    }
    
    #search-bar {
        column-span: 2;
        padding: 1;
        background: $surface;
        height: auto;
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
    }
    
    #command-detail {
        row-span: 1;
        border: solid $primary;
        padding: 1;
    }
    
    Footer {
        column-span: 2;
        background: $boost;
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


if __name__ == "__main__":
    app = CommandNavigatorApp()
    app.run()
