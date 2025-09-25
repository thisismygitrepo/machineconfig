#!/usr/bin/env python3
"""
Windows Terminal local layout generator and session manager.
Equivalent to zellij_local.py but for Windows Terminal.
"""

import shlex
import subprocess
import random
import string
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, TabConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TMP_LAYOUT_DIR = Path.home().joinpath("tmp_results", "session_manager", "wt", "layout_manager")


class WTLayoutGenerator:
    def __init__(self):
        self.session_name: Optional[str] = None
        self.layout_config: Optional[LayoutConfig] = None  # Store the complete layout config
        self.script_path: Optional[str] = None  # Store the full path to the PowerShell script

    @staticmethod
    def _generate_random_suffix(length: int) -> str:
        """Generate a random string suffix for unique PowerShell script names."""
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
    def _escape_for_wt(text: str) -> str:
        """Escape text for use in Windows Terminal commands."""
        # Windows Terminal uses PowerShell-style escaping
        text = text.replace('"', '""')  # Escape quotes for PowerShell
        if " " in text or ";" in text or "&" in text or "|" in text:
            return f'"{text}"'
        return text

    @staticmethod
    def _create_tab_command(tab_config: TabConfig, is_first_tab: bool) -> str:
        """Create a Windows Terminal tab command string from tab config."""
        tab_name = tab_config["tabName"]
        cwd = tab_config["startDir"]
        command = tab_config["command"]

        # Convert paths to Windows format if needed
        if cwd.startswith("~/"):
            cwd = cwd.replace("~/", f"{Path.home()}/")
        elif cwd == "~":
            cwd = str(Path.home())

        # Build the wt command parts
        tab_parts = []

        if not is_first_tab:
            tab_parts.append("new-tab")

        # Add starting directory
        tab_parts.extend(["-d", WTLayoutGenerator._escape_for_wt(cwd)])

        # Add tab title
        tab_parts.extend(["--title", WTLayoutGenerator._escape_for_wt(tab_name)])

        # Add the command to execute
        tab_parts.append(WTLayoutGenerator._escape_for_wt(command))

        return " ".join(tab_parts)

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

    def create_wt_layout(self, layout_config: LayoutConfig, output_dir: Optional[str]) -> str:
        WTLayoutGenerator._validate_layout_config(layout_config)
        logger.info(f"Creating Windows Terminal layout '{layout_config['layoutName']}' with {len(layout_config['layoutTabs'])} tabs")

        # Store session name and layout config for status checking
        self.session_name = layout_config["layoutName"]
        self.layout_config = layout_config.copy()

        # Generate Windows Terminal command
        wt_command = self._generate_wt_command_string(layout_config, self.session_name)

        try:
            random_suffix = WTLayoutGenerator._generate_random_suffix(8)
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                script_file = output_path / f"wt_layout_{random_suffix}.ps1"
            else:
                # Use the predefined TMP_LAYOUT_DIR for temporary files
                TMP_LAYOUT_DIR.mkdir(parents=True, exist_ok=True)
                script_file = TMP_LAYOUT_DIR / f"wt_layout_{self.session_name}_{random_suffix}.ps1"

            # Create PowerShell script
            text = f"""# Windows Terminal layout for {self.session_name}
# Generated with random suffix: {random_suffix}
{wt_command}
"""
            script_file.write_text(text, encoding="utf-8")

            self.script_path = str(script_file.absolute())
            logger.info(f"Windows Terminal PowerShell script created: {self.script_path}")
            return self.script_path
        except OSError as e:
            logger.error(f"Failed to create PowerShell script: {e}")
            raise

    def _generate_wt_command_string(self, layout_config: LayoutConfig, window_name: str) -> str:
        """Generate complete Windows Terminal command string."""
        # Start building the wt command
        wt_parts = ["wt"]

        # Add window name
        wt_parts.extend(["-w", WTLayoutGenerator._escape_for_wt(window_name)])

        # Add tabs
        tab_commands = []
        for i, tab in enumerate(layout_config["layoutTabs"]):
            is_first = i == 0
            tab_cmd = self._create_tab_command(tab, is_first)
            tab_commands.append(tab_cmd)

        # Join all parts with semicolons (Windows Terminal command separator)
        if tab_commands:
            if len(tab_commands) == 1:
                # Single tab - just add to the main command
                wt_parts.extend(tab_commands[0].split())
            else:
                # Multiple tabs - join with semicolons
                wt_parts.append(tab_commands[0])  # First tab
                for tab_cmd in tab_commands[1:]:
                    wt_parts.extend([";", tab_cmd])

        return " ".join(wt_parts)

    def get_wt_layout_preview(self, layout_config: LayoutConfig) -> str:
        """Generate preview of the Windows Terminal command that would be created."""
        WTLayoutGenerator._validate_layout_config(layout_config)
        return self._generate_wt_command_string(layout_config, "preview")

    def check_all_commands_status(self) -> Dict[str, Dict[str, Any]]:
        if not self.layout_config:
            logger.warning("No layout config tracked. Make sure to create a layout first.")
            return {}

        status_report = {}
        for tab in self.layout_config["layoutTabs"]:
            tab_name = tab["tabName"]
            status_report[tab_name] = WTLayoutGenerator.check_command_status(tab_name, self.layout_config)

        return status_report

    @staticmethod
    def check_wt_session_status(session_name: str) -> Dict[str, Any]:
        try:
            # Check for Windows Terminal processes
            wt_check_cmd = ["powershell", "-Command", "Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, MainWindowTitle | ConvertTo-Json -Depth 2"]

            result = subprocess.run(wt_check_cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                output = result.stdout.strip()
                if output and output != "":
                    try:
                        import json

                        processes = json.loads(output)
                        if not isinstance(processes, list):
                            processes = [processes]

                        # Look for windows that might belong to our session
                        session_windows = []
                        for proc in processes:
                            window_title = proc.get("MainWindowTitle", "")
                            if session_name in window_title or not window_title:
                                session_windows.append(proc)

                        return {"wt_running": True, "session_exists": len(session_windows) > 0, "session_name": session_name, "all_windows": processes, "session_windows": session_windows}
                    except Exception as e:
                        return {"wt_running": True, "session_exists": False, "error": f"Failed to parse process info: {e}", "session_name": session_name}
                else:
                    return {"wt_running": False, "session_exists": False, "session_name": session_name, "all_windows": []}
            else:
                return {"wt_running": False, "error": result.stderr, "session_name": session_name}

        except subprocess.TimeoutExpired:
            return {"wt_running": False, "error": "Timeout while checking Windows Terminal processes", "session_name": session_name}
        except FileNotFoundError:
            return {"wt_running": False, "error": "PowerShell not found in PATH", "session_name": session_name}
        except Exception as e:
            return {"wt_running": False, "error": str(e), "session_name": session_name}

    @staticmethod
    def check_command_status(tab_name: str, layout_config: LayoutConfig) -> Dict[str, Any]:
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
            # Create PowerShell script to check for processes
            cmd_parts = [part for part in command.split() if len(part) > 2]
            primary_cmd = cmd_parts[0] if cmd_parts else ""

            ps_script = f"""
$targetCommand = '{command.replace("'", "''")}'
$cmdParts = @({", ".join([f"'{part}'" for part in cmd_parts])})
$primaryCmd = '{primary_cmd}'
$currentPid = $PID
$matchingProcesses = @()

Get-Process | ForEach-Object {{
    try {{
        if ($_.Id -eq $currentPid) {{ return }}

        $cmdline = ""
        try {{
            $cmdline = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
        }} catch {{
            $cmdline = $_.ProcessName
        }}

        if ($cmdline -and $cmdline -ne "") {{
            if ($cmdline -like "*PowerShell*" -and $cmdline -like "*Get-Process*") {{ return }}

            $matchesPrimary = $cmdline -like "*$primaryCmd*" -and $primaryCmd -ne "powershell"
            $matchCount = 0
            foreach ($part in $cmdParts[1..($cmdParts.Length-1)]) {{
                if ($cmdline -like "*$part*") {{ $matchCount++ }}
            }}

            if ($matchesPrimary -and $matchCount -ge 1) {{
                $procInfo = @{{
                    "pid" = $_.Id
                    "name" = $_.ProcessName
                    "cmdline" = $cmdline
                    "status" = $_.Status
                    "start_time" = $_.StartTime
                }} | ConvertTo-Json -Compress
                Write-Output $procInfo
            }}
        }}
    }} catch {{
        # Ignore processes we can't access
    }}
}}
"""

            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=15)

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

        except Exception as e:
            logger.error(f"Error checking command status for tab '{tab_name}': {e}")
            return {"status": "error", "error": str(e), "running": False, "command": command, "tab_name": tab_name}

    def get_status_report(self) -> Dict[str, Any]:
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

        print("=" * 80)
        print("🖥️  WINDOWS TERMINAL LAYOUT STATUS REPORT")
        print("=" * 80)

        # Windows Terminal session status
        print(f"🪟 Session: {self.session_name}")
        if wt_session.get("wt_running", False):
            if wt_session.get("session_exists", False):
                session_windows = wt_session.get("session_windows", [])
                all_windows = wt_session.get("all_windows", [])
                print("✅ Windows Terminal is running")
                print(f"   Session windows: {len(session_windows)}")
                print(f"   Total WT windows: {len(all_windows)}")
            else:
                print("⚠️  Windows Terminal is running but no session windows found")
        else:
            error_msg = wt_session.get("error", "Unknown error")
            print(f"❌ Windows Terminal session issue: {error_msg}")

        print()

        # Commands in this layout
        print(f"📋 COMMANDS ({summary['running_commands']}/{summary['total_commands']} running):")
        for tab_name, cmd_status in commands.items():
            status_icon = "✅" if cmd_status.get("running", False) else "❌"
            cmd_text = cmd_status.get("command", "Unknown")[:50]
            if len(cmd_status.get("command", "")) > 50:
                cmd_text += "..."

            print(f"   {status_icon} {tab_name}: {cmd_text}")

            if cmd_status.get("processes"):
                for proc in cmd_status["processes"][:2]:  # Show first 2 processes
                    pid = proc.get("pid", "Unknown")
                    name = proc.get("name", "Unknown")
                    print(f"      └─ PID {pid}: {name}")
        print()

        print("=" * 80)


