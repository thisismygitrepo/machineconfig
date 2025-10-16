#!/usr/bin/env python3
from typing import Optional
from pathlib import Path
import logging

from rich.console import Console

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.cluster.sessions_managers.zellij_utils.monitoring_types import ComprehensiveStatus, CommandStatus
from machineconfig.cluster.sessions_managers.zellij_utils.zellij_local_helper import validate_layout_config, create_tab_section, check_command_status, check_zellij_session_status
from machineconfig.cluster.sessions_managers.zellij_utils.zellij_local_helper_restart import restart_tab_process


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


DEFAULT_LAYOUT_TEMPLATE = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""


def create_zellij_layout(layout_config: LayoutConfig, layout_template: str) -> str:
    """Standalone function to create Zellij layout content from config."""
    validate_layout_config(layout_config)
    # Enhanced Rich logging
    tab_count = len(layout_config["layoutTabs"])
    layout_name = layout_config["layoutName"]
    console.print(f"[bold cyan]📋 Creating Zellij layout[/bold cyan] [bright_green]'{layout_name}' with {tab_count} tabs[/bright_green]")

    # Display tab summary with emojis and colors
    for tab in layout_config["layoutTabs"]:
        console.print(f"  [yellow]→[/yellow] [bold]{tab['tabName']}[/bold] [dim]in[/dim] [blue]{tab['startDir']}[/blue]")
    from copy import deepcopy
    layout_config = deepcopy(layout_config)  # Avoid mutating the original
    layout_content = layout_template
    for tab in layout_config["layoutTabs"]:
        layout_content += "\n" + create_tab_section(tab)
    layout_content += "\n}\n"

    console.print("[bold green]✅ Zellij layout content generated[/bold green]")
    return layout_content


