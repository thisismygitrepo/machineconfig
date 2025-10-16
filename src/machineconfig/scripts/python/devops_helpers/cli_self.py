
import typer
from typing import Optional, Annotated


def update(copy_assets: Annotated[bool, typer.Option(..., "--copy-assets", "-c", help="Copy assets to the machine after the update. Default is True.")] = False):
    """🔄 UPDATE uv and machineconfig"""
    # from machineconfig.utils.source_of_truth import LIBRARY_ROOT
    # repo_root = LIBRARY_ROOT.parent.parent
    from pathlib import Path
    if Path.home().joinpath("code", "machineconfig").exists():
        code = """
    uv self update
    cd ~/code/machineconfig
    git pull
    uv tool install --upgrade --editable $HOME/code/machineconfig
    """
    else:
        code = """
    uv self update
    uv tool install --upgrade machineconfig
    """
    import platform
    if platform.system() == "Windows":
        from machineconfig.utils.code import run_shell_script_after_exit
        run_shell_script_after_exit(code)
        from machineconfig.profile.create_helper import copy_assets_to_machine
        copy_assets_to_machine(which="scripts")
        copy_assets_to_machine(which="settings")
    else:
        from machineconfig.utils.code import run_shell_script
        run_shell_script(code)
        if copy_assets:
            import machineconfig.profile.create_helper as create_helper
            create_helper.copy_assets_to_machine(which="scripts")
            create_helper.copy_assets_to_machine(which="settings")


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
        run_shell_script(r"""$HOME\.local\bin\uv.exe tool install "machineconfig>=6.36" """)
    else:
        run_shell_script("""$HOME/.local/bin/uv tool install "machineconfig>=6.36" """)

def navigate():
    """📚 NAVIGATE command structure with TUI"""
    import machineconfig.scripts.python as navigator
    from pathlib import Path
    path = Path(navigator.__file__).resolve().parent.joinpath("devops_navigator.py")
    from machineconfig.utils.code import run_shell_script
    run_shell_script(f"""uv run --with "machineconfig>=6.36,textual" {path}""")


def run_python(ip: Annotated[str, typer.Argument(..., help="Python command to run in the machineconfig environment")],
               command: Annotated[Optional[bool], typer.Option(..., "--command", "-c", help="Run as command")] = False):
    """🐍 RUN python command/file in the machineconfig environment"""
    if command:
        exec(ip)
        return
    import machineconfig
    import subprocess
    import sys
    subprocess.run([sys.executable, ip], cwd=machineconfig.__path__[0])
def readme():
    from rich.console import Console
    from rich.markdown import Markdown
    import requests

    # URL of the raw README.md file
    url_readme = "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/refs/heads/main/README.md"

    # Fetch the content
    response = requests.get(url_readme)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse markdown
    md = Markdown(response.text)

    # Render in terminal
    console = Console()
    console.print(md)


def get_app():
    cli_app = typer.Typer(help="🔄 [s] self operations subcommands", no_args_is_help=True)
    cli_app.command("update", no_args_is_help=False, help="🔄  [u] UPDATE machineconfig")(update)
    cli_app.command("u", no_args_is_help=False, hidden=True)(update)
    cli_app.command("interactive", no_args_is_help=False, help="🤖  [i] INTERACTIVE configuration of machine.")(interactive)
    cli_app.command("i", no_args_is_help=False, help="INTERACTIVE configuration of machine.", hidden=True)(interactive)
    cli_app.command("status", no_args_is_help=False, help="📊  [s] STATUS of machine, shell profile, apps, symlinks, dotfiles, etc.")(status)
    cli_app.command("s", no_args_is_help=False, help="STATUS of machine, shell profile, apps, symlinks, dotfiles, etc.", hidden=True)(status)
    cli_app.command("install", no_args_is_help=False, help="📋  [I] CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates.")(install)
    cli_app.command("I", no_args_is_help=False, help="CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates.", hidden=True)(install)
    cli_app.command("navigate", no_args_is_help=False, help="📚  [n] NAVIGATE command structure with TUI")(navigate)
    cli_app.command("n", no_args_is_help=False, help="NAVIGATE command structure with TUI", hidden=True)(navigate)
    cli_app.command("python", no_args_is_help=False, help="🐍  [c] python command/file in the machineconfig environment", context_settings={"show_help_on_error": True})(run_python)
    cli_app.command("c", no_args_is_help=False, help="RUN python command/file in the machineconfig environment", hidden=True)(run_python)
    cli_app.command("readme", no_args_is_help=False, help="📚  [r] render readme markdown in terminal.")(readme)
    cli_app.command("r", no_args_is_help=False, hidden=True)(readme)
    return cli_app

