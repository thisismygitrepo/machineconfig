#!/usr/bin/env python3
from pathlib import Path
import random
import string
import subprocess
import shlex
from typing import NotRequired, TypedDict

from machineconfig.utils.schemas.layouts.layout_types import LayoutConfig, TabConfig
from machineconfig.cluster.sessions_managers.zellij.zellij_utils.monitoring_types import CommandStatus


class TmuxSessionStatus(TypedDict):
    tmux_running: bool
    session_exists: bool
    session_name: str
    all_sessions: list[str]
    error: NotRequired[str]


def generate_random_suffix(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def normalize_cwd(cwd: str) -> str:
    normalized = cwd.replace("$HOME", str(Path.home()))
    return str(Path(normalized).expanduser())


def shell_quote(value: str) -> str:
    return shlex.quote(value)


def validate_layout_config(layout_config: LayoutConfig) -> None:
    if not layout_config["layoutTabs"]:
        raise ValueError("Layout must contain at least one tab")
    for tab in layout_config["layoutTabs"]:
        if not tab["tabName"].strip():
            raise ValueError(f"Invalid tab name: {tab['tabName']}")
        if not tab["command"].strip():
            raise ValueError(f"Invalid command for tab '{tab['tabName']}': {tab['command']}")
        if not tab["startDir"].strip():
            raise ValueError(f"Invalid startDir for tab '{tab['tabName']}': {tab['startDir']}")


def build_tmux_commands(layout_config: LayoutConfig, session_name: str) -> list[str]:
    validate_layout_config(layout_config)
    tabs = layout_config["layoutTabs"]
    first_tab = tabs[0]
    first_window = first_tab["tabName"]
    first_cwd = normalize_cwd(first_tab["startDir"])
    commands: list[str] = []
    commands.append(
        f"tmux new-session -d -s {shell_quote(session_name)} -n {shell_quote(first_window)} -c {shell_quote(first_cwd)}"
    )
    if first_tab["command"].strip():
        target = f"{session_name}:{first_window}"
        commands.append(
            f"tmux send-keys -t {shell_quote(target)} {shell_quote(first_tab['command'])} C-m"
        )
    for tab in tabs[1:]:
        window_name = tab["tabName"]
        cwd = normalize_cwd(tab["startDir"])
        commands.append(
            f"tmux new-window -t {shell_quote(session_name)} -n {shell_quote(window_name)} -c {shell_quote(cwd)}"
        )
        if tab["command"].strip():
            target = f"{session_name}:{window_name}"
            commands.append(
                f"tmux send-keys -t {shell_quote(target)} {shell_quote(tab['command'])} C-m"
            )
    commands.append(f"tmux select-window -t {shell_quote(session_name)}:0")
    return commands


def build_tmux_script(layout_config: LayoutConfig, session_name: str) -> str:
    script_lines = ["#!/usr/bin/env bash", "set -e"]
    script_lines.extend(build_tmux_commands(layout_config, session_name))
    return "\n".join(script_lines) + "\n"


def check_tmux_session_status(session_name: str) -> TmuxSessionStatus:
    try:
        result = subprocess.run(["tmux", "list-sessions", "-F", "#{session_name}"], capture_output=True, text=True, timeout=5)
    except FileNotFoundError as exc:
        return {
            "tmux_running": False,
            "session_exists": False,
            "session_name": session_name,
            "all_sessions": [],
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "tmux_running": False,
            "session_exists": False,
            "session_name": session_name,
            "all_sessions": [],
            "error": str(exc),
        }

    if result.returncode != 0:
        stderr = (result.stderr or "").strip().lower()
        if "no server running" in stderr:
            return {"tmux_running": False, "session_exists": False, "session_name": session_name, "all_sessions": []}
        return {
            "tmux_running": False,
            "session_exists": False,
            "session_name": session_name,
            "all_sessions": [],
            "error": (result.stderr or result.stdout or "Unknown error").strip(),
        }

    sessions = [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]
    return {
        "tmux_running": True,
        "session_exists": session_name in sessions,
        "session_name": session_name,
        "all_sessions": sessions,
    }


def build_unknown_command_status(tab_config: TabConfig) -> CommandStatus:
    return {
        "status": "unknown",
        "running": False,
        "processes": [],
        "command": tab_config["command"],
        "tab_name": tab_config["tabName"],
        "cwd": tab_config["startDir"],
    }
