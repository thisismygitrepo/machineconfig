#!/usr/bin/env python3
"""
Remote command execution utilities for SSH operations with Windows Terminal.
Adapted from zellij remote executor but focused on Windows Terminal commands.
"""

import subprocess
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class WTRemoteExecutor:
    """Handles SSH command execution on remote Windows machines with Windows Terminal."""

    def __init__(self, remote_name: str):
        self.remote_name = remote_name

    def run_command(self, command: str, timeout: int = 30, shell: str = "powershell") -> subprocess.CompletedProcess[str]:
        """Execute a command on the remote machine via SSH."""
        # For Windows Terminal on remote machines, we need to use PowerShell or CMD
        if shell == "powershell":
            # Wrap command in PowerShell invocation if needed
            if not command.startswith("powershell"):
                command = f'powershell -Command "{command}"'

        ssh_cmd = ["ssh", self.remote_name, command]
        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"SSH command timed out after {timeout}s: {command}")
            raise
        except Exception as e:
            logger.error(f"SSH command failed: {e}")
            raise

    def copy_file_to_remote(self, local_file: str, remote_path: str) -> Dict[str, Any]:
        """Copy a file to the remote machine using SCP."""
        scp_cmd = ["scp", local_file, f"{self.remote_name}:{remote_path}"]
        try:
            result = subprocess.run(scp_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"File copied successfully to {self.remote_name}:{remote_path}")
                return {"success": True, "remote_path": remote_path}
            else:
                logger.error(f"SCP failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
        except Exception as e:
            logger.error(f"SCP operation failed: {e}")
            return {"success": False, "error": str(e)}

    def create_remote_directory(self, remote_dir: str) -> bool:
        """Create a directory on the remote machine."""
        try:
            # Use PowerShell mkdir which creates parent directories automatically
            result = self.run_command(f"New-Item -ItemType Directory -Path '{remote_dir}' -Force")
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to create remote directory {remote_dir}: {e}")
            return False

    def start_wt_session_interactive(self, wt_command: str) -> None:
        """Start a Windows Terminal session interactively via SSH."""
        try:
            # For interactive Windows Terminal, we need to use SSH with a TTY
            ssh_cmd = ["ssh", "-t", self.remote_name, wt_command]
            logger.info(f"Starting Windows Terminal session on {self.remote_name}")
            subprocess.run(ssh_cmd)
        except Exception as e:
            logger.error(f"Failed to start Windows Terminal session: {e}")
            raise

    def check_wt_available(self) -> bool:
        """Check if Windows Terminal is available on the remote machine."""
        try:
            result = self.run_command("where wt", timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    def get_remote_windows_info(self) -> Dict[str, Any]:
        """Get information about the remote Windows system."""
        try:
            # Get Windows version and terminal info
            version_cmd = "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion"
            result = self.run_command(version_cmd, timeout=15)

            wt_available = self.check_wt_available()

            return {"windows_info": result.stdout if result.returncode == 0 else "Unknown", "wt_available": wt_available, "remote_name": self.remote_name}
        except Exception as e:
            logger.error(f"Failed to get remote Windows info: {e}")
            return {"windows_info": "Error getting info", "wt_available": False, "remote_name": self.remote_name, "error": str(e)}

    def run_wt_command(self, wt_command: str, detached: bool = True) -> subprocess.CompletedProcess[str]:
        """Run a Windows Terminal command on the remote machine."""
        try:
            if detached:
                # Run in detached mode (background)
                full_command = f"Start-Process -FilePath 'wt' -ArgumentList '{wt_command}' -WindowStyle Hidden"
            else:
                # Run in foreground
                full_command = f"wt {wt_command}"

            return self.run_command(full_command, timeout=30)
        except Exception as e:
            logger.error(f"Failed to run Windows Terminal command: {e}")
            raise

    def list_wt_processes(self) -> Dict[str, Any]:
        """List Windows Terminal processes on the remote machine."""
        try:
            # Get all WindowsTerminal.exe processes
            ps_command = "Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, CPU"
            result = self.run_command(ps_command, timeout=15)

            if result.returncode == 0:
                return {"success": True, "processes": result.stdout, "remote": self.remote_name}
            else:
                return {"success": False, "error": result.stderr, "remote": self.remote_name}
        except Exception as e:
            logger.error(f"Failed to list Windows Terminal processes: {e}")
            return {"success": False, "error": str(e), "remote": self.remote_name}

    def kill_wt_processes(self, process_ids: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Kill Windows Terminal processes on the remote machine."""
        try:
            if process_ids:
                # Kill specific processes
                kill_cmd = f"Stop-Process -Id {','.join(map(str, process_ids))} -Force"
            else:
                # Kill all Windows Terminal processes
                kill_cmd = "Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | Stop-Process -Force"

            result = self.run_command(kill_cmd, timeout=10)

            return {"success": result.returncode == 0, "message": "Processes killed" if result.returncode == 0 else result.stderr, "remote": self.remote_name}
        except Exception as e:
            logger.error(f"Failed to kill Windows Terminal processes: {e}")
            return {"success": False, "error": str(e), "remote": self.remote_name}
