
from git import Optional
import typer

cli_app = typer.Typer(help="🔄 SELF operations subcommands", no_args_is_help=True)


@cli_app.command()
def update():
    """🔄 UPDATE essential repos"""
    import machineconfig.scripts.python.devops_helpers.devops_update_repos as helper
    helper.main()
@cli_app.command()
def interactive():
    """🤖 INTERACTIVE configuration of machine."""
    from machineconfig.scripts.python.interactive import main
    main()

@cli_app.command()
def status():
    """📊 STATUS of machine, shell profile, apps, symlinks, dotfiles, etc."""
    import machineconfig.scripts.python.devops_helpers.devops_status as helper
    helper.main()
@cli_app.command()
def install():
    """📋 CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates."""
    from machineconfig.utils.code import run_shell_script
    from machineconfig.profile.create_shell_profile import create_default_shell_profile
    # from machineconfig.profile.create_links_export import main_public_from_parser
    create_default_shell_profile()
    # main_public_from_parser()
    import platform
    if platform.system() == "Windows":
        run_shell_script(r"""$HOME\.local\bin\uv.exe tool install machineconfig""")
    else:
        run_shell_script("""$HOME/.local/bin/uv tool install machineconfig""")

@cli_app.command(no_args_is_help=False)
def navigate():
    """📚 NAVIGATE command structure with TUI"""
    import machineconfig.scripts.python as navigator
    from pathlib import Path
    path = Path(navigator.__file__).resolve().parent.joinpath("devops_navigator.py")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(f"uv run --with machineconfig {path}")


@cli_app.command(no_args_is_help=True)
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
