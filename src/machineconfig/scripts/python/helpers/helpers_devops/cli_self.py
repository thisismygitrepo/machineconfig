
import typer
from typing import Annotated, Literal


def copy_both_assets():
    import machineconfig.profile.create_helper as create_helper
    create_helper.copy_assets_to_machine(which="scripts")
    create_helper.copy_assets_to_machine(which="settings")


def init(which: Annotated[Literal["init", "ia", "live", "wrap"], typer.Argument(..., help="Comma-separated list of script names to run all initialization scripts.")] = "init",
         run: Annotated[bool, typer.Option("--run/--no-run", "-r/-nr", help="Run the script after displaying it.")] = False,
                        ) -> None:
    import platform
    if platform.system() == "Linux" or platform.system() == "Darwin":
        match which:
            case "init":
                import machineconfig.settings as module
                from pathlib import Path
                if platform.system() == "Darwin":
                    init_path = Path(module.__file__).parent.joinpath("shells", "zsh", "init.sh")
                else: init_path = Path(module.__file__).parent.joinpath("shells", "bash", "init.sh")
                script = init_path.read_text(encoding="utf-8")
            case "ia":
                from machineconfig.setup_linux import INTERACTIVE as script_path
                script = script_path.read_text(encoding="utf-8")
            case "live":
                from machineconfig.setup_linux import LIVE as script_path
                script = script_path.read_text(encoding="utf-8")
            case _:
                typer.echo("Unsupported shell script for Linux.")
                raise typer.Exit(code=1)

    elif platform.system() == "Windows":
        match which:
            case "init":
                import machineconfig.settings as module
                from pathlib import Path
                init_path = Path(module.__file__).parent.joinpath("shells", "powershell", "init.ps1")
                script = init_path.read_text(encoding="utf-8")
            case "ia":
                from machineconfig.setup_windows import INTERACTIVE as script_path
                script = script_path.read_text(encoding="utf-8")
            case "live":
                from machineconfig.setup_windows import LIVE as script_path
                script = script_path.read_text(encoding="utf-8")
            case _:
                typer.echo("Unsupported shell script for Windows.")
                raise typer.Exit(code=1)
    else:
        # raise NotImplementedError("Unsupported platform")
        typer.echo("Unsupported platform for init scripts.")
        raise typer.Exit(code=1)
    if run:
        from machineconfig.utils.code import exit_then_run_shell_script
        exit_then_run_shell_script(script, strict=True)
    else:
        print(script)


def update(copy_assets: Annotated[bool, typer.Option("--assets-copy/--no-assets-copy", "-a/-na", help="Copy (overwrite) assets to the machine after the update")] = True,
           link_public_configs: Annotated[bool, typer.Option("--link-public-configs/--no-link-public-configs", "-b/-nb", help="Link public configs after update (overwrites your configs!)")] = False,
           ):
    """🔄 UPDATE uv and machineconfig"""
    from pathlib import Path
    if Path.home().joinpath("code", "machineconfig").exists():
        shell_script = """
uv self update
cd ~/code/machineconfig
git pull
uv tool install --no-cache --upgrade --editable $HOME/code/machineconfig
    """
    else:
        shell_script = """
uv self update
uv tool install --no-cache --upgrade machineconfig
    """
    import platform
    if platform.system() == "Windows":
        from machineconfig.utils.code import exit_then_run_shell_script, get_uv_command_executing_python_script
        from machineconfig.utils.meta import lambda_to_python_script
        python_script = lambda_to_python_script(lambda: copy_both_assets(),
                                                in_global=True, import_module=False)
        uv_command, _py_file = get_uv_command_executing_python_script(python_script=python_script, uv_with=["machineconfig"], uv_project_dir=None)
        exit_then_run_shell_script(shell_script + "\n" + uv_command, strict=True)
    else:
        from machineconfig.utils.code import run_shell_script
        run_shell_script(shell_script)
        if copy_assets:
            copy_both_assets()
        if link_public_configs:
            import machineconfig.profile.create_links_export as create_links_export
            create_links_export.main_public_from_parser(method="copy", on_conflict="overwrite-default-path", which="all", interactive=False)


