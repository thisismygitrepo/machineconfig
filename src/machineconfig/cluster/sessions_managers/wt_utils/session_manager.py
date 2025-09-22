#!/usr/bin/env python3
"""
Windows Terminal session management utilities for local and remote operations.
"""

import logging
import subprocess
from typing import Optional, TypedDict, NotRequired
from pathlib import Path
from machineconfig.cluster.sessions_managers.wt_utils.remote_executor import WTRemoteExecutor

logger = logging.getLogger(__name__)


class WTProcessInfo(TypedDict, total=False):
    Id: int
    ProcessName: str
    StartTime: str
    MainWindowTitle: str


class CheckWTSessionStatusResult(TypedDict):
    wt_running: bool
    session_exists: bool
    session_name: str
    location: str
    all_windows: NotRequired[list[WTProcessInfo]]
    session_windows: NotRequired[list[WTProcessInfo]]
    error: NotRequired[str]


class StartWTSessionResult(TypedDict):
    success: bool
    session_name: str
    location: str
    message: NotRequired[str]
    error: NotRequired[str]


class KillWTSessionResult(TypedDict):
    success: bool
    session_name: str
    location: str
    message: NotRequired[str]
    error: NotRequired[str]


class CreateNewTabResult(TypedDict):
    success: bool
    tab_name: str
    command: str
    location: str
    message: NotRequired[str]
    error: NotRequired[str]


class GetWTVersionResult(TypedDict):
    success: bool
    location: str
    version: NotRequired[str]
    error: NotRequired[str]


