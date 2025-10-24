#!/usr/bin/env python3
"""
Windows Terminal local layout generator and session manager.
Equivalent to zellij_local.py but for Windows Terminal.

https://github.com/ruby9455/app_management/tree/main/app_management

"""

import subprocess
import platform
from typing import Optional, Any
from pathlib import Path
import logging

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.cluster.sessions_managers.wt_utils.wt_helpers import (
    generate_random_suffix,
    # escape_for_wt,
    validate_layout_config,
    generate_wt_command_string,
    check_wt_session_status,
    check_command_status,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

# Check if we're on Windows
IS_WINDOWS = platform.system().lower() == "windows"
POWERSHELL_CMD = "powershell" if IS_WINDOWS else "pwsh"  # Use pwsh on non-Windows systems
TMP_LAYOUT_DIR = Path.home() / "tmp_results" / "wt_layouts"


class WTLayoutGenerator:
    def __init__(self, layout_config: LayoutConfig, session_name: str):
        self.session_name: str = session_name
        self.layout_config: LayoutConfig = layout_config.copy()
        self.script_path: Optional[str] = None

    def create_layout_file(self) -> bool:
        """Create Windows Terminal layout file and return success status."""
        validate_layout_config(self.layout_config)
        tab_count = len(self.layout_config['layoutTabs'])
        layout_name = self.layout_config['layoutName']
        console.print(f"[bold cyan]📋 Creating Windows Terminal layout[/bold cyan] [bright_green]'{layout_name}' with {tab_count} tabs[/bright_green]")
        
        for tab in self.layout_config['layoutTabs']:
            console.print(f"  [yellow]→[/yellow] [bold]{tab['tabName']}[/bold] [dim]in[/dim] [blue]{tab['startDir']}[/blue]")

        wt_command = generate_wt_command_string(self.layout_config, self.session_name)

        random_suffix = generate_random_suffix(8)
        script_content = f"""# Windows Terminal layout for {self.session_name}
# Generated with random suffix: {random_suffix}
{wt_command}
"""
        tmp_dir = Path(TMP_LAYOUT_DIR)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        script_file = tmp_dir / f"wt_layout_{self.session_name}_{random_suffix}.ps1"
        script_file.write_text(script_content, encoding="utf-8")
        self.script_path = str(script_file.absolute())

        console.print(f"[bold green]✅ Layout created successfully:[/bold green] [cyan]{self.script_path}[/cyan]")
        return True

    def get_wt_layout_preview(self, layout_config: LayoutConfig) -> str:
        """Generate preview of the Windows Terminal command that would be created."""
        validate_layout_config(layout_config)
        return generate_wt_command_string(layout_config, "preview")

    def check_all_commands_status(self) -> dict[str, dict[str, Any]]:
        if not self.layout_config:
            logger.warning("No layout config tracked. Make sure to create a layout first.")
            return {}

        status_report = {}
        for tab in self.layout_config["layoutTabs"]:
            tab_name = tab["tabName"]
            status_report[tab_name] = check_command_status(tab_name, self.layout_config)

        return status_report

    def get_status_report(self) -> dict[str, Any]:
        """Get status report for this layout including Windows Terminal and commands."""
        wt_status = check_wt_session_status(self.session_name or "default")
        commands_status = self.check_all_commands_status()

        running_count = sum(1 for status in commands_status.values() if status.get("running", False))
        total_count = len(commands_status)

        return {
            "wt_session": wt_status,
            "commands": commands_status,
            "summary": {"total_commands": total_count, "running_commands": running_count, "stopped_commands": total_count - running_count, "session_healthy": wt_status.get("session_exists", False)},
        }

    def print_status_report(self) -> None:
        """Print a comprehensive status report for this Windows Terminal layout."""
        status = self.get_status_report()
        wt_session = status["wt_session"]
        commands = status["commands"]
        summary = status["summary"]

        console.print()
        console.print(Panel.fit("� WINDOWS TERMINAL LAYOUT STATUS REPORT", style="bold cyan"))

        # Windows Terminal session status
        if wt_session.get("wt_running", False):
            if wt_session.get("session_exists", False):
                session_windows = wt_session.get("session_windows", [])
                all_windows = wt_session.get("all_windows", [])
                console.print(f"[bold green]✅ Windows Terminal session[/bold green] [yellow]'{self.session_name}'[/yellow] [green]is running[/green]")
                console.print(f"   Session windows: {len(session_windows)}")
                console.print(f"   Total WT windows: {len(all_windows)}")
            else:
                console.print(f"[bold yellow]⚠️  Windows Terminal is running but session[/bold yellow] [yellow]'{self.session_name}'[/yellow] [yellow]not found[/yellow]")
        else:
            error_msg = wt_session.get("error", "Unknown error")
            console.print(f"[bold red]❌ Windows Terminal session issue:[/bold red] [red]{error_msg}[/red]")

        console.print()

        # Commands status table
        table = Table(title="📋 COMMAND STATUS", show_header=True, header_style="bold magenta")
        table.add_column("Tab", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("PID", justify="center", style="dim")
        table.add_column("Command", style="green", max_width=40)

        for tab_name, cmd_status in commands.items():
            if cmd_status.get("running", False):
                status_text = "[bold green]✅ Running[/bold green]"
                processes = cmd_status.get("processes", [])
                if processes:
                    proc = processes[0]
                    pid = str(proc.get("pid", "N/A"))
                else:
                    pid = "N/A"
            else:
                status_text = "[bold red]❌ Stopped[/bold red]"
                pid = "N/A"

            command = cmd_status.get("command", "Unknown")
            if len(command) > 35:
                command = command[:32] + "..."

            table.add_row(tab_name, status_text, pid, command)

        console.print(table)
        console.print()

        # Summary panel
        summary_text = f"""[bold]Total commands:[/bold] {summary['total_commands']}
[green]Running:[/green] {summary['running_commands']}
[red]Stopped:[/red] {summary['stopped_commands']}
[yellow]Session healthy:[/yellow] {"✅" if summary['session_healthy'] else "❌"}"""

        console.print(Panel(summary_text, title="📊 Summary", style="blue"))


def create_wt_layout(layout_config: LayoutConfig, output_path: str) -> str:
    session_name = layout_config["layoutName"]
    generator = WTLayoutGenerator(layout_config=layout_config, session_name=session_name)
    generator.create_layout_file()
    
    if generator.script_path is None:
        raise RuntimeError("Script path was not set after creating layout file")
    
    logger.info(f"Windows Terminal PowerShell script created: {generator.script_path}")
    return generator.script_path


def run_wt_layout(layout_config: LayoutConfig) -> None:
    """Create and run a Windows Terminal layout."""
    session_name = layout_config["layoutName"]
    generator = WTLayoutGenerator(layout_config=layout_config, session_name=session_name)
    generator.create_layout_file()
    if generator.script_path is None:
        raise RuntimeError("Script path was not set after creating layout file")
    # Execute the script
    cmd = f'powershell -ExecutionPolicy Bypass -File "{generator.script_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Windows Terminal layout is running @ {layout_config['layoutName']}")
    else:
        logger.error(f"Failed to run Windows Terminal layout: {result.stderr}")
        raise RuntimeError(f"Failed to run layout: {result.stderr}")


def run_command_in_wt_tab(command: str, tab_name: str, cwd: Optional[str]) -> str:
    """Create a command to run in a new Windows Terminal tab."""
    cwd_part = f'-d "{cwd}"' if cwd else ""
    return f"""
echo "Creating new Windows Terminal tab: {tab_name}"
wt new-tab --title "{tab_name}" {cwd_part} "{command}"
"""


if __name__ == "__main__":
    sample_layout: LayoutConfig = {"layoutName": "TestLayout",
                                   "layoutTabs": [
            {"tabName": "Frontend", "startDir": "~/code", "command": "btm"},
            {"tabName": "Monitor", "startDir": "~", "command": "lf"}
            ]}
    try:
        session_name = sample_layout["layoutName"]
        generator = WTLayoutGenerator(layout_config=sample_layout, session_name=session_name)
        generator.create_layout_file()
        
        print(f"✅ Windows Terminal layout created: {generator.script_path}")
        preview = generator.get_wt_layout_preview(generator.layout_config)
        print(f"📋 Command Preview:\n{preview}")
        print("🔍 Current status:")
        generator.print_status_report()
        print("▶️  To run this layout, execute:")
        print(f'   powershell -ExecutionPolicy Bypass -File "{generator.script_path}"')
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
