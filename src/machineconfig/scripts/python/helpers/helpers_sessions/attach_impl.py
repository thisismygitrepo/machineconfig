
import subprocess
from pathlib import Path
from machineconfig.settings.zellij import layouts

root = layouts.__path__[0]
STANDARD = Path(root).joinpath("st2.kdl")
# STANDARD = "st2.kdl"
# a = 1 + "sd"

def strip_ansi_codes(text: str) -> str:
    import re
    _ANSI_ESCAPE_RE = re.compile(
        r"(?:\x1B|\u001B|\033)\[[0-?]*[ -/]*[@-~]|\[[0-9;?]+[ -/]*[@-~]|\[m"
    )
    return _ANSI_ESCAPE_RE.sub("", text)


def choose_session(name: str | None, new_session: bool, kill_all: bool) -> tuple[str, str | None]:
    """Choose a Zellij session. Returns tuple of (action, script_to_run) where action is 'run_script', 'exit', or 'error'."""
    # from machineoncif

    if name is not None:
        return ("run_script", f"zellij attach {name}")
    if new_session:
        cmd = f"zellij --layout {STANDARD}"
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
        return ("run_script", f"zellij --layout {STANDARD}")
    if len(sessions) == 1:
        sn = strip_ansi_codes(sessions[0])
        session_name = sn.split(" [Created")[0]
        return ("run_script", f"zellij attach {session_name}")
    from machineconfig.utils.options import choose_from_options
    NEW_SESSION_LABEL = "NEW SESSION"
    KILL_ALL_AND_NEW_LABEL = "KILL ALL SESSIONS & START NEW"
    options = sessions + [NEW_SESSION_LABEL, KILL_ALL_AND_NEW_LABEL]
    try:
        session_name = choose_from_options(msg="Choose a Zellij session to attach to:", multi=False, options=options, tv=True)
    except Exception as e:
        return ("error", f"Error choosing Zellij session: {e}")
    if session_name == NEW_SESSION_LABEL:
        cmd = f"zellij --layout {STANDARD}"
        if kill_all:
            cmd = f"zellij kill-all-sessions --yes\n{cmd}"
        return ("run_script", cmd)
    if session_name == KILL_ALL_AND_NEW_LABEL:
        return ("run_script", f"zellij kill-all-sessions --yes\nzellij --layout {STANDARD}")
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