class WTSessionManager:
    """Handles Windows Terminal session operations on local and remote machines."""

    def __init__(self, remote_executor: Optional[WTRemoteExecutor] = None, session_name: str = "default", tmp_layout_dir: Path | None = None):
        self.remote_executor = remote_executor
        self.session_name = session_name
        self.tmp_layout_dir = tmp_layout_dir or Path.home() / "tmp_results" / "wt_layouts" / "layout_manager"
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

    def copy_script_to_remote(self, local_script_file: Path, random_suffix: str) -> str:
        """Copy the script file to the remote machine and return the remote path."""
        if self.is_local:
            # For local operations, just return the local path
            return str(local_script_file)

        if self.remote_executor is None:
            raise ValueError("Remote executor is None but operation requires remote access")

        remote_layout_dir = f"~/{self.tmp_layout_dir.relative_to(Path.home())}"
        remote_script_file = f"{remote_layout_dir}/wt_script_{self.session_name}_{random_suffix}.ps1"

        # Create remote directory
        if not self.remote_executor.create_remote_directory(remote_layout_dir):
            raise RuntimeError(f"Failed to create remote directory: {remote_layout_dir}")

        # Copy script file to remote machine
        copy_result = self.remote_executor.copy_file_to_remote(str(local_script_file), remote_script_file)
        if not copy_result["success"]:
            raise RuntimeError(f"Failed to copy script file to remote: {copy_result['error']}")

        logger.info(f"Windows Terminal script file copied to remote: {self.remote_executor.remote_name}:{remote_script_file}")
        return remote_script_file

    def check_wt_session_status(self) -> CheckWTSessionStatusResult:
        """Check if Windows Terminal windows exist and are running."""
        try:
            # Check for Windows Terminal processes
            wt_check_cmd = """
Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue |
Select-Object Id, ProcessName, StartTime, MainWindowTitle |
ConvertTo-Json -Depth 2
"""
            result = self._run_command(wt_check_cmd, timeout=10)

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
                            if self.session_name in window_title or not window_title:
                                session_windows.append(proc)

                        return {"wt_running": True, "session_exists": len(session_windows) > 0, "session_name": self.session_name, "all_windows": processes, "session_windows": session_windows, "location": self.location_name}
                    except Exception as e:
                        logger.error(f"Failed to parse Windows Terminal process info: {e}")
                        return {"wt_running": True, "session_exists": False, "error": f"Failed to parse process info: {e}", "session_name": self.session_name, "location": self.location_name}
                else:
                    return {"wt_running": False, "session_exists": False, "session_name": self.session_name, "all_windows": [], "location": self.location_name}
            else:
                return {"wt_running": False, "session_exists": False, "error": result.stderr, "session_name": self.session_name, "location": self.location_name}

        except Exception as e:
            return {"wt_running": False, "session_exists": False, "error": str(e), "session_name": self.session_name, "location": self.location_name}

    def start_wt_session(self, script_file_path: Optional[str] = None, wt_command: Optional[str] = None) -> StartWTSessionResult:
        """Start a Windows Terminal session with the generated layout."""
        try:
            if script_file_path:
                # Execute the script file
                if self.is_local:
                    script_path = script_file_path
                else:
                    script_filename = Path(script_file_path).name
                    script_path = f"~/{self.tmp_layout_dir.relative_to(Path.home())}/{script_filename}"

                logger.info(f"Starting Windows Terminal session '{self.session_name}' with script: {script_path}")

                # Execute the PowerShell script
                if self.is_local:
                    start_cmd = f"& '{script_path}'"
                else:
                    start_cmd = f"powershell -ExecutionPolicy Bypass -File '{script_path}'"

            elif wt_command:
                # Execute the wt command directly
                logger.info(f"Starting Windows Terminal session '{self.session_name}' with command: {wt_command}")
                start_cmd = wt_command
            else:
                raise ValueError("Either script_file_path or wt_command must be provided.")

            logger.info(f"Executing command: {start_cmd}")
            result = self._run_command(start_cmd, timeout=30)

            if result.returncode == 0:
                logger.info(f"Windows Terminal session '{self.session_name}' started successfully")
                return {"success": True, "session_name": self.session_name, "location": self.location_name, "message": "Session started successfully"}
            else:
                return {"success": False, "error": result.stderr or result.stdout, "session_name": self.session_name, "location": self.location_name}

        except Exception as e:
            error_location = "locally" if self.is_local else f"on {self.remote_executor.remote_name if self.remote_executor else 'unknown'}"
            logger.error(f"Failed to start Windows Terminal session {error_location}: {e}")
            return {"success": False, "error": str(e), "session_name": self.session_name, "location": self.location_name}

    def attach_to_session(self, window_name: Optional[str] = None) -> None:
        """Attach to a Windows Terminal session/window."""
        try:
            if self.is_local:
                # For local sessions, try to focus existing window or create new one
                if window_name:
                    attach_cmd = f"wt -w {window_name}"
                else:
                    attach_cmd = f"wt -w {self.session_name}"

                logger.info(f"Attaching to local Windows Terminal window '{window_name or self.session_name}'")
                subprocess.run(attach_cmd, shell=True)
            else:
                # For remote sessions, use SSH with interactive terminal
                if self.remote_executor is None:
                    raise ValueError("Remote executor is None but operation requires remote access")

                if window_name:
                    attach_cmd = f"wt -w {window_name}"
                else:
                    attach_cmd = f"wt -w {self.session_name}"

                self.remote_executor.start_wt_session_interactive(attach_cmd)
        except Exception as e:
            logger.error(f"Failed to attach to Windows Terminal session: {e}")
            raise

    def kill_wt_session(self, force: bool = True) -> KillWTSessionResult:
        """Kill Windows Terminal processes related to this session."""
        try:
            if force:
                # Kill all Windows Terminal processes
                kill_cmd = "Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | Stop-Process -Force"
            else:
                # Try to gracefully close windows (this is harder to target specific windows)
                kill_cmd = "Get-Process -Name 'WindowsTerminal' -ErrorAction SilentlyContinue | ForEach-Object { $_.CloseMainWindow() }"

            logger.info(f"Killing Windows Terminal session '{self.session_name}'")
            result = self._run_command(kill_cmd, timeout=10)

            return {"success": result.returncode == 0, "message": "Session killed" if result.returncode == 0 else result.stderr, "session_name": self.session_name, "location": self.location_name}

        except Exception as e:
            logger.error(f"Failed to kill Windows Terminal session: {e}")
            return {"success": False, "error": str(e), "session_name": self.session_name, "location": self.location_name}

    def create_new_tab(self, tab_name: str, cwd: str, command: str, window_name: Optional[str] = None) -> CreateNewTabResult:
        """Create a new tab in the Windows Terminal session."""
        try:
            # Build the new-tab command
            tab_cmd_parts = ["wt"]

            if window_name:
                tab_cmd_parts.extend(["-w", f'"{window_name}"'])

            tab_cmd_parts.append("new-tab")
            tab_cmd_parts.extend(["-d", f'"{cwd}"'])
            tab_cmd_parts.extend(["--title", f'"{tab_name}"'])
            tab_cmd_parts.append(f'"{command}"')

            new_tab_cmd = " ".join(tab_cmd_parts)

            logger.info(f"Creating new tab '{tab_name}' in Windows Terminal")
            result = self._run_command(new_tab_cmd, timeout=15)

            return {"success": result.returncode == 0, "message": f"Tab '{tab_name}' created" if result.returncode == 0 else result.stderr, "tab_name": tab_name, "command": command, "location": self.location_name}

        except Exception as e:
            logger.error(f"Failed to create new tab '{tab_name}': {e}")
            return {"success": False, "error": str(e), "tab_name": tab_name, "command": command, "location": self.location_name}

    def get_wt_version(self) -> GetWTVersionResult:
        """Get Windows Terminal version information."""
        try:
            version_cmd = "wt --version"
            result = self._run_command(version_cmd, timeout=10)

            return {"success": result.returncode == 0, "version": result.stdout.strip() if result.returncode == 0 else "Unknown", "location": self.location_name}
        except Exception as e:
            return {"success": False, "error": str(e), "location": self.location_name}