def create_wt_layout(layout_config: LayoutConfig, output_dir: Optional[str]) -> str:
    generator = WTLayoutGenerator()
    return generator.create_wt_layout(layout_config, output_dir)


def run_wt_layout(layout_config: LayoutConfig) -> str:
    """Create and run a Windows Terminal layout."""
    generator = WTLayoutGenerator()
    script_path = generator.create_wt_layout(layout_config, None)

    # Execute the script
    cmd = f'powershell -ExecutionPolicy Bypass -File "{script_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Windows Terminal layout is running @ {layout_config['layoutName']}")
        return script_path
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
    # Example usage with new schema
    sample_layout: LayoutConfig = {"layoutName": "TestLayout", "layoutTabs": [{"tabName": "Frontend", "startDir": "~/code", "command": "btm"}, {"tabName": "Monitor", "startDir": "~", "command": "lf"}]}

    try:
        # Create layout using the generator
        generator = WTLayoutGenerator()
        script_path = generator.create_wt_layout(sample_layout, None)
        print(f"✅ Windows Terminal layout created: {script_path}")

        # Show preview
        preview = generator.get_wt_layout_preview(sample_layout)
        print(f"\n📋 Command Preview:\n{preview}")

        # Check status (won't find anything since we haven't run it)
        print("\n🔍 Current status:")
        generator.print_status_report()

        # Show how to run the layout
        print("\n▶️  To run this layout, execute:")
        print(f'   powershell -ExecutionPolicy Bypass -File "{script_path}"')

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
