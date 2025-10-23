import subprocess
import typer
from typing import Annotated


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    import re
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)


def choose_zellij_session():
    cmd = "zellij list-sessions"
    sessions: list[str] = subprocess.check_output(cmd, shell=True).decode().strip().split("\n")
    sessions.sort(key=lambda s: "EXITED" in s)
    if "current" in sessions:
        print("Already in a Zellij session, avoiding nesting and exiting.")
        raise typer.Exit()
    if len(sessions) == 0:
        print("No Zellij sessions found, creating a new one.")
        result = """zellij --layout st2"""
    elif len(sessions) == 1:
        session = sessions[0].split(" [Created")[0]
        print(f"Only one Zellij session found: {session}, attaching to it.")
        result = f"zellij attach {session}"
    else:
        from machineconfig.utils.options import choose_from_options
        session = choose_from_options(msg="Choose a Zellij session to attach to:", multi=False, options=sessions, fzf=True)
        session = session.split(" [Created")[0]
        result = f"zellij attach {session}"
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(result, strict=True)


def new_zellij_session(kill_all: Annotated[bool, typer.Option("--kill-all", "-k", help="Kill all existing Zellij sessions before creating a new one.", show_default=True)] = False):
    cmd = """
zellij --layout st2
"""
    if kill_all:
        cmd = f"""zellij kill-sessions
{cmd}"""
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(cmd, strict=True)


def get_session_tabs() -> list[tuple[str, str]]:
    cmd = "zellij list-sessions"
    sessions: list[str] = subprocess.check_output(cmd, shell=True).decode().strip().split("\n")
    sessions = [strip_ansi_codes(s) for s in sessions]
    active_sessions = [s for s in sessions if "EXITED" not in s]
    result: list[tuple[str, str]] = []
    for session_line in active_sessions:
        session_name = session_line.split(" [Created")[0].strip()
        # Query tab names for the session
        tab_cmd = f"zellij  --session {session_name} action query-tab-names"
        try:
            tabs: list[str] = subprocess.check_output(tab_cmd, shell=True).decode().strip().split("\n")
            for tab in tabs:
                if tab.strip():
                    result.append((session_name, tab.strip()))
        except subprocess.CalledProcessError:
            # Skip if query fails
            continue
    print(result)
    return result


def main():
    app = typer.Typer(help="🖥️ Terminal utilities", no_args_is_help=True, add_help_option=False)
    app.command(name="choose-zellij-session", no_args_is_help=False, help="[c] Choose a Zellij session to attach to")(choose_zellij_session)
    app.command(name="c", hidden=True, no_args_is_help=False, help="[c] Choose a Zellij session to attach to")(choose_zellij_session)
    app.command(name="new-zellij-session", no_args_is_help=False, help="[n] new zellij session.")(new_zellij_session)
    app.command(name="n", hidden=True, no_args_is_help=False, help="[n] new zellij session.")(new_zellij_session)

    app.command(name="get-session-tabs", no_args_is_help=False, help="Get all Zellij session tabs.")(get_session_tabs)
    app.command(name="gst", hidden=True, no_args_is_help=False, help="Get all Zellij session tabs.")(get_session_tabs)
    app()


if __name__ == "__main__":
    main()
