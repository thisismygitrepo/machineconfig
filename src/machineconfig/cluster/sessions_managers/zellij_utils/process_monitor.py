#!/usr/bin/env python3
"""
Process monitoring and status checking utilities for remote commands.
"""

import json
import shlex
import logging
from typing import Dict
from machineconfig.cluster.sessions_managers.zellij_utils.remote_executor import RemoteExecutor
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig
from machineconfig.cluster.sessions_managers.zellij_utils.monitoring_types import CommandStatus, ProcessInfo

logger = logging.getLogger(__name__)


class ProcessMonitor:
    """Handles process status checking and verification on remote machines."""

    def __init__(self, remote_executor: RemoteExecutor):
        self.remote_executor = remote_executor

    def check_command_status(self, tab_name: str, layout_config: LayoutConfig, use_verification: bool) -> CommandStatus:
        """Check command status with optional process verification."""
        # Find the tab with the given name
        tab_config = None
        for tab in layout_config["layoutTabs"]:
            if tab["tabName"] == tab_name:
                tab_config = tab
                break

        if tab_config is None:
            return {"status": "unknown", "error": f"Tab '{tab_name}' not found in layout config", "running": False, "command": "", "tab_name": tab_name, "processes": [], "remote": self.remote_executor.remote_name}

        # Use the verified method by default for more accurate results
        if use_verification:
            return self.get_verified_process_status(tab_name, layout_config)

        return self._basic_process_check(tab_name, layout_config)

    def _basic_process_check(self, tab_name: str, layout_config: LayoutConfig) -> CommandStatus:
        """Basic process checking without verification."""
        # Find the tab with the given name
        tab_config = None
        for tab in layout_config["layoutTabs"]:
            if tab["tabName"] == tab_name:
                tab_config = tab
                break

        if tab_config is None:
            return {"status": "unknown", "error": f"Tab '{tab_name}' not found in layout config", "running": False, "command": "", "tab_name": tab_name, "processes": [], "remote": self.remote_executor.remote_name}

        command = tab_config["command"]
        try:
            check_script = self._create_process_check_script(command)
            remote_cmd = f"$HOME/.local/bin devops self python -c {shlex.quote(check_script)}"
            result = self.remote_executor.run_command(remote_cmd, timeout=15)
            if result.returncode == 0:
                try:
                    matching_processes = json.loads(result.stdout.strip())

                    if matching_processes:
                        return {"status": "running", "running": True, "processes": matching_processes, "command": command, "tab_name": tab_name, "remote": self.remote_executor.remote_name}
                    else:
                        return {"status": "not_running", "running": False, "processes": [], "command": command, "tab_name": tab_name, "remote": self.remote_executor.remote_name}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse remote process check output: {e}")
                    return {"status": "error", "error": f"Failed to parse remote output: {e}", "running": False, "processes": [], "command": command, "tab_name": tab_name, "remote": self.remote_executor.remote_name}
            else:
                return {"status": "error", "error": f"Remote command failed: {result.stderr}", "running": False, "processes": [], "command": command, "tab_name": tab_name, "remote": self.remote_executor.remote_name}

        except Exception as e:
            logger.error(f"Error checking command status for tab '{tab_name}': {e}")
            return {"status": "error", "error": str(e), "running": False, "processes": [], "command": command, "tab_name": tab_name, "remote": self.remote_executor.remote_name}

    def _create_process_check_script(self, command: str) -> str:
        """Create Python script for checking processes on remote machine."""
        return f"""
import psutil
import json
import os

def check_process():
    matching_processes = []
    full_command = '{command}'
    cmd_parts = [part for part in full_command.split() if len(part) > 2]
    current_pid = os.getpid()

    primary_cmd = cmd_parts[0] if cmd_parts else ''

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
        try:
            if proc.info['pid'] == current_pid:
                continue

            if proc.info['cmdline'] and len(proc.info['cmdline']) > 0:
                cmdline_str = ' '.join(proc.info['cmdline'])

                if 'check_process()' in cmdline_str or 'psutil.process_iter' in cmdline_str:
                    continue

                matches_primary = primary_cmd in cmdline_str
                matches_parts = sum(1 for part in cmd_parts[1:] if part in cmdline_str)

                if (matches_primary and matches_parts >= 2) or \\
                   (full_command in cmdline_str and not any(python_indicator in cmdline_str.lower()
                                                           for python_indicator in ['python -c', 'import psutil', 'def check_process'])):
                    matching_processes.append({{
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline": proc.info['cmdline'],
                        "status": proc.info['status'],
                        "cmdline_str": cmdline_str,
                        "create_time": proc.info['create_time']
                    }})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return matching_processes

if __name__ == "__main__":
    processes = check_process()
    print(json.dumps(processes))
"""

    def force_fresh_process_check(self, tab_name: str, layout_config: LayoutConfig) -> CommandStatus:
        """Force a fresh process check with additional validation."""
        for tab in layout_config["layoutTabs"]:
            if tab["tabName"] == tab_name:
                tab_config = tab
                break
        else:
            return {"status": "unknown", "error": f"Tab '{tab_name}' not found in layout config", "running": False, "command": "", "tab_name": tab_name, "processes": [], "remote": self.remote_executor.remote_name}
        command = tab_config["command"]

        try:
            # Get timestamp for freshness validation
            timestamp_result = self.remote_executor.run_command("date +%s", timeout=5)
            check_timestamp = timestamp_result.stdout.strip() if timestamp_result.returncode == 0 else "unknown"

            check_script = self._create_fresh_check_script(command)
            remote_cmd = f"$HOME/.local/bin/devops self python -c {shlex.quote(check_script)}"
            result = self.remote_executor.run_command(remote_cmd, timeout=15)

            if result.returncode == 0:
                try:
                    check_result = json.loads(result.stdout.strip())
                    raw_processes = check_result.get("processes", [])
                    matching_processes: list[ProcessInfo] = raw_processes  # runtime JSON provides shape

                    return {
                        "status": "running" if matching_processes else "not_running",
                        "running": bool(matching_processes),
                        "processes": matching_processes,
                        "command": command,
                        "tab_name": tab_name,
                        "remote": self.remote_executor.remote_name,
                        "check_timestamp": check_timestamp,
                        "method": "force_fresh_check",
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse fresh check output: {e}")
                    return {"status": "error", "error": f"Failed to parse output: {e}", "running": False, "processes": [], "command": command, "tab_name": tab_name, "remote": self.remote_executor.remote_name, "raw_output": result.stdout}
            else:
                return {"status": "error", "error": f"Remote command failed: {result.stderr}", "running": False, "processes": [], "command": command, "tab_name": tab_name, "remote": self.remote_executor.remote_name}

        except Exception as e:
            logger.error(f"Error in fresh process check for tab '{tab_name}': {e}")
            return {"status": "error", "error": str(e), "running": False, "processes": [], "command": command, "tab_name": tab_name, "remote": self.remote_executor.remote_name}

    def _create_fresh_check_script(self, command: str) -> str:
        """Create enhanced process checking script with freshness validation."""
        escaped_command = command.replace("'", "\\'").replace('"', '\\"')

        return f"""
import psutil
import json
import os
import time

def force_fresh_check():
    time.sleep(0.1)

    matching_processes = []
    full_command = '{escaped_command}'
    cmd_parts = [part for part in full_command.split() if len(part) > 2]
    current_pid = os.getpid()
    primary_cmd = cmd_parts[0] if cmd_parts else ''

    check_time = time.time()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
        try:
            if proc.info['pid'] == current_pid:
                continue

            if proc.info['cmdline'] and len(proc.info['cmdline']) > 0:
                cmdline_str = ' '.join(proc.info['cmdline'])

                if any(indicator in cmdline_str for indicator in [
                    'check_process()', 'psutil.process_iter', 'force_fresh_check',
                    'import psutil', 'def check_process'
                ]):
                    continue

                if proc.info['create_time'] and proc.info['create_time'] > check_time - 5:
                    continue

                matches_primary = primary_cmd in cmdline_str and primary_cmd != 'python'
                matches_parts = sum(1 for part in cmd_parts[1:] if part in cmdline_str)

                if matches_primary and matches_parts >= 2:
                    script_indicators = ['-c', 'import ', 'def ', 'psutil']
                    is_direct_command = not any(script_indicator in cmdline_str.lower()
                                              for script_indicator in script_indicators)

                    if is_direct_command or (full_command in cmdline_str and 'python -c' not in cmdline_str):
                        matching_processes.append({{
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cmdline": proc.info['cmdline'],
                            "status": proc.info['status'],
                            "cmdline_str": cmdline_str,
                            "create_time": proc.info['create_time'],
                            "is_direct_command": is_direct_command
                        }})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return {{
        "processes": matching_processes,
        "check_timestamp": check_time,
        "search_command": full_command,
        "search_parts": cmd_parts
    }}

if __name__ == "__main__":
    result = force_fresh_check()
    print(json.dumps(result))
"""

    def verify_process_alive(self, pid: int) -> bool:
        """Verify if a process with given PID is actually alive."""
        try:
            verify_cmd = f"kill -0 {pid} 2>/dev/null && echo 'alive' || echo 'dead'"
            result = self.remote_executor.run_command(verify_cmd, timeout=5)

            if result.returncode == 0:
                return result.stdout.strip() == "alive"
            return False
        except Exception:
            return False

    def get_verified_process_status(self, tab_name: str, layout_config: LayoutConfig) -> CommandStatus:
        """Get process status with additional verification that processes are actually alive."""
        status = self.force_fresh_process_check(tab_name, layout_config)

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
            status["verification_method"] = "kill_signal_check"

        return status

    def check_all_commands_status(self, layout_config: LayoutConfig) -> Dict[str, CommandStatus]:
        """Check status of all commands in the layout configuration."""
        if not layout_config or not layout_config.get("layoutTabs"):
            logger.warning("No layout configuration provided.")
            return {}

        status_report = {}
        for tab in layout_config["layoutTabs"]:
            tab_name = tab["tabName"]
            status_report[tab_name] = self.check_command_status(tab_name, layout_config, True)
        return status_report
