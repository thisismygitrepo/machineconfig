#!/usr/bin/env python3
"""
Windows Terminal local layout generator and session manager.
Equivalent to zellij_local.py but for Windows Terminal.

https://github.com/ruby9455/app_management/tree/main/app_management

"""

import shlex
import subprocess
import random
import string
import json
import platform
from typing import Optional, Any
from pathlib import Path
import logging

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig

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
        self.script_path: Optional[str] = None  # Store the full path to the PowerShell script

    @staticmethod
    def _generate_random_suffix(length: int) -> str:
        """Generate a random string suffix for unique PowerShell script names."""
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    @staticmethod
    def _parse_command(command: str) -> tuple[str, list[str]]:
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
    def _escape_for_wt(text: str) -> str:
        """Escape text for use in Windows Terminal commands."""
        # Windows Terminal uses PowerShell-style escaping
        text = text.replace('"', '""')  # Escape quotes for PowerShell
        if " " in text or ";" in text or "&" in text or "|" in text:
            return f'"{text}"'
        return text



    @staticmethod
    def _validate_layout_config(layout_config: LayoutConfig) -> None:
        """Validate layout configuration format and content."""
        if not layout_config["layoutTabs"]:
            raise ValueError("Layout must contain at least one tab")
        for tab in layout_config["layoutTabs"]:
            if not tab["tabName"].strip():
                raise ValueError(f"Invalid tab name: {tab['tabName']}")
            if not tab["command"].strip():
                raise ValueError(f"Invalid command for tab '{tab['tabName']}': {tab['command']}")
            if not tab["startDir"].strip():
                raise ValueError(f"Invalid startDir for tab '{tab['tabName']}': {tab['startDir']}")

    def create_layout_file(self) -> bool:
        """Create Windows Terminal layout file and return success status."""
        WTLayoutGenerator._validate_layout_config(self.layout_config)
        tab_count = len(self.layout_config['layoutTabs'])
        layout_name = self.layout_config['layoutName']
        console.print(f"[bold cyan]📋 Creating Windows Terminal layout[/bold cyan] [bright_green]'{layout_name}' with {tab_count} tabs[/bright_green]")
        
        for tab in self.layout_config['layoutTabs']:
            console.print(f"  [yellow]→[/yellow] [bold]{tab['tabName']}[/bold] [dim]in[/dim] [blue]{tab['startDir']}[/blue]")

        # Generate Windows Terminal command
        wt_command = self._generate_wt_command_string(self.layout_config, self.session_name)

        random_suffix = WTLayoutGenerator._generate_random_suffix(8)
        # Create PowerShell script content
        script_content = f"""# Windows Terminal layout for {self.session_name}
# Generated with random suffix: {random_suffix}
{wt_command}
"""
        # Write to file
        random_suffix = WTLayoutGenerator._generate_random_suffix(8)
        tmp_dir = Path(TMP_LAYOUT_DIR)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        script_file = tmp_dir / f"wt_layout_{self.session_name}_{random_suffix}.ps1"
        script_file.write_text(script_content, encoding="utf-8")
        self.script_path = str(script_file.absolute())

        console.print(f"[bold green]✅ Layout created successfully:[/bold green] [cyan]{self.script_path}[/cyan]")
        return True

    def _generate_wt_command_string(self, layout_config: LayoutConfig, window_name: str) -> str:
        """Generate complete Windows Terminal command string."""
        # Build the complete Windows Terminal command
        command_parts = []
        
        for i, tab in enumerate(layout_config["layoutTabs"]):
            is_first = i == 0
            
            if is_first:
                # First tab: start with wt command and window name
                tab_parts = ["wt", "-w", WTLayoutGenerator._escape_for_wt(window_name)]
            else:
                # Subsequent tabs: use new-tab
                tab_parts = ["new-tab"]
            
            # Add common tab arguments
            tab_name = tab["tabName"]
            cwd = tab["startDir"]
            command = tab["command"]
            
            # Convert paths to Windows format if needed
            if cwd.startswith("~/"):
                cwd = cwd.replace("~/", f"{Path.home()}/")
            elif cwd == "~":
                cwd = str(Path.home())
            
            # Add arguments in the correct order
            tab_parts.extend(["-d", WTLayoutGenerator._escape_for_wt(cwd)])
            tab_parts.extend(["--title", WTLayoutGenerator._escape_for_wt(tab_name)])
            tab_parts.append(WTLayoutGenerator._escape_for_wt(command))
            
            command_parts.append(" ".join(tab_parts))
        
        # Join all tab commands with escaped semicolons for PowerShell
        return " `; ".join(command_parts)

    def get_wt_layout_preview(self, layout_config: LayoutConfig) -> str:
        """Generate preview of the Windows Terminal command that would be created."""
        WTLayoutGenerator._validate_layout_config(layout_config)
        return self._generate_wt_command_string(layout_config, "preview")

    def check_all_commands_status(self) -> dict[str, dict[str, Any]]:
        if not self.layout_config:
            logger.warning("No layout config tracked. Make sure to create a layout first.")
            return {}

        status_report = {}
        for tab in self.layout_config["layoutTabs"]:
            tab_name = tab["tabName"]
            status_report[tab_name] = WTLayoutGenerator.check_command_status(tab_name, self.layout_config)

        return status_report

    @staticmethod
    def check_wt_session_status(session_name: str) -> dict[str, Any]:
        try:
            # Simplified Windows Terminal process check
            ps_script = """
try {
    $wtProcesses = Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue
    if ($wtProcesses) {
        $processInfo = @()
        $wtProcesses | ForEach-Object {
            $info = @{
                "Id" = $_.Id
                "ProcessName" = $_.ProcessName
                "StartTime" = $_.StartTime.ToString()
            }
            $processInfo += $info
        }
        $processInfo | ConvertTo-Json -Depth 2
    }
} catch {
    # No Windows Terminal processes found
}
"""

            result = subprocess.run([POWERSHELL_CMD, "-Command", ps_script], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                output = result.stdout.strip()
                if output and output != "":
                    try:
                        processes = json.loads(output)
                        if not isinstance(processes, list):
                            processes = [processes]

                        # For simplicity, assume session exists if WT is running
                        return {
                            "wt_running": True, 
                            "session_exists": len(processes) > 0, 
                            "session_name": session_name, 
                            "all_windows": processes, 
                            "session_windows": processes  # Simplified - assume all windows could be session windows
                        }
                    except Exception as e:
                        return {"wt_running": True, "session_exists": False, "error": f"Failed to parse process info: {e}", "session_name": session_name}
                else:
                    return {"wt_running": False, "session_exists": False, "session_name": session_name, "all_windows": []}
            else:
                return {"wt_running": False, "error": result.stderr, "session_name": session_name}

        except subprocess.TimeoutExpired:
            return {"wt_running": False, "error": "Timeout while checking Windows Terminal processes", "session_name": session_name}
        except FileNotFoundError:
            return {"wt_running": False, "error": f"PowerShell ({POWERSHELL_CMD}) not found in PATH", "session_name": session_name}
        except Exception as e:
            return {"wt_running": False, "error": str(e), "session_name": session_name}

    @staticmethod
    def check_command_status(tab_name: str, layout_config: LayoutConfig) -> dict[str, Any]:
        """Check if a command is running by looking for processes."""
        # Find the tab with the given name
        tab_config = None
        for tab in layout_config["layoutTabs"]:
            if tab["tabName"] == tab_name:
                tab_config = tab
                break

        if tab_config is None:
            return {"status": "unknown", "error": f"Tab '{tab_name}' not found in layout config", "running": False, "pid": None, "command": None}

        command = tab_config["command"]

        try:
            # Extract the primary executable name from command
            primary_cmd = command.split()[0] if command.strip() else ""
            if not primary_cmd:
                return {"status": "error", "error": "Empty command", "running": False, "command": command, "tab_name": tab_name}

            # Use a much simpler PowerShell script that just checks for process names
            ps_script = f"""
try {{
    $processes = Get-Process -Name '{primary_cmd}' -ErrorAction SilentlyContinue
    if ($processes) {{
        $processes | ForEach-Object {{
            $procInfo = @{{
                "pid" = $_.Id
                "name" = $_.ProcessName
                "start_time" = $_.StartTime.ToString()
            }}
            Write-Output ($procInfo | ConvertTo-Json -Compress)
        }}
    }}
}} catch {{
    # No processes found or other error
}}
"""

            result = subprocess.run([POWERSHELL_CMD, "-Command", ps_script], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                output_lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
                matching_processes = []

                for line in output_lines:
                    if line.startswith("{") and line.endswith("}"):
                        try:
                            proc_info = json.loads(line)
                            matching_processes.append(proc_info)
                        except json.JSONDecodeError:
                            continue

                if matching_processes:
                    return {"status": "running", "running": True, "processes": matching_processes, "command": command, "tab_name": tab_name}
                else:
                    return {"status": "not_running", "running": False, "processes": [], "command": command, "tab_name": tab_name}
            else:
                return {"status": "error", "error": f"Command failed: {result.stderr}", "running": False, "command": command, "tab_name": tab_name}

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout checking command status for tab '{tab_name}'")
            return {"status": "timeout", "error": "Timeout checking process status", "running": False, "command": command, "tab_name": tab_name}
        except Exception as e:
            logger.error(f"Error checking command status for tab '{tab_name}': {e}")
            return {"status": "error", "error": str(e), "running": False, "command": command, "tab_name": tab_name}

    def get_status_report(self) -> dict[str, Any]:
        """Get status report for this layout including Windows Terminal and commands."""
        wt_status = WTLayoutGenerator.check_wt_session_status(self.session_name or "default")
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
