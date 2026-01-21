#!/usr/bin/env python3
from pathlib import Path
import subprocess
from typing import Optional, TypedDict

from rich.console import Console

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.cluster.sessions_managers.tmux.tmux_utils.tmux_helpers import (
    build_tmux_script,
    check_tmux_session_status,
    build_unknown_command_status,
    validate_layout_config,
    TmuxSessionStatus,
)
from machineconfig.cluster.sessions_managers.zellij.zellij_utils.monitoring_types import CommandStatus


console = Console()


class TmuxLayoutSummary(TypedDict):
    total_commands: int
    running_commands: int
    stopped_commands: int
    session_healthy: bool


class TmuxLayoutStatus(TypedDict):
    tmux_session: TmuxSessionStatus
    commands: dict[str, CommandStatus]
    summary: TmuxLayoutSummary


class TmuxLayoutGenerator:
    def __init__(self, layout_config: LayoutConfig, session_name: str) -> None:
        self.session_name: str = session_name
        self.layout_config: LayoutConfig = layout_config.copy()
        self.script_path: Optional[str] = None

    def create_layout_file(self) -> bool:
        validate_layout_config(self.layout_config)
        tab_count = len(self.layout_config["layoutTabs"])
        layout_name = self.layout_config["layoutName"]
        console.print(f"[bold cyan]📋 Creating tmux layout[/bold cyan] [bright_green]'{layout_name}' with {tab_count} windows[/bright_green]")
        for tab in self.layout_config["layoutTabs"]:
            console.print(f"  [yellow]→[/yellow] [bold]{tab['tabName']}[/bold] [dim]in[/dim] [blue]{tab['startDir']}[/blue]")
        script_content = build_tmux_script(self.layout_config, self.session_name)
        tmp_dir = Path.home() / "tmp_results" / "sessions" / "tmux_layouts"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        import tempfile
        layout_file = Path(tempfile.mkstemp(suffix="_layout.sh", dir=tmp_dir)[1])
        layout_file.write_text(script_content, encoding="utf-8")
        layout_file.chmod(layout_file.stat().st_mode | 0o111)
        self.script_path = str(layout_file.absolute())
        console.print(f"[bold green]✅ Layout created successfully:[/bold green] [cyan]{self.script_path}[/cyan]")
        return True

    def check_all_commands_status(self) -> dict[str, CommandStatus]:
        if not self.layout_config:
            return {}
        status_report: dict[str, CommandStatus] = {}
        for tab in self.layout_config["layoutTabs"]:
            status_report[tab["tabName"]] = build_unknown_command_status(tab)
        return status_report

    def get_status_report(self) -> TmuxLayoutStatus:
        tmux_status = check_tmux_session_status(self.session_name or "default")
        commands_status = self.check_all_commands_status()
        running_count = sum(1 for status in commands_status.values() if status.get("running", False))
        total_count = len(commands_status)
        return {
            "tmux_session": tmux_status,
            "commands": commands_status,
            "summary": {
                "total_commands": total_count,
                "running_commands": running_count,
                "stopped_commands": total_count - running_count,
                "session_healthy": tmux_status.get("session_exists", False),
            },
        }

    def print_status_report(self) -> None:
        status = self.get_status_report()
        tmux_status = status["tmux_session"]
        commands = status["commands"]
        summary = status["summary"]
        console.print()
        console.print("[bold cyan]🔍 TMUX LAYOUT STATUS REPORT[/bold cyan]")
        if tmux_status.get("tmux_running", False):
            if tmux_status.get("session_exists", False):
                console.print(f"[bold green]✅ tmux session[/bold green] [yellow]'{self.session_name}'[/yellow] [green]is running[/green]")
            else:
                console.print(f"[bold yellow]⚠️  tmux is running but session[/bold yellow] [yellow]'{self.session_name}'[/yellow] [yellow]not found[/yellow]")
        else:
            console.print(f"[bold red]❌ tmux issue:[/bold red] [red]{tmux_status.get('error', 'Unknown error')}[/red]")
        console.print()
        for tab_name, cmd_status in commands.items():
            status_icon = "✅" if cmd_status.get("running", False) else "❌"
            cmd_text = cmd_status.get("command", "Unknown")
            if len(cmd_text) > 50:
                cmd_text = cmd_text[:47] + "..."
            console.print(f"   {status_icon} {tab_name}: {cmd_text}")
        console.print()
        console.print(
            f"[bold]Total commands:[/bold] {summary['total_commands']} | "
            f"[green]Running:[/green] {summary['running_commands']} | "
            f"[red]Stopped:[/red] {summary['stopped_commands']} | "
            f"[yellow]Session healthy:[/yellow] {'✅' if summary['session_healthy'] else '❌'}"
        )

    def run(self) -> dict[str, str | int]:
        if self.script_path is None:
            raise RuntimeError("Script path was not set after creating layout file")
        result = subprocess.run(["bash", self.script_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to run tmux layout: {result.stderr or result.stdout}")
        return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def run_tmux_layout(layout_config: LayoutConfig) -> None:
    session_name = layout_config["layoutName"]
    generator = TmuxLayoutGenerator(layout_config=layout_config, session_name=session_name)
    generator.create_layout_file()
    generator.run()
