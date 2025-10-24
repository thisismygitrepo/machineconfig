import subprocess
import random
import string
import json
import shlex
import logging
from typing import Any
from pathlib import Path

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig

logger = logging.getLogger(__name__)

POWERSHELL_CMD = "powershell" if __import__("platform").system().lower() == "windows" else "pwsh"


def generate_random_suffix(length: int) -> str:
    """Generate a random string suffix for unique PowerShell script names."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def parse_command(command: str) -> tuple[str, list[str]]:
    try:
        parts = shlex.split(command)
        if not parts:
            raise ValueError("Empty command provided")
        return parts[0], parts[1:] if len(parts) > 1 else []
    except ValueError as e:
        logger.error(f"Error parsing command '{command}': {e}")
        parts = command.split()
        return parts[0] if parts else "", parts[1:] if len(parts) > 1 else []


def escape_for_wt(text: str) -> str:
    """Escape text for use in Windows Terminal commands."""
    text = text.replace('"', '""')
    if " " in text or ";" in text or "&" in text or "|" in text:
        return f'"{text}"'
    return text


def validate_layout_config(layout_config: LayoutConfig) -> None:
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


def generate_wt_command_string(layout_config: LayoutConfig, window_name: str) -> str:
    """Generate complete Windows Terminal command string."""
    command_parts = []
    
    for i, tab in enumerate(layout_config["layoutTabs"]):
        is_first = i == 0
        
        if is_first:
            tab_parts = ["wt", "-w", escape_for_wt(window_name)]
        else:
            tab_parts = ["new-tab"]
        
        tab_name = tab["tabName"]
        cwd = tab["startDir"]
        command = tab["command"]
        
        if cwd.startswith("~/"):
            cwd = cwd.replace("~/", f"{Path.home()}/")
        elif cwd == "~":
            cwd = str(Path.home())
        
        tab_parts.extend(["-d", escape_for_wt(cwd)])
        tab_parts.extend(["--title", escape_for_wt(tab_name)])
        tab_parts.append("--")
        
        # Split the command into arguments
        command_args = shlex.split(command)
        tab_parts.extend(command_args)
        
        command_parts.append(" ".join(tab_parts))
    
    return " `; ".join(command_parts)


def check_wt_session_status(session_name: str) -> dict[str, Any]:
    try:
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

                    return {"wt_running": True, "session_exists": len(processes) > 0, "session_name": session_name, "all_windows": processes, "session_windows": processes}
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


def check_command_status(tab_name: str, layout_config: LayoutConfig) -> dict[str, Any]:
    """Check if a command is running by looking for processes."""
    tab_config = None
    for tab in layout_config["layoutTabs"]:
        if tab["tabName"] == tab_name:
            tab_config = tab
            break

    if tab_config is None:
        return {"status": "unknown", "error": f"Tab '{tab_name}' not found in layout config", "running": False, "pid": None, "command": None}

    command = tab_config["command"]

    try:
        primary_cmd = command.split()[0] if command.strip() else ""
        if not primary_cmd:
            return {"status": "error", "error": "Empty command", "running": False, "command": command, "tab_name": tab_name}

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
