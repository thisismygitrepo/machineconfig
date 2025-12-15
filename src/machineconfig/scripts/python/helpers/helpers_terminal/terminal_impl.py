import re
import subprocess
from pathlib import Path


_ANSI_ESCAPE_RE = re.compile(
    r"(?:\x1B|\u001B|\033)\[[0-?]*[ -/]*[@-~]|\[[0-9;?]+[ -/]*[@-~]|\[m"
)


def strip_ansi_codes(text: str) -> str:
    return _ANSI_ESCAPE_RE.sub("", text)


def choose_zellij_session(name: str | None, new_session: bool, kill_all: bool) -> tuple[str, str | None]:
    """Choose a Zellij session. Returns tuple of (action, script_to_run) where action is 'run_script', 'exit', or 'error'."""
    if name is not None:
        return ("run_script", f"zellij attach {name}")
    if new_session:
        cmd = "zellij --layout st2"
        if kill_all:
            cmd = f"zellij kill-all-sessions --yes\n{cmd}"
        return ("run_script", cmd)
    cmd = "zellij list-sessions"
    try:
        sessions: list[str] = subprocess.check_output(cmd, shell=True).decode().strip().split("\n")
    except subprocess.CalledProcessError:
        sessions = []
    sessions = [s for s in sessions if s.strip()]
    # print(f"Found Zellij sessions: {sessions}")
    sessions.sort(key=lambda s: "EXITED" in s)
    if "current" in sessions:
        return ("error", "Already in a Zellij session, avoiding nesting and exiting.")
    if len(sessions) == 0:
        return ("run_script", "zellij --layout st2")
    if len(sessions) == 1:
        sn = strip_ansi_codes(sessions[0])
        session_name = sn.split(" [Created")[0]
        return ("run_script", f"zellij attach {session_name}")
    from machineconfig.utils.options import choose_from_options
    NEW_SESSION_LABEL = "NEW SESSION"
    KILL_ALL_AND_NEW_LABEL = "KILL ALL SESSIONS & START NEW"
    options = sessions + [NEW_SESSION_LABEL, KILL_ALL_AND_NEW_LABEL]
    session_name = choose_from_options(msg="Choose a Zellij session to attach to:", multi=False, options=options, tv=True)
    if session_name == NEW_SESSION_LABEL:
        cmd = "zellij --layout st2"
        if kill_all:
            cmd = f"zellij kill-all-sessions --yes\n{cmd}"
        return ("run_script", cmd)
    if session_name == KILL_ALL_AND_NEW_LABEL:
        return ("run_script", "zellij kill-all-sessions --yes\nzellij --layout st2")
    session_name_clean = strip_ansi_codes(session_name)
    session_name_clean = session_name_clean.split(" [Created")[0]
    return ("run_script", f"zellij attach {session_name_clean}")


def get_session_tabs() -> list[tuple[str, str]]:
    cmd = "zellij list-sessions"
    try:
        sessions: list[str] = subprocess.check_output(cmd, shell=True).decode().strip().split("\n")
    except subprocess.CalledProcessError:
        sessions = []
    sessions = [strip_ansi_codes(s) for s in sessions]
    active_sessions = [s for s in sessions if "EXITED" not in s]
    result: list[tuple[str, str]] = []
    for session_line in active_sessions:
        session_name = session_line.split(" [Created")[0].strip()
        tab_cmd = f"zellij  --session {session_name} action query-tab-names"
        try:
            tabs: list[str] = subprocess.check_output(tab_cmd, shell=True).decode().strip().split("\n")
            for tab in tabs:
                if tab.strip():
                    result.append((session_name, tab.strip()))
        except subprocess.CalledProcessError:
            continue
    return result


def start_wt(layout_name: str) -> tuple[str, str | None]:
    """Start a Windows Terminal layout by name. Returns tuple of (status, message) where status is 'success' or 'error'."""
    import json
    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
    from machineconfig.cluster.sessions_managers.wt_local import run_wt_layout
    layouts_file = Path.home().joinpath("dotfiles/machineconfig/layouts.json")
    if not layouts_file.exists():
        return ("error", f"❌ Layouts file not found: {layouts_file}")
    layouts_data: LayoutsFile = json.loads(layouts_file.read_text(encoding="utf-8"))
    chosen_layout = next((a_layout for a_layout in layouts_data["layouts"] if a_layout["layoutName"] == layout_name), None)
    if not chosen_layout:
        available_layouts = [a_layout["layoutName"] for a_layout in layouts_data["layouts"]]
        return ("error", f"❌ Layout '{layout_name}' not found in layouts file.\nAvailable layouts: {', '.join(available_layouts)}")
    run_wt_layout(layout_config=chosen_layout)
    return ("success", None)
