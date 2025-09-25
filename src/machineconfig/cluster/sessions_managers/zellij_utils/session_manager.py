#!/usr/bin/env python3
"""
Zellij session management utilities for remote operations.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from rich.console import Console

from machineconfig.cluster.sessions_managers.zellij_utils.remote_executor import RemoteExecutor

logger = logging.getLogger(__name__)
console = Console()


class SessionManager:
    """Handles Zellij session operations on remote machines."""

    def __init__(self, remote_executor: RemoteExecutor, session_name: str, tmp_layout_dir: Path):
        self.remote_executor = remote_executor
        self.session_name = session_name
        self.tmp_layout_dir = tmp_layout_dir

    def copy_layout_to_remote(self, local_layout_file: Path, random_suffix: str) -> str:
        """Copy the layout file to the remote machine and return the remote path."""
        remote_layout_dir = f"~/{self.tmp_layout_dir.relative_to(Path.home())}"
        remote_layout_file = f"{remote_layout_dir}/zellij_layout_{self.session_name}_{random_suffix}.kdl"

        # Create remote directory
        if not self.remote_executor.create_remote_directory(remote_layout_dir):
            raise RuntimeError(f"Failed to create remote directory: {remote_layout_dir}")

        # Copy layout file to remote machine
        copy_result = self.remote_executor.copy_file_to_remote(str(local_layout_file), remote_layout_file)
        if not copy_result["success"]:
            raise RuntimeError(f"Failed to copy layout file to remote: {copy_result['error']}")

        # Enhanced Rich logging
        console.print(f"[bold green]📁 Zellij layout file copied to remote:[/bold green] [yellow]{self.remote_executor.remote_name}[/yellow][cyan]:{remote_layout_file}[/cyan]")
        return remote_layout_file

    def check_zellij_session_status(self) -> Dict[str, Any]:
        """Check if the Zellij session exists and is running."""
        try:
            result = self.remote_executor.run_command("zellij list-sessions", timeout=10)

            if result.returncode == 0:
                sessions = result.stdout.strip().split("\n") if result.stdout.strip() else []
                session_running = any(self.session_name in session for session in sessions)

                return {"zellij_running": True, "session_exists": session_running, "session_name": self.session_name, "all_sessions": sessions, "remote": self.remote_executor.remote_name}
            else:
                return {"zellij_running": False, "error": result.stderr, "session_name": self.session_name, "remote": self.remote_executor.remote_name}

        except Exception as e:
            return {"zellij_running": False, "error": str(e), "session_name": self.session_name, "remote": self.remote_executor.remote_name}

    def start_zellij_session(self, layout_file_path: Optional[str]) -> Dict[str, Any]:
        """Start a Zellij session on the remote machine with the generated layout."""
        try:
            if layout_file_path:
                layout_filename = Path(layout_file_path).name
                remote_layout_file = f"~/{self.tmp_layout_dir.relative_to(Path.home())}/{layout_filename}"
            else:
                raise ValueError("No layout file path provided.")

            # Enhanced Rich logging for session start
            console.print(
                f"[bold cyan]🚀 Starting Zellij session[/bold cyan] [yellow]'{self.session_name}'[/yellow] [dim]on remote[/dim] [bold yellow]'{self.remote_executor.remote_name}'[/bold yellow] [dim]with layout:[/dim] [blue]{remote_layout_file}[/blue]"
            )

            # Start Zellij session with layout
            start_cmd = f"zellij --layout {remote_layout_file} a -b {self.session_name}"
            console.print(f"[dim]Executing:[/dim] [green]{start_cmd}[/green]")
            result = self.remote_executor.run_command(start_cmd, timeout=30)

            if result.returncode == 0:
                console.print(f"[bold green]✅ Zellij session[/bold green] [yellow]'{self.session_name}'[/yellow] [green]started successfully on[/green] [bold yellow]{self.remote_executor.remote_name}[/bold yellow]")
                return {"success": True, "session_name": self.session_name, "remote": self.remote_executor.remote_name, "message": "Session started successfully"}
            else:
                return {"success": False, "error": result.stderr, "session_name": self.session_name, "remote": self.remote_executor.remote_name}

        except Exception as e:
            logger.error(f"Failed to start Zellij session on {self.remote_executor.remote_name}: {e}")
            return {"success": False, "error": str(e), "session_name": self.session_name, "remote": self.remote_executor.remote_name}

    def attach_to_session(self) -> None:
        """Attach to the Zellij session on the remote machine via SSH."""
        self.remote_executor.attach_to_session_interactive(self.session_name)
