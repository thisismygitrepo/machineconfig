#!/usr/bin/env python3
"""
Process monitoring and status checking utilities for Windows Terminal commands.
Adapted from zellij process monitor but focused on Windows processes.
"""

import json
import logging
import subprocess
from typing import Dict, Any, Optional, List
from machineconfig.utils.schemas.layouts.layout_types import TabConfig
from machineconfig.cluster.sessions_managers.wt_utils.remote_executor import WTRemoteExecutor

logger = logging.getLogger(__name__)


class WTProcessMonitor:
    """Handles process status checking and verification on local and remote Windows machines."""

    def __init__(self, remote_executor: Optional[WTRemoteExecutor] = None):
        self.remote_executor = remote_executor
        self.is_local = remote_executor is None

    @property
    def location_name(self) -> str:
        """Get the location name for status reporting."""
        return "local" if self.is_local else (self.remote_executor.remote_name if self.remote_executor else "unknown")

    def _run_command(self, command: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
        """Run command either locally or remotely."""
        if self.is_local:
            return subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=timeout)
        else:
            if self.remote_executor is None:
                raise ValueError("Remote executor is None but is_local is False")
            return self.remote_executor.run_command(command, timeout)

    def check_command_status(self, tab_name: str, tabs: List[TabConfig], use_verification: bool = True) -> Dict[str, Any]:
        """Check command status with optional process verification."""
        the_tab = next((t for t in tabs if t["tabName"] == tab_name), None)
        if the_tab is None:
            return {"status": "unknown", "error": f"Tab '{tab_name}' not found in tracked configuration", "running": False, "pid": None, "command": None, "location": self.location_name}

        # Use the verified method by default for more accurate results
        if use_verification:
            return self.get_verified_process_status(tab_name, tabs)

        return self._basic_process_check(tab_name, tabs)

    def _basic_process_check(self, tab_name: str, tabs: List[TabConfig]) -> Dict[str, Any]:
        """Basic process checking without verification."""
        the_tab = next((t for t in tabs if t["tabName"] == tab_name), None)
        command = the_tab["command"] if the_tab is not None else ""

        try:
            check_script = self._create_process_check_script(command)
            result = self._run_command(check_script, timeout=15)

            if result.returncode == 0:
                try:
                    # Parse PowerShell output (JSON format)
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
                        return {"status": "running", "running": True, "processes": matching_processes, "command": command, "tab_name": tab_name, "location": self.location_name}
                    else:
                        return {"status": "not_running", "running": False, "processes": [], "command": command, "tab_name": tab_name, "location": self.location_name}
                except Exception as e:
                    logger.error(f"Failed to parse process check output: {e}")
                    return {"status": "error", "error": f"Failed to parse output: {e}", "running": False, "command": command, "tab_name": tab_name, "location": self.location_name}
            else:
                return {"status": "error", "error": f"Command failed: {result.stderr}", "running": False, "command": command, "tab_name": tab_name, "location": self.location_name}

        except Exception as e:
            logger.error(f"Error checking command status for tab '{tab_name}': {e}")
            return {"status": "error", "error": str(e), "running": False, "command": command, "tab_name": tab_name, "location": self.location_name}

    def _create_process_check_script(self, command: str) -> str:
        """Create PowerShell script for checking processes."""
        # Escape command for PowerShell
        escaped_command = command.replace("'", "''").replace('"', '""')
        cmd_parts = [part for part in command.split() if len(part) > 2]
        primary_cmd = cmd_parts[0] if cmd_parts else ""

        return f"""
$targetCommand = '{escaped_command}'
$cmdParts = @({", ".join([f"'{part}'" for part in cmd_parts])})
$primaryCmd = '{primary_cmd}'
$currentPid = $PID

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

            if ($matchesPrimary -and $matchCount -ge 2) {{
                $procInfo = @{{
                    "pid" = $_.Id
                    "name" = $_.ProcessName
                    "cmdline" = $cmdline
                    "status" = $_.Status
                    "start_time" = $_.StartTime
                    "cpu_time" = $_.CPU
                }} | ConvertTo-Json -Compress
                Write-Output $procInfo
            }}
        }}
    }} catch {{
        # Ignore processes we can't access
    }}
}}
"""

    def force_fresh_process_check(self, tab_name: str, tabs: List[TabConfig]) -> Dict[str, Any]:
        """Force a fresh process check with additional validation."""
        the_tab = next((t for t in tabs if t["tabName"] == tab_name), None)
        if the_tab is None:
            return {"status": "unknown", "error": f"Tab '{tab_name}' not found in tracked configuration", "running": False, "command": None, "location": self.location_name}

        command = the_tab["command"]

        try:
            # Get timestamp for freshness validation
            timestamp_cmd = "Get-Date -UFormat %s"
            timestamp_result = self._run_command(timestamp_cmd, timeout=5)
            check_timestamp = timestamp_result.stdout.strip() if timestamp_result.returncode == 0 else "unknown"

            check_script = self._create_fresh_check_script(command)
            result = self._run_command(check_script, timeout=15)

            if result.returncode == 0:
                try:
                    # Parse the output to extract JSON
                    output_lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
                    for line in output_lines:
                        if line.startswith("{") and '"processes"' in line:
                            check_result = json.loads(line)
                            matching_processes = check_result.get("processes", [])

                            return {
                                "status": "running" if matching_processes else "not_running",
                                "running": bool(matching_processes),
                                "processes": matching_processes,
                                "command": command,
                                "tab_name": tab_name,
                                "location": self.location_name,
                                "check_timestamp": check_timestamp,
                                "method": "force_fresh_check",
                            }

                    # Fallback if no JSON found
                    return {"status": "not_running", "running": False, "processes": [], "command": command, "tab_name": tab_name, "location": self.location_name, "raw_output": result.stdout}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse fresh check output: {e}")
                    return {"status": "error", "error": f"Failed to parse output: {e}", "running": False, "command": command, "tab_name": tab_name, "location": self.location_name, "raw_output": result.stdout}
            else:
                return {"status": "error", "error": f"Command failed: {result.stderr}", "running": False, "command": command, "tab_name": tab_name, "location": self.location_name}

        except Exception as e:
            logger.error(f"Error in fresh process check for tab '{tab_name}': {e}")
            return {"status": "error", "error": str(e), "running": False, "command": command, "tab_name": tab_name, "location": self.location_name}

    def _create_fresh_check_script(self, command: str) -> str:
        """Create enhanced PowerShell process checking script with freshness validation."""
        escaped_command = command.replace("'", "''").replace('"', '""')
        cmd_parts = [part for part in command.split() if len(part) > 2]
        primary_cmd = cmd_parts[0] if cmd_parts else ""

        return f"""
Start-Sleep -Milliseconds 100

$targetCommand = '{escaped_command}'
$cmdParts = @({", ".join([f"'{part}'" for part in cmd_parts])})
$primaryCmd = '{primary_cmd}'
$currentPid = $PID
$checkTime = Get-Date
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
            # Skip our own checking processes
            if ($cmdline -like "*Get-Process*" -or $cmdline -like "*force_fresh_check*") {{ return }}

            # Skip processes that started very recently (likely our own scripts)
            if ($_.StartTime -and ($checkTime - $_.StartTime).TotalSeconds -lt 5) {{ return }}

            $matchesPrimary = $cmdline -like "*$primaryCmd*" -and $primaryCmd -ne "powershell"
            $matchCount = 0
            foreach ($part in $cmdParts[1..($cmdParts.Length-1)]) {{
                if ($cmdline -like "*$part*") {{ $matchCount++ }}
            }}

            if ($matchesPrimary -and $matchCount -ge 2) {{
                $isDirectCommand = -not ($cmdline -like "*-Command*" -or $cmdline -like "*Get-Process*")

                if ($isDirectCommand -or ($targetCommand -in $cmdline -and $cmdline -notlike "*powershell -Command*")) {{
                    $procInfo = @{{
                        "pid" = $_.Id
                        "name" = $_.ProcessName
                        "cmdline" = $cmdline
                        "status" = $_.Status
                        "start_time" = $_.StartTime
                        "cpu_time" = $_.CPU
                        "is_direct_command" = $isDirectCommand
                    }}
                    $matchingProcesses += $procInfo
                }}
            }}
        }}
    }} catch {{
        # Ignore processes we can't access
    }}
}}

$result = @{{
    "processes" = $matchingProcesses
    "check_timestamp" = $checkTime
    "search_command" = $targetCommand
    "search_parts" = $cmdParts
}} | ConvertTo-Json -Depth 3 -Compress

Write-Output $result
"""

    def verify_process_alive(self, pid: int) -> bool:
        """Verify if a process with given PID is actually alive."""
        try:
            verify_cmd = f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -First 1"
            result = self._run_command(verify_cmd, timeout=5)

            return result.returncode == 0 and result.stdout.strip() != ""
        except Exception:
            return False

    def get_verified_process_status(self, tab_name: str, tabs: List[TabConfig]) -> Dict[str, Any]:
        """Get process status with additional verification that processes are actually alive."""
        status = self.force_fresh_process_check(tab_name, tabs)

        if status.get("running") and status.get("processes"):
            verified_processes = []
            for proc in status["processes"]:
                pid = proc.get("pid")
                if pid and self.verify_process_alive(pid):
                    proc["verified_alive"] = True
                    verified_processes.append(proc)
                else:
                    proc["verified_alive"] = False
                    logger.warning(f"Process PID {pid} found in process list but not actually alive")

            status["processes"] = verified_processes
            status["running"] = bool(verified_processes)
            status["status"] = "running" if verified_processes else "not_running"
            status["verification_method"] = "get_process_check"

        return status

    def check_all_commands_status(self, tabs: List[TabConfig]) -> Dict[str, Dict[str, Any]]:
        """Check status of all commands in the tab configuration."""
        if not tabs:
            logger.warning("No tab configuration provided.")
            return {}

        status_report = {}
        for the_tab in tabs:
            tab_name = the_tab["tabName"]
            status_report[tab_name] = self.check_command_status(tab_name, tabs)
        return status_report

    def get_windows_terminal_windows(self) -> Dict[str, Any]:
        """Get information about currently running Windows Terminal windows."""
        try:
            wt_info_cmd = """
Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue |
Select-Object Id, ProcessName, StartTime, @{Name="WindowTitle";Expression={(Get-Process -Id $_.Id).MainWindowTitle}} |
ConvertTo-Json -Depth 2
"""
            result = self._run_command(wt_info_cmd, timeout=15)

            if result.returncode == 0 and result.stdout.strip():
                try:
                    wt_processes = json.loads(result.stdout)
                    return {"success": True, "windows": wt_processes if isinstance(wt_processes, list) else [wt_processes], "location": self.location_name}
                except json.JSONDecodeError:
                    return {"success": False, "error": "Failed to parse Windows Terminal process info", "location": self.location_name}
            else:
                return {"success": True, "windows": [], "message": "No Windows Terminal processes found", "location": self.location_name}
        except Exception as e:
            logger.error(f"Failed to get Windows Terminal windows: {e}")
            return {"success": False, "error": str(e), "location": self.location_name}
