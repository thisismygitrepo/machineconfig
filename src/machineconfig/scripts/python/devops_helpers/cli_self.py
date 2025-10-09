
import typer
from typing import Optional


def update():
    """🔄 UPDATE essential repos"""
    import machineconfig.scripts.python.devops_helpers.devops_update_repos as helper
    helper.main()
def interactive():
    """🤖 INTERACTIVE configuration of machine."""
    from machineconfig.scripts.python.interactive import main
    main()

def status():
    """📊 STATUS of machine, shell profile, apps, symlinks, dotfiles, etc."""
    import machineconfig.scripts.python.devops_helpers.devops_status as helper
    helper.main()
def install():
    """📋 CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates."""
    from machineconfig.utils.code import run_shell_script
    from machineconfig.profile.create_shell_profile import create_default_shell_profile
    # from machineconfig.profile.create_links_export import main_public_from_parser
    create_default_shell_profile()
    # main_public_from_parser()
    import platform
    if platform.system() == "Windows":
        run_shell_script(r"""$HOME\.local\bin\uv.exe tool install machineconfig>=5.72""")
    else:
        run_shell_script("""$HOME/.local/bin/uv tool install machineconfig>=5.72""")

def navigate():
    """📚 NAVIGATE command structure with TUI"""
    import machineconfig.scripts.python as navigator
    from pathlib import Path
    path = Path(navigator.__file__).resolve().parent.joinpath("devops_navigator.py")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(f"""uv run --with "machineconfig>=5.72,textual" {path}""")


def run_python(ip: str = typer.Argument(..., help="Python command to run in the machineconfig environment"),
               command: Optional[bool] = typer.Option(False, "--command", "-c", help="Run as command")):
    """🐍 RUN python command/file in the machineconfig environment"""
    if command:
        exec(ip)
        return
    import machineconfig
    import subprocess
    import sys
    subprocess.run([sys.executable, ip], cwd=machineconfig.__path__[0])

def get_app():
    cli_app = typer.Typer(help="🔄 [s] self operations subcommands", no_args_is_help=True)
    cli_app.command("update", no_args_is_help=False, help="🔄  [u] UPDATE essential repos")(update)
    cli_app.command("u", no_args_is_help=False, help="UPDATE essential repos", hidden=True)(update)
    cli_app.command("interactive", no_args_is_help=False, help="🤖  [ia] INTERACTIVE configuration of machine.")(interactive)
    cli_app.command("ia", no_args_is_help=False, help="INTERACTIVE configuration of machine.", hidden=True)(interactive)
    cli_app.command("status", no_args_is_help=False, help="📊  [s] STATUS of machine, shell profile, apps, symlinks, dotfiles, etc.")(status)
    cli_app.command("s", no_args_is_help=False, help="STATUS of machine, shell profile, apps, symlinks, dotfiles, etc.", hidden=True)(status)
    cli_app.command("install", no_args_is_help=False, help="📋  [i] CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates.")(install)
    cli_app.command("i", no_args_is_help=False, help="CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates.", hidden=True)(install)
    cli_app.command("navigate", no_args_is_help=False, help="📚  [n] NAVIGATE command structure with TUI")(navigate)
    cli_app.command("n", no_args_is_help=False, help="NAVIGATE command structure with TUI", hidden=True)(navigate)
    cli_app.command("python", no_args_is_help=False, help="🐍 [c] python command/file in the machineconfig environment")(run_python)
    cli_app.command("c", no_args_is_help=False, help="RUN python command/file in the machineconfig environment", hidden=True)(run_python)
    return cli_app