def install(copy_assets: Annotated[bool, typer.Option("--copy-assets/--no-assets-copy", "-a/-na", help="Copy (overwrite) assets to the machine after the update")] = True,
            dev: Annotated[bool, typer.Option("--dev", "-d", help="Install from local development code instead of PyPI")] = False,
    
            ):
    """📋 CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates."""
    from machineconfig.utils.code import run_shell_script, get_uv_command, get_shell_script_running_lambda_function, exit_then_run_shell_script
    from pathlib import Path
    import platform
    _ = run_shell_script
    if dev and not Path.home().joinpath("code/machineconfig").exists():
        # clone: https://github.com/thisismygitrepo/machineconfig.git
        import git
        repo_parent = Path.home().joinpath("code")
        repo_parent.mkdir(parents=True, exist_ok=True)
        git.Repo.clone_from("https://github.com/thisismygitrepo/machineconfig.git", str(repo_parent.joinpath("machineconfig")))
    uv_command = get_uv_command(platform=platform.system())
    if copy_assets:
        def func():
            from machineconfig.profile.create_shell_profile import create_default_shell_profile
            create_default_shell_profile()   # involves copying assets too
        uv_command2, _script_path = get_shell_script_running_lambda_function(lambda: func(),
                                                          uv_with=["machineconfig"], uv_project_dir=None)
    else:
        uv_command2 = ""
    if Path.home().joinpath("code/machineconfig").exists():
        exit_then_run_shell_script(f"""
{uv_command} tool install --upgrade --editable "{str(Path.home().joinpath("code/machineconfig"))}"
{uv_command2}
""")
    else:
        exit_then_run_shell_script(rf"""
{uv_command} tool install --upgrade "machineconfig>=8.37"
{uv_command2}
""")



def interactive():
    """🤖 INTERACTIVE configuration of machine."""
    from machineconfig.scripts.python.helpers.helpers_devops.interactive import main
    main()

def status():
    """📊 STATUS of machine, shell profile, apps, symlinks, dotfiles, etc."""
    import machineconfig.scripts.python.helpers.helpers_devops.devops_status as helper
    helper.main()


def navigate():
    """📚 NAVIGATE command structure with TUI"""
    import machineconfig.scripts.python as navigator
    from pathlib import Path
    path = Path(navigator.__file__).resolve().parent.joinpath("devops_navigator.py")
    from machineconfig.utils.code import exit_then_run_shell_script
    if Path.home().joinpath("code/machineconfig").exists(): executable = f"""--project "{str(Path.home().joinpath("code/machineconfig"))}" --with textual"""
    else: executable = """--with "machineconfig>=8.37,textual" """
    exit_then_run_shell_script(f"""uv run {executable} {path}""")

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
    cli_app = typer.Typer(help="🔄 [s] self operations subcommands", no_args_is_help=True, add_help_option=True, add_completion=False)
    cli_app.command("update",      no_args_is_help=False, help="🔄 [u] UPDATE machineconfig")(update)
    cli_app.command("u",           no_args_is_help=False, hidden=True)(update)
    cli_app.command("interactive", no_args_is_help=False, help="🤖 [ia] INTERACTIVE configuration of machine.")(interactive)
    cli_app.command("ia",           no_args_is_help=False, help="INTERACTIVE configuration of machine.", hidden=True)(interactive)
    cli_app.command(name="init",         no_args_is_help=False, help="🦐 [t] Define and manage configurations")(init)
    cli_app.command(name="t",            no_args_is_help=False, hidden=True)(init)
    cli_app.command("status",      no_args_is_help=False, help="📊 [s] STATUS of machine, shell profile, apps, symlinks, dotfiles, etc.")(status)
    cli_app.command("s",           no_args_is_help=False, help="STATUS of machine, shell profile, apps, symlinks, dotfiles, etc.", hidden=True)(status)
    cli_app.command("install",     no_args_is_help=False, help="📋 [i] CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates.")(install)
    cli_app.command("i",           no_args_is_help=False, help="CLONE machienconfig locally and incorporate to shell profile for faster execution and nightly updates.", hidden=True)(install)
    cli_app.command("navigate", no_args_is_help=False, help="📚 [n] NAVIGATE command structure with TUI")(navigate)
    cli_app.command("n", no_args_is_help=False, help="NAVIGATE command structure with TUI", hidden=True)(navigate)

    cli_app.command("readme", no_args_is_help=False, help="📚 [r] render readme markdown in terminal.")(readme)
    cli_app.command("r", no_args_is_help=False, hidden=True)(readme)
    return cli_app

