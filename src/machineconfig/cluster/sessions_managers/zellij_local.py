#!/usr/bin/env python3
import shlex
import subprocess
from machineconfig.cluster.sessions_managers.zellij_utils.monitoring_types import CommandStatus, ZellijSessionStatus, ComprehensiveStatus, ProcessInfo
import psutil
import random
import string
from typing import List, Optional
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
    def _generate_random_suffix(length: int) -> str:
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

    def create_zellij_layout(self, layout_config: LayoutConfig, output_dir: Optional[str], session_name: Optional[str]) -> str:
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
            random_suffix = ZellijLayoutGenerator._generate_random_suffix(8)
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
    def get_layout_preview(layout_config: LayoutConfig, layout_template: str | None) -> str:
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
    def check_command_status(tab_name: str, layout_config: LayoutConfig) -> CommandStatus:
        # Find the tab with the given name
        tab_config = None
        for tab in layout_config["layoutTabs"]:
            if tab["tabName"] == tab_name:
                tab_config = tab
                break

        if tab_config is None:
            return {"status": "unknown", "error": f"Tab '{tab_name}' not found in layout config", "running": False, "command": "", "cwd": "", "tab_name": tab_name, "processes": []}

        command = tab_config["command"]
        cwd = tab_config["startDir"]
        cmd, args = ZellijLayoutGenerator._parse_command(command)
        try:
            shells = {"bash", "sh", "zsh", "fish"}
            matching_processes: list[ProcessInfo] = []
            for proc in psutil.process_iter(["pid", "name", "cmdline", "status", "ppid", "create_time", "memory_info"]):
                try:
                    info = proc.info
                    proc_cmdline: list[str] | None = info.get("cmdline")  # type: ignore[assignment]
                    if not proc_cmdline:
                        continue
                    if info.get("status") in ["zombie", "dead", "stopped"]:
                        continue
                    proc_name = info.get("name", "")
                    is_match = False
                    joined_cmdline = " ".join(proc_cmdline)
                    # Primary matching heuristics - more precise matching
                    if proc_name == cmd and cmd not in shells:
                        # For non-shell commands, match if args appear in cmdline
                        if not args or any(arg in joined_cmdline for arg in args):
                            is_match = True
                    elif proc_name == cmd and cmd in shells:
                        # For shell commands, require more precise matching to avoid false positives
                        if args:
                            # Check if all args appear as separate cmdline arguments (not just substrings)
                            args_found = 0
                            for arg in args:
                                for cmdline_arg in proc_cmdline[1:]:  # Skip shell name
                                    if arg == cmdline_arg or (len(arg) > 3 and arg in cmdline_arg):
                                        args_found += 1
                                        break
                            # Require at least as many args found as we're looking for
                            if args_found >= len(args):
                                is_match = True
                    elif cmd in proc_cmdline[0] and cmd not in shells:
                        # Non-shell command in first argument
                        is_match = True

                    # Additional shell wrapper filter - be more restrictive for shells
                    if is_match and proc_name in shells and args:
                        # For shell processes, ensure the match is actually meaningful
                        # Don't match generic shell sessions just because they contain common paths
                        meaningful_match = False
                        for arg in args:
                            # Only consider it meaningful if the arg is substantial (not just a common path)
                            if len(arg) > 10 and any(arg == cmdline_arg for cmdline_arg in proc_cmdline[1:]):
                                meaningful_match = True
                                break
                            # Or if it's an exact script name match
                            elif arg.endswith(".py") or arg.endswith(".sh") or arg.endswith(".rb"):
                                if any(arg in cmdline_arg for cmdline_arg in proc_cmdline[1:]):
                                    meaningful_match = True
                                    break
                        if not meaningful_match:
                            is_match = False
                    if not is_match:
                        continue
                    try:
                        proc_obj = psutil.Process(info["pid"])  # type: ignore[index]
                        if proc_obj.status() not in ["running", "sleeping"]:
                            continue
                        mem_info = None
                        try:
                            mem = proc_obj.memory_info()
                            mem_info = mem.rss / (1024 * 1024)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        matching_processes.append(
                            {
                                "pid": info["pid"],  # type: ignore[index]
                                "name": proc_name,
                                "cmdline": proc_cmdline,
                                "status": info.get("status", "unknown"),
                                "cmdline_str": joined_cmdline,
                                "create_time": info.get("create_time", 0.0),
                                **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
                            }
                        )
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            # Second-pass filtering: remove idle wrapper shells that have no meaningful (non-shell) descendants
            filtered_active: list[ProcessInfo] = []
            for proc_info in matching_processes:
                try:
                    proc_obj = psutil.Process(proc_info["pid"])  # type: ignore[index]
                    if not proc_obj.is_running():
                        continue
                    status_val = proc_obj.status()
                    if status_val not in ["running", "sleeping"]:
                        continue
                    proc_name = proc_info.get("name", "")
                    if proc_name in shells:
                        descendants = proc_obj.children(recursive=True)
                        # Keep shell only if there exists a non-shell alive descendant OR descendant cmdline still includes our command token
                        meaningful = False
                        for child in descendants:
                            try:
                                if not child.is_running():
                                    continue
                                child_name = child.name()
                                child_cmdline = " ".join(child.cmdline())
                                if child_name not in shells:
                                    meaningful = True
                                    break
                                if cmd in child_cmdline or any(arg in child_cmdline for arg in args):
                                    meaningful = True
                                    break
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                        if not meaningful:
                            continue  # discard idle wrapper shell
                    filtered_active.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            if filtered_active:
                # Heuristic: if the only remaining processes are wrapper shells invoking a script that already completed, mark as not running.
                # Case: layout launches 'bash <script.sh>' where script finishes and leaves an idle shell whose cmdline still shows the script path.
                try:
                    if all(p.get("name") in shells for p in filtered_active):
                        script_paths = [arg for arg in args if arg.endswith(".sh")]
                        shell_only = True
                        stale_script_overall = False
                        for p in filtered_active:
                            proc_shell = psutil.Process(p["pid"])  # type: ignore[index]
                            create_time = getattr(proc_shell, "create_time", lambda: None)()
                            cmdline_joined = " ".join(p.get("cmdline", []))
                            stale_script = False
                            for spath in script_paths:
                                script_file = Path(spath)
                                if script_file.exists():
                                    try:
                                        # If script mtime older than process start AND no non-shell descendants -> likely finished
                                        if create_time and script_file.stat().st_mtime < create_time:
                                            stale_script = True
                                    except OSError:
                                        pass
                                if spath not in cmdline_joined:
                                    stale_script = False
                            # If shell has any alive non-shell descendants, treat as running
                            descendants = proc_shell.children(recursive=True)
                            for d in descendants:
                                try:
                                    if d.is_running() and d.name() not in shells:
                                        shell_only = False
                                        break
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    continue
                            if not shell_only:
                                break
                            if stale_script:
                                stale_script_overall = True
                        if shell_only and stale_script_overall:
                            return {"status": "not_running", "running": False, "processes": [], "command": command, "cwd": cwd, "tab_name": tab_name}
                except Exception:
                    pass
                return {"status": "running", "running": True, "processes": filtered_active, "command": command, "cwd": cwd, "tab_name": tab_name}
            return {"status": "not_running", "running": False, "processes": [], "command": command, "cwd": cwd, "tab_name": tab_name}

        except Exception as e:
            logger.error(f"Error checking command status for tab '{tab_name}': {e}")
            return {"status": "error", "error": str(e), "running": False, "command": command, "cwd": cwd, "tab_name": tab_name, "processes": []}

    def check_all_commands_status(self) -> dict[str, CommandStatus]:
        if not self.layout_config:
            logger.warning("No layout config tracked. Make sure to create a layout first.")
            return {}

        status_report: dict[str, CommandStatus] = {}
        for tab in self.layout_config["layoutTabs"]:
            tab_name = tab["tabName"]
            status_report[tab_name] = ZellijLayoutGenerator.check_command_status(tab_name, self.layout_config)

        return status_report

    @staticmethod
    def check_zellij_session_status(session_name: str) -> ZellijSessionStatus:
        try:
            # Run zellij list-sessions command
            result = subprocess.run(["zellij", "list-sessions"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                sessions = result.stdout.strip().split("\n") if result.stdout.strip() else []
                session_running = any(session_name in session for session in sessions)

                return {"zellij_running": True, "session_exists": session_running, "session_name": session_name, "all_sessions": sessions}
            else:
                return {"zellij_running": False, "session_exists": False, "session_name": session_name, "all_sessions": [], "error": result.stderr}

        except subprocess.TimeoutExpired:
            return {"zellij_running": False, "session_exists": False, "session_name": session_name, "all_sessions": [], "error": "Timeout while checking Zellij sessions"}
        except FileNotFoundError:
            return {"zellij_running": False, "session_exists": False, "session_name": session_name, "all_sessions": [], "error": "Zellij not found in PATH"}
        except Exception as e:
            return {"zellij_running": False, "session_exists": False, "session_name": session_name, "all_sessions": [], "error": str(e)}

    def get_comprehensive_status(self) -> ComprehensiveStatus:
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


def created_zellij_layout(layout_config: LayoutConfig, output_dir: Optional[str]) -> str:
    generator = ZellijLayoutGenerator()
    return generator.create_zellij_layout(layout_config, output_dir, None)


def run_zellij_layout(layout_config: LayoutConfig):
    layout_path = created_zellij_layout(layout_config, None)
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
        layout_path = generator.create_zellij_layout(sample_layout, None, "test_session")
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
