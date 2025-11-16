
import typer
from typing import Annotated, Optional


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    import re
    return re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)


def choose_zellij_session(
        name: Annotated[Optional[str], typer.Argument(help="Name of the Zellij session to attach to. If not provided, a list will be shown to choose from.")] = None,
        new_session: Annotated[bool, typer.Option("--new-session", "-n", help="Create a new Zellij session instead of attaching to an existing one.", show_default=True)] = False,
        kill_all: Annotated[bool, typer.Option("--kill-all", "-k", help="Kill all existing Zellij sessions before creating a new one.", show_default=True)] = False):
    if name is not None:
        result = f"zellij attach {name}"
        from machineconfig.utils.code import exit_then_run_shell_script
        exit_then_run_shell_script(result, strict=True)

    if new_session:
        cmd = """
    zellij --layout st2
    """
        if kill_all:
            cmd = f"""zellij kill-sessions
    {cmd}"""
        from machineconfig.utils.code import exit_then_run_shell_script
        exit_then_run_shell_script(script=cmd, strict=True)
        typer.Exit()
        return
    cmd = "zellij list-sessions"
    import subprocess
    sessions: list[str] = subprocess.check_output(cmd, shell=True).decode().strip().split("\n")
    # filter out empty lines and keep raw lines (they contain creation info)
    sessions = [s for s in sessions if s.strip()]
    sessions.sort(key=lambda s: "EXITED" in s)

    if "current" in sessions:
        print("Already in a Zellij session, avoiding nesting and exiting.")
        raise typer.Exit()
    if len(sessions) == 0:
        print("No Zellij sessions found, creating a new one.")
        result = """zellij --layout st2"""
    elif len(sessions) == 1:
        session_name = sessions[0].split(" [Created")[0]
        print(f"Only one Zellij session found: {session_name}, attaching to it.")
        result = f"zellij attach {session_name}"
    else:
        from machineconfig.utils.options import choose_from_options
        # Artificially inject a "NEW SESSION" option so the user can create one from the list
        NEW_SESSION_LABEL = "NEW SESSION"
        options = [NEW_SESSION_LABEL] + sessions
        session_name = choose_from_options(msg="Choose a Zellij session to attach to:", multi=False, options=options, tv=True)
        if session_name == NEW_SESSION_LABEL:
            cmd = "zellij --layout st2"
            if kill_all:
                cmd = f"zellij kill-sessions\n{cmd}"
            from machineconfig.utils.code import exit_then_run_shell_script
            exit_then_run_shell_script(cmd, strict=True)
            raise typer.Exit()
        session_name = session_name.split(" [Created")[0]
        result = f"zellij attach {session_name}"
    from machineconfig.utils.code import exit_then_run_shell_script
    exit_then_run_shell_script(result, strict=True)



def get_session_tabs() -> list[tuple[str, str]]:
    cmd = "zellij list-sessions"
    import subprocess
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


def start_wt(layout_name: Annotated[str, typer.Argument(help="Layout name to start.")]):
    from pathlib import Path
    layouts_file = Path.home().joinpath("dotfiles/machineconfig/layouts.json")
    if not layouts_file.exists():
        typer.echo(f"❌ Layouts file not found: {layouts_file}")
        # available
        raise typer.Exit(code=1)
    import json
    from machineconfig.utils.schemas.layouts.layout_types import LayoutsFile
    layouts_data: LayoutsFile = json.loads(layouts_file.read_text(encoding="utf-8"))
    chosen_layout = next((a_layout for a_layout in layouts_data["layouts"] if a_layout["layoutName"] == layout_name), None)
    if not chosen_layout:
        typer.echo(f"❌ Layout '{layout_name}' not found in layouts file.")
        available_layouts = [a_layout["layoutName"] for a_layout in layouts_data["layouts"]]
        typer.echo(f"Available layouts: {', '.join(available_layouts)}")
        raise typer.Exit(code=1)
    from machineconfig.cluster.sessions_managers.wt_local import run_wt_layout
    run_wt_layout(layout_config=chosen_layout)
    # cmd = f'powershell -ExecutionPolicy Bypass -File "./{layout_name}_layout.ps1"'
    # from machineconfig.utils.code import exit_then_run_shell_script
    # exit_then_run_shell_script(cmd, strict=True)


def get_app():
    app = typer.Typer(help="🖥️ Terminal utilities", no_args_is_help=True, add_help_option=False)
    app.command(name="attach-to-zellij", no_args_is_help=False, help="[z] Choose a Zellij session to attach to")(choose_zellij_session)
    app.command(name="z", hidden=True, no_args_is_help=False, help="[z] Choose a Zellij session to attach to")(choose_zellij_session)

    app.command(name="start-wt", no_args_is_help=True, help="[w] Start a Windows Terminal layout by name.")(start_wt)
    app.command(name="w", hidden=True, no_args_is_help=True, help="[w] Start a Windows Terminal layout by name.")(start_wt)

    app.command(name="get-session-tabs", no_args_is_help=False, help="[zt] Get all Zellij session tabs.")(get_session_tabs)
    app.command(name="zt", hidden=True, no_args_is_help=False, help="[zt] Get all Zellij session tabs.")(get_session_tabs)
    return app

def main():
    app = get_app()
    app()


if __name__ == "__main__":
    main()