class ZellijLayoutGenerator:
    def __init__(self, layout_config: LayoutConfig, session_name: str):
        self.session_name: str = session_name
        self.layout_config: LayoutConfig = layout_config.copy()
        self.layout_path: Optional[str] = None
    def create_layout_file(self) -> bool:
        """Create zellij layout file and return the path."""
        layout_content = create_zellij_layout(self.layout_config, layout_template=DEFAULT_LAYOUT_TEMPLATE)
        # Write to file
        tmp_dir = Path.home() / "tmp_results" / "sessions" / "zellij_layouts"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        import tempfile
        layout_file = Path(tempfile.mkstemp(suffix="_layout.kdl", dir=tmp_dir)[1])
        layout_file.write_text(layout_content, encoding="utf-8")
        self.layout_path = str(layout_file.absolute())

        console.print(f"[bold green]✅ Layout created successfully:[/bold green] [cyan]{self.layout_path}[/cyan]")
        return True

    def check_all_commands_status(self) -> dict[str, CommandStatus]:
        if not self.layout_config:
            logger.warning("No layout config tracked. Make sure to create a layout first.")
            return {}

        status_report: dict[str, CommandStatus] = {}
        for tab in self.layout_config["layoutTabs"]:
            tab_name = tab["tabName"]
            status_report[tab_name] = check_command_status(tab_name, self.layout_config)

        return status_report

    def get_comprehensive_status(self) -> ComprehensiveStatus:
        zellij_status = check_zellij_session_status(self.session_name or "default")
        commands_status = self.check_all_commands_status()
        running_count = sum(1 for status in commands_status.values() if status.get("running", False))
        total_count = len(commands_status)
        return {"zellij_session": zellij_status, "commands": commands_status, "summary": {"total_commands": total_count, "running_commands": running_count, "stopped_commands": total_count - running_count, "session_healthy": zellij_status.get("session_exists", False)}}

    def print_status_report(self) -> None:
        from rich.panel import Panel
        from rich.table import Table

        status = self.get_comprehensive_status()

        # Create main panel
        console.print()
        console.print(Panel.fit("🔍 ZELLIJ LAYOUT STATUS REPORT", style="bold cyan"))

        # Zellij session status
        zellij = status["zellij_session"]
        if zellij.get("zellij_running", False):
            if zellij.get("session_exists", False):
                console.print(f"[bold green]✅ Zellij session[/bold green] [yellow]'{self.session_name}'[/yellow] [green]is running[/green]")
            else:
                console.print(f"[bold yellow]⚠️  Zellij is running but session[/bold yellow] [yellow]'{self.session_name}'[/yellow] [yellow]not found[/yellow]")
        else:
            error_msg = zellij.get("error", "Unknown error")
            console.print(f"[bold red]❌ Zellij session issue:[/bold red] [red]{error_msg}[/red]")

        console.print()

        # Commands status table
        table = Table(title="📋 COMMAND STATUS", show_header=True, header_style="bold magenta")
        table.add_column("Tab", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("PID", justify="center", style="dim")
        table.add_column("Memory", justify="center", style="blue")
        table.add_column("Command", style="green", max_width=40)

        for tab_name, cmd_status in status["commands"].items():
            # Determine status display
            if cmd_status.get("running", False):
                status_text = "[bold green]✅ Running[/bold green]"
                processes = cmd_status.get("processes", [])
                if processes:
                    proc = processes[0]  # Show first process
                    pid = str(proc.get("pid", "N/A"))
                    memory = f"{proc.get('memory_mb', 0):.1f}MB" if proc.get("memory_mb") else "N/A"
                else:
                    pid = "N/A"
                    memory = "N/A"
            else:
                status_text = "[bold red]❌ Stopped[/bold red]"
                pid = "N/A"
                memory = "N/A"

            command = cmd_status.get("command", "Unknown")
            # Truncate long commands
            if len(command) > 35:
                command = command[:32] + "..."

            table.add_row(tab_name, status_text, pid, memory, command)

        console.print(table)
        console.print()

        # Enhanced summary
        summary = status["summary"]
        from rich.panel import Panel

        summary_text = f"""[bold]Total commands:[/bold] {summary["total_commands"]}
[green]Running:[/green] {summary["running_commands"]}
[red]Stopped:[/red] {summary["stopped_commands"]}
[yellow]Session healthy:[/yellow] {"✅" if summary["session_healthy"] else "❌"}"""

        console.print(Panel(summary_text, title="📊 Summary", style="blue"))

    def restart_tab(self, tab_name: str) -> bool:
        """Restart the process running in a specific tab without changing the layout.
        
        This method will:
        1. Navigate to the specified tab
        2. Send Ctrl+C to stop the running process
        3. Clear the screen
        4. Re-execute the original command
        
        The tab layout and configuration remain unchanged - only the process is restarted.
        """
        return restart_tab_process(tab_name=tab_name, layout_config=self.layout_config, session_name=self.session_name)

    def run(self):
        from machineconfig.cluster.sessions_managers.helpers.enhanced_command_runner import enhanced_zellij_session_start
        enhanced_zellij_session_start(session_name=self.session_name, layout_path=str(self.layout_path))


def run_zellij_layout(layout_config: LayoutConfig) -> None:
    session_name = layout_config["layoutName"]
    generator = ZellijLayoutGenerator(layout_config, session_name)
    generator.create_layout_file()
    generator.run()


def run_command_in_zellij_tab(command: str, tab_name: str, cwd: Optional[str]) -> str:
    maybe_cwd = f"--cwd {cwd}" if cwd is not None else ""
    return f"""
echo "Sleep 1 seconds to allow zellij to create a new tab"
sleep 1
zellij action new-tab --name {tab_name} {maybe_cwd}
echo "Sleep 2 seconds to allow zellij to go to the new tab"
sleep 2
zellij action go-to-tab-name {tab_name}
echo "Sleep 2 seconds to allow zellij to start the new pane"
sleep 2
zellij action new-pane --direction down -- /bin/bash {command}
echo "Sleep 2 seconds to allow zellij to start the new pane"
sleep 1
zellij action move-focus up; sleep 2
echo "Sleep 2 seconds to allow zellij to close the pane"
sleep 1
zellij action close-pane; sleep 2
"""


if __name__ == "__main__":
    # Example usage with new schema
    sample_layout: LayoutConfig = {
        "layoutName": "SampleBots",
        "layoutTabs": [{"tabName": "Explorer", "startDir": "~/code", "command": "lf"}, {"tabName": "🤖Bot2", "startDir": "~", "command": "cmatrix"}, {"tabName": "📊Monitor", "startDir": "~", "command": "htop"}, {"tabName": "📝Logs", "startDir": "/var/log", "command": "tail -f /var/log/app.log"}],
    }
    try:
        # Create layout using the generator with new design
        generator = ZellijLayoutGenerator(layout_config=sample_layout, session_name="test_session")
        generator.create_layout_file()

        generator.run()
        # Demonstrate status checking
        print("\n🔍 Checking command status (this is just a demo - commands aren't actually running):")
        generator.print_status_report()

        # Individual command status check
        print("\n🔎 Individual command status for 🤖Bot2:")
        bot2_status = check_command_status("🤖Bot2", generator.layout_config)
        print(f"Status: {bot2_status['status']}")
        print(f"Running: {bot2_status['running']}")

    except Exception as e:
        print(f"❌ Error: {e}")
