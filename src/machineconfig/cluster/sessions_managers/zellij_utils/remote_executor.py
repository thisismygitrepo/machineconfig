#!/usr/bin/env python3
"""
Remote command execution utilities for SSH operations.
"""

import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RemoteExecutor:
    """Handles SSH command execution on remote machines."""

    def __init__(self, remote_name: str):
        self.remote_name = remote_name

    def run_command(self, command: str, timeout: int) -> subprocess.CompletedProcess[str]:
        """Execute a command on the remote machine via SSH."""
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
            result = self.run_command(f"mkdir -p {remote_dir}", 30)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to create remote directory {remote_dir}: {e}")
            return False

    def attach_to_session_interactive(self, session_name: str) -> None:
        """Attach to a Zellij session interactively via SSH."""
        try:
            attach_cmd = ["ssh", "-t", self.remote_name, f"zellij attach {session_name}"]
            logger.info(f"Attaching to Zellij session '{session_name}' on {self.remote_name}")
            subprocess.run(attach_cmd)
        except Exception as e:
            logger.error(f"Failed to attach to session: {e}")
            raise
