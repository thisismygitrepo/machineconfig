
# import logging
import subprocess
from pathlib import Path
# from typing import Optional, Dict

def copy_layout_to_remote(remote_machine: str, local_layout_path: str, remote_layout_path: str | None = None) -> str:
    local_path = Path(local_layout_path)
    if not local_path.exists():
        raise FileNotFoundError(f"Local layout file not found: {local_layout_path}")
    
    # Use same path on remote if not specified, but resolve relative to remote home
    if remote_layout_path is None:
        local_home = Path.home()
        local_abs_path = local_path.resolve()
        
        # Check if the local path is within the home directory
        try:
            relative_to_home = local_abs_path.relative_to(local_home)
            # Use the relative path from home, which will resolve to the remote user's home
            remote_layout_path = f"~/{relative_to_home}"
        except ValueError:
            # If path is not relative to home, just use the filename in remote home
            remote_layout_path = f"~/{local_path.name}"
    
    # Copy the layout file to remote machine
    scp_command = [
        "scp", 
        str(local_path), 
        f"{remote_machine}:{remote_layout_path}"
    ]
    
    print(f"📁 Copying layout file to {remote_machine}:{remote_layout_path}")
    result = subprocess.run(scp_command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to copy layout file: {result.stderr}")
    
    return remote_layout_path


def execute_zellij_layout(remote_machine: str, remote_layout_path: str, session_name: str = "JobManager"):
    # Execute zellij with the layout on remote machine
    ssh_command = [
        "ssh", remote_machine, "-n",
        f". ~/.profile; . ~/.bashrc; zellij --layout {remote_layout_path} a -b {session_name}"
    ]
    
    print(f"🚀 Executing zellij layout on {remote_machine}")
    result = subprocess.run(ssh_command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️  Warning: SSH command returned non-zero exit code: {result.stderr}")
    else:
        print(f"✅ Successfully launched zellij layout on {remote_machine}")
    
    return result


def send_and_execute_zellij_layout(remote_machine: str, local_layout_path: str, remote_layout_path: str | None = None, session_name: str = "JobManager"):
    remote_path = copy_layout_to_remote(remote_machine, local_layout_path, remote_layout_path)
    return execute_zellij_layout(remote_machine, remote_path, session_name)
