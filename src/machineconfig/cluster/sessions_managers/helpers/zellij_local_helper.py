#!/usr/bin/env python3
import shlex
import subprocess
import random
import string
import psutil
import logging
from typing import List
from pathlib import Path

from machineconfig.cluster.sessions_managers.zellij_utils.monitoring_types import CommandStatus, ZellijSessionStatus
from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, TabConfig


logger = logging.getLogger(__name__)


def generate_random_suffix(length: int) -> str:
    """Generate a random string suffix for unique layout file names."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def parse_command(command: str) -> tuple[str, List[str]]:
    """Parse a command string into executable and arguments."""
    try:
        parts = shlex.split(command)
        if not parts:
            raise ValueError("Empty command provided")
        return parts[0], parts[1:] if len(parts) > 1 else []
    except ValueError as e:
        logger.error(f"Error parsing command '{command}': {e}")
        parts = command.split()
        return parts[0] if parts else "", parts[1:] if len(parts) > 1 else []


def format_args_for_kdl(args: List[str]) -> str:
    """Format command arguments for KDL layout format."""
    if not args:
        return ""
    formatted_args = []
    for arg in args:
        if " " in arg or '"' in arg or "'" in arg:
            escaped_arg = arg.replace('"', '\\"')
            formatted_args.append(f'"{escaped_arg}"')
        else:
            formatted_args.append(f'"{arg}"')
    return " ".join(formatted_args)


def create_tab_section(tab_config: TabConfig) -> str:
    """Create a KDL tab section from tab configuration."""
    tab_name = tab_config["tabName"]
    cwd = tab_config["startDir"]
    command = tab_config["command"]
    cmd, args = parse_command(command)
    args_str = format_args_for_kdl(args)
    tab_cwd = cwd or "~"
    escaped_tab_name = tab_name.replace('"', '\\"')
    tab_section = f'  tab name="{escaped_tab_name}" cwd="{tab_cwd}" {{\n'
    tab_section += f'    pane command="{cmd}" {{\n'
    if args_str:
        tab_section += f"      args {args_str}\n"
    tab_section += "    }\n  }\n"
    return tab_section


def validate_layout_config(layout_config: LayoutConfig) -> None:
    """Validate layout configuration."""
    if not layout_config["layoutTabs"]:
        raise ValueError("Layout must contain at least one tab")
    for tab in layout_config["layoutTabs"]:
        if not tab["tabName"].strip():
            raise ValueError(f"Invalid tab name: {tab['tabName']}")
        if not tab["command"].strip():
            raise ValueError(f"Invalid command for tab '{tab['tabName']}': {tab['command']}")
        if not tab["startDir"].strip():
            raise ValueError(f"Invalid startDir for tab '{tab['tabName']}': {tab['startDir']}")


def check_command_status(tab_name: str, layout_config: LayoutConfig) -> CommandStatus:
    """Check the running status of a command for a specific tab."""
    # Find the tab with the given name
    tab_config = None
    for tab in layout_config["layoutTabs"]:
        if tab["tabName"] == tab_name:
            tab_config = tab
            break

    if tab_config is None:
        return {"status": "unknown", "error": f"Tab '{tab_name}' not found in layout config", "running": False, "command": "", "cwd": "", "tab_name": tab_name, "processes": []}

    command = tab_config["command"]
    cwd = tab_config["startDir"]
    cmd, args = parse_command(command)
    try:
        shells = {"bash", "sh", "zsh", "fish"}
        matching_processes = []
        for proc in psutil.process_iter(["pid", "name", "cmdline", "status", "ppid", "create_time", "memory_info"]):
            try:
                info = proc.info
                proc_cmdline: list[str] | None = info.get("cmdline")  # type: ignore[assignment]
                if not proc_cmdline:
                    continue
                if info.get("status") in ["zombie", "dead", "stopped"]:
                    continue
                proc_name = info.get("name", "")
                is_match = False
                joined_cmdline = " ".join(proc_cmdline)
                # Primary matching heuristics - more precise matching
                if proc_name == cmd and cmd not in shells:
                    # For non-shell commands, match if args appear in cmdline
                    if not args or any(arg in joined_cmdline for arg in args):
                        is_match = True
                elif proc_name == cmd and cmd in shells:
                    # For shell commands, require more precise matching to avoid false positives
                    if args:
                        # Check if all args appear as separate cmdline arguments (not just substrings)
                        args_found = 0
                        for arg in args:
                            for cmdline_arg in proc_cmdline[1:]:  # Skip shell name
                                if arg == cmdline_arg or (len(arg) > 3 and arg in cmdline_arg):
                                    args_found += 1
                                    break
                        # Require at least as many args found as we're looking for
                        if args_found >= len(args):
                            is_match = True
                elif cmd in proc_cmdline[0] and cmd not in shells:
                    # Non-shell command in first argument
                    is_match = True

                # Additional shell wrapper filter - be more restrictive for shells
                if is_match and proc_name in shells and args:
                    # For shell processes, ensure the match is actually meaningful
                    # Don't match generic shell sessions just because they contain common paths
                    meaningful_match = False
                    for arg in args:
                        # Only consider it meaningful if the arg is substantial (not just a common path)
                        if len(arg) > 10 and any(arg == cmdline_arg for cmdline_arg in proc_cmdline[1:]):
                            meaningful_match = True
                            break
                        # Or if it's an exact script name match
                        elif arg.endswith(".py") or arg.endswith(".sh") or arg.endswith(".rb"):
                            if any(arg in cmdline_arg for cmdline_arg in proc_cmdline[1:]):
                                meaningful_match = True
                                break
                    if not meaningful_match:
                        is_match = False
                if not is_match:
                    continue
                try:
                    proc_obj = psutil.Process(info["pid"])  # type: ignore[index]
                    if proc_obj.status() not in ["running", "sleeping"]:
                        continue
                    mem_info = None
                    try:
                        mem = proc_obj.memory_info()
                        mem_info = mem.rss / (1024 * 1024)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    matching_processes.append(
                        {
                            "pid": info["pid"],  # type: ignore[index]
                            "name": proc_name,
                            "cmdline": proc_cmdline,
                            "status": info.get("status", "unknown"),
                            "cmdline_str": joined_cmdline,
                            "create_time": info.get("create_time", 0.0),
                            **({"memory_mb": float(mem_info)} if mem_info is not None else {}),
                        }
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Second-pass filtering: remove idle wrapper shells that have no meaningful (non-shell) descendants
        filtered_active = []
        for proc_info in matching_processes:
            try:
                proc_obj = psutil.Process(proc_info["pid"])  # type: ignore[index]
                if not proc_obj.is_running():
                    continue
                status_val = proc_obj.status()
                if status_val not in ["running", "sleeping"]:
                    continue
                proc_name = proc_info.get("name", "")
                if proc_name in shells:
                    descendants = proc_obj.children(recursive=True)
                    # Keep shell only if there exists a non-shell alive descendant OR descendant cmdline still includes our command token
                    meaningful = False
                    for child in descendants:
                        try:
                            if not child.is_running():
                                continue
                            child_name = child.name()
                            child_cmdline = " ".join(child.cmdline())
                            if child_name not in shells:
                                meaningful = True
                                break
                            if cmd in child_cmdline or any(arg in child_cmdline for arg in args):
                                meaningful = True
                                break
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    if not meaningful:
                        continue  # discard idle wrapper shell
                filtered_active.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        if filtered_active:
            # Heuristic: if the only remaining processes are wrapper shells invoking a script that already completed, mark as not running.
            # Case: layout launches 'bash <script.sh>' where script finishes and leaves an idle shell whose cmdline still shows the script path.
            try:
                if all(p.get("name") in shells for p in filtered_active):
                    script_paths = [arg for arg in args if arg.endswith(".sh")]
                    shell_only = True
                    stale_script_overall = False
                    for p in filtered_active:
                        proc_shell = psutil.Process(p["pid"])  # type: ignore[index]
                        create_time = getattr(proc_shell, "create_time", lambda: None)()
                        cmdline_joined = " ".join(p.get("cmdline", []))
                        stale_script = False
                        for spath in script_paths:
                            script_file = Path(spath)
                            if script_file.exists():
                                try:
                                    # If script mtime older than process start AND no non-shell descendants -> likely finished
                                    if create_time and script_file.stat().st_mtime < create_time:
                                        stale_script = True
                                except OSError:
                                    pass
                            if spath not in cmdline_joined:
                                stale_script = False
                        # If shell has any alive non-shell descendants, treat as running
                        descendants = proc_shell.children(recursive=True)
                        for d in descendants:
                            try:
                                if d.is_running() and d.name() not in shells:
                                    shell_only = False
                                    break
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                        if not shell_only:
                            break
                        if stale_script:
                            stale_script_overall = True
                    if shell_only and stale_script_overall:
                        return {"status": "not_running", "running": False, "processes": [], "command": command, "cwd": cwd, "tab_name": tab_name}
            except Exception:
                pass
            return {"status": "running", "running": True, "processes": filtered_active, "command": command, "cwd": cwd, "tab_name": tab_name}
        return {"status": "not_running", "running": False, "processes": [], "command": command, "cwd": cwd, "tab_name": tab_name}

    except Exception as e:
        logger.error(f"Error checking command status for tab '{tab_name}': {e}")
        return {"status": "error", "error": str(e), "running": False, "command": command, "cwd": cwd, "tab_name": tab_name, "processes": []}


def check_zellij_session_status(session_name: str) -> ZellijSessionStatus:
    """Check if a Zellij session is running."""
    try:
        # Run zellij list-sessions command
        result = subprocess.run(["zellij", "list-sessions"], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            sessions = result.stdout.strip().split("\n") if result.stdout.strip() else []
            session_running = any(session_name in session for session in sessions)

            return {"zellij_running": True, "session_exists": session_running, "session_name": session_name, "all_sessions": sessions}
        else:
            return {"zellij_running": False, "session_exists": False, "session_name": session_name, "all_sessions": [], "error": result.stderr}

    except subprocess.TimeoutExpired:
        return {"zellij_running": False, "session_exists": False, "session_name": session_name, "all_sessions": [], "error": "Timeout while checking Zellij sessions"}
    except FileNotFoundError:
        return {"zellij_running": False, "session_exists": False, "session_name": session_name, "all_sessions": [], "error": "Zellij not found in PATH"}
    except Exception as e:
        return {"zellij_running": False, "session_exists": False, "session_name": session_name, "all_sessions": [], "error": str(e)}


def get_layout_preview(layout_config: LayoutConfig, layout_template: str | None) -> str:
    """Generate a preview of the layout configuration."""
    if layout_template is None:
        layout_template = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""
    validate_layout_config(layout_config)
    layout_content = layout_template
    for tab in layout_config["layoutTabs"]:
        layout_content += "\n" + create_tab_section(tab)
    return layout_content + "\n}\n"
