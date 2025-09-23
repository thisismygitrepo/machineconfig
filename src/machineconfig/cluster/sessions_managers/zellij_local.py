#!/usr/bin/env python3
import shlex
import subprocess
import psutil
import random
import string
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from rich.console import Console

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, TabConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()
TMP_LAYOUT_DIR = Path.home().joinpath("tmp_results", "session_manager", "zellij", "layout_manager")


class ZellijLayoutGenerator:
    def __init__(self):
        self.session_name: Optional[str] = None
        self.layout_config: Optional[LayoutConfig] = None  # Store the complete layout config
        self.layout_path: Optional[str] = None  # Store the full path to the layout file
        self.layout_template = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""

    @staticmethod
    def _generate_random_suffix(length: int = 8) -> str:
        """Generate a random string suffix for unique layout file names."""
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    @staticmethod
    def _parse_command(command: str) -> tuple[str, List[str]]:
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
    def _format_args_for_kdl(args: List[str]) -> str:
        if not args:
            return ""
        formatted_args = []
        for arg in args:
            if " " in arg or '"' in arg or "'" in arg:
                escaped_arg = arg.replace('"', '\\"')
                formatted_args.append(f'"{escaped_arg}"')
            else:
                formatted_args.append(f'"{arg}"')
        return " ".join(formatted_args)

    @staticmethod
    def _create_tab_section(tab_config: TabConfig) -> str:
        tab_name = tab_config["tabName"]
        cwd = tab_config["startDir"]
        command = tab_config["command"]

        cmd, args = ZellijLayoutGenerator._parse_command(command)
        args_str = ZellijLayoutGenerator._format_args_for_kdl(args)
        tab_cwd = cwd or "~"
        escaped_tab_name = tab_name.replace('"', '\\"')
        tab_section = f'  tab name="{escaped_tab_name}" cwd="{tab_cwd}" {{\n'
        tab_section += f'    pane command="{cmd}" {{\n'
        if args_str:
            tab_section += f"      args {args_str}\n"
        tab_section += "    }\n  }\n"
        return tab_section

    @staticmethod
    def _validate_layout_config(layout_config: LayoutConfig) -> None:
        if not layout_config["layoutTabs"]:
            raise ValueError("Layout must contain at least one tab")
        for tab in layout_config["layoutTabs"]:
            if not tab["tabName"].strip():
                raise ValueError(f"Invalid tab name: {tab['tabName']}")
            if not tab["command"].strip():
                raise ValueError(f"Invalid command for tab '{tab['tabName']}': {tab['command']}")
            if not tab["startDir"].strip():
                raise ValueError(f"Invalid startDir for tab '{tab['tabName']}': {tab['startDir']}")

    def create_zellij_layout(self, layout_config: LayoutConfig, output_dir: Optional[str] = None, session_name: Optional[str] = None) -> str:
        ZellijLayoutGenerator._validate_layout_config(layout_config)

        # Enhanced Rich logging
        tab_count = len(layout_config["layoutTabs"])
        layout_name = layout_config["layoutName"]
        console.print(f"[bold cyan]📋 Creating Zellij layout[/bold cyan] [bright_green]'{layout_name}' with {tab_count} tabs[/bright_green]")

        # Display tab summary with emojis and colors
        for tab in layout_config["layoutTabs"]:
            console.print(f"  [yellow]→[/yellow] [bold]{tab['tabName']}[/bold] [dim]in[/dim] [blue]{tab['startDir']}[/blue]")

        # Store session name and layout config for status checking
        self.session_name = session_name or layout_name
        self.layout_config = layout_config.copy()

        layout_content = self.layout_template
        for tab in layout_config["layoutTabs"]:
            layout_content += "\n" + ZellijLayoutGenerator._create_tab_section(tab)
        layout_content += "\n}\n"

        try:
            random_suffix = ZellijLayoutGenerator._generate_random_suffix()
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                layout_file = output_path / f"zellij_layout_{random_suffix}.kdl"
                layout_file.write_text(layout_content, encoding="utf-8")
                self.layout_path = str(layout_file.absolute())
            else:
                # Use the predefined TMP_LAYOUT_DIR for temporary files
                TMP_LAYOUT_DIR.mkdir(parents=True, exist_ok=True)
                layout_file = TMP_LAYOUT_DIR / f"zellij_layout_{self.session_name or 'default'}_{random_suffix}.kdl"
                layout_file.write_text(layout_content, encoding="utf-8")
                self.layout_path = str(layout_file.absolute())

            # Enhanced Rich logging for file creation
            console.print(f"[bold green]✅ Zellij layout file created:[/bold green] [cyan]{self.layout_path}[/cyan]")
            return self.layout_path
        except OSError as e:
            logger.error(f"Failed to create layout file: {e}")
            raise

    @staticmethod
    def get_layout_preview(layout_config: LayoutConfig, layout_template: str | None = None) -> str:
        if layout_template is None:
            layout_template = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""
        ZellijLayoutGenerator._validate_layout_config(layout_config)
        layout_content = layout_template
        for tab in layout_config["layoutTabs"]:
            layout_content += "\n" + ZellijLayoutGenerator._create_tab_section(tab)
        return layout_content + "\n}\n"

    @staticmethod
    def check_command_status(tab_name: str, layout_config: LayoutConfig) -> Dict[str, Any]:
        # Find the tab with the given name
        tab_config = None
        for tab in layout_config["layoutTabs"]:
            if tab["tabName"] == tab_name:
                tab_config = tab
                break

        if tab_config is None:
            return {"status": "unknown", "error": f"Tab '{tab_name}' not found in layout config", "running": False, "pid": None, "command": None, "cwd": None}

        command = tab_config["command"]
        cwd = tab_config["startDir"]
        cmd, _ = ZellijLayoutGenerator._parse_command(command)

        try:
            # Look for processes matching the command
            matching_processes = []
            for proc in psutil.process_iter(["pid", "name", "cmdline", "status"]):
                try:
                    if proc.info["cmdline"] and len(proc.info["cmdline"]) > 0:
                        # Check if the command matches
                        if proc.info["name"] == cmd or cmd in proc.info["cmdline"][0] or any(cmd in arg for arg in proc.info["cmdline"]):
                            matching_processes.append({"pid": proc.info["pid"], "name": proc.info["name"], "cmdline": proc.info["cmdline"], "status": proc.info["status"]})
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if matching_processes:
                return {"status": "running", "running": True, "processes": matching_processes, "command": command, "cwd": cwd, "tab_name": tab_name}
            else:
                return {"status": "not_running", "running": False, "processes": [], "command": command, "cwd": cwd, "tab_name": tab_name}

        except Exception as e:
            logger.error(f"Error checking command status for tab '{tab_name}': {e}")
            return {"status": "error", "error": str(e), "running": False, "command": command, "cwd": cwd, "tab_name": tab_name}

    def check_all_commands_status(self) -> Dict[str, Dict[str, Any]]:
        if not self.layout_config:
            logger.warning("No layout config tracked. Make sure to create a layout first.")
            return {}

        status_report = {}
        for tab in self.layout_config["layoutTabs"]:
            tab_name = tab["tabName"]
            status_report[tab_name] = ZellijLayoutGenerator.check_command_status(tab_name, self.layout_config)

        return status_report

    @staticmethod
    def check_zellij_session_status(session_name: str) -> Dict[str, Any]:
        try:
            # Run zellij list-sessions command
            result = subprocess.run(["zellij", "list-sessions"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                sessions = result.stdout.strip().split("\n") if result.stdout.strip() else []
                session_running = any(session_name in session for session in sessions)

                return {"zellij_running": True, "session_exists": session_running, "session_name": session_name, "all_sessions": sessions}
            else:
                return {"zellij_running": False, "error": result.stderr, "session_name": session_name}

        except subprocess.TimeoutExpired:
            return {"zellij_running": False, "error": "Timeout while checking Zellij sessions", "session_name": session_name}
        except FileNotFoundError:
            return {"zellij_running": False, "error": "Zellij not found in PATH", "session_name": session_name}
        except Exception as e:
            return {"zellij_running": False, "error": str(e), "session_name": session_name}

    def get_comprehensive_status(self) -> Dict[str, Any]:
        zellij_status = ZellijLayoutGenerator.check_zellij_session_status(self.session_name or "default")
        commands_status = self.check_all_commands_status()

        running_count = sum(1 for status in commands_status.values() if status.get("running", False))
        total_count = len(commands_status)

        return {
            "zellij_session": zellij_status,
            "commands": commands_status,
            "summary": {"total_commands": total_count, "running_commands": running_count, "stopped_commands": total_count - running_count, "session_healthy": zellij_status.get("session_exists", False)},
        }

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


def created_zellij_layout(layout_config: LayoutConfig, output_dir: Optional[str] = None) -> str:
    generator = ZellijLayoutGenerator()
    return generator.create_zellij_layout(layout_config, output_dir)


def run_zellij_layout(layout_config: LayoutConfig):
    layout_path = created_zellij_layout(layout_config)
    session_name = layout_config["layoutName"]
    try:
        from machineconfig.cluster.sessions_managers.enhanced_command_runner import enhanced_zellij_session_start
        enhanced_zellij_session_start(session_name, layout_path)
    except ImportError:
        # Fallback to original implementation
        cmd = f"zellij delete-session --force {session_name}; zellij --layout {layout_path} a -b {session_name}"
        import subprocess

        subprocess.run(cmd, shell=True, check=True)
        console.print(f"[bold green]🚀 Zellij layout is running[/bold green] [yellow]@[/yellow] [bold cyan]{session_name}[/bold cyan]")


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
        "layoutTabs": [
            {"tabName": "🤖Bot1", "startDir": "~/code/bytesense/bithence", "command": "~/scripts/fire -mO go1.py bot1 --kw create_new_bot True"},
            {"tabName": "🤖Bot2", "startDir": "~/code/bytesense/bithence", "command": "~/scripts/fire -mO go2.py bot2 --kw create_new_bot True"},
            {"tabName": "📊Monitor", "startDir": "~", "command": "htop"},
            {"tabName": "📝Logs", "startDir": "/var/log", "command": "tail -f /var/log/app.log"},
        ],
    }

    try:
        # Create layout using the generator directly to access status methods
        generator = ZellijLayoutGenerator()
        layout_path = generator.create_zellij_layout(sample_layout, session_name="test_session")
        print(f"✅ Layout created successfully: {layout_path}")

        # Demonstrate status checking
        print("\n🔍 Checking command status (this is just a demo - commands aren't actually running):")
        generator.print_status_report()

        # Individual command status check
        print("\n🔎 Individual command status for Bot1:")
        if generator.layout_config:
            bot1_status = ZellijLayoutGenerator.check_command_status("🤖Bot1", generator.layout_config)
            print(f"Status: {bot1_status['status']}")
            print(f"Running: {bot1_status['running']}")

    except Exception as e:
        print(f"❌ Error: {e}")
