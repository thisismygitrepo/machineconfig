"""devops with emojis"""

import typer
from typing import Optional, Annotated

import machineconfig.scripts.python.helpers_devops.cli_repos as cli_repos
import machineconfig.scripts.python.helpers_devops.cli_config as cli_config
import machineconfig.scripts.python.helpers_devops.cli_self as cli_self
import machineconfig.scripts.python.helpers_devops.cli_data as cli_data
import machineconfig.scripts.python.helpers_devops.cli_nw as cli_network


def install(which: Annotated[Optional[str], typer.Argument(..., help="Comma-separated list of program names to install, or group name if --group flag is set.")] = None,
        group: Annotated[bool, typer.Option(..., "--group", "-g", help="Treat 'which' as a group name. A group is bundle of apps.")] = False,
        interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Interactive selection of programs to install.")] = False,
    ) -> None:
        """📦 Install packages"""
        import machineconfig.utils.installer_utils.installer_cli as installer_entry_point
        installer_entry_point.main_installer_cli(which=which, group=group, interactive=interactive)


def init(which: Annotated[str, typer.Argument(..., help="Comma-separated list of script names to run, [init,ia,wrap] to run all initialization scripts.")] = "init") -> None:
    import platform
    if platform.system() == "Linux":
        if which == "init":
            import machineconfig.settings as module
            from pathlib import Path
            init_path = Path(module.__file__).parent.joinpath("shells", "bash", "init.sh")
            script = init_path.read_text(encoding="utf-8")
        elif which == "ia":
            from machineconfig.setup_linux import INTERACTIVE as script_path
            script = script_path.read_text(encoding="utf-8")
        else:
            typer.echo("Unsupported shell script for Linux.")
            raise typer.Exit(code=1)

    elif platform.system() == "Darwin":
        if which == "init":
            import machineconfig.settings as module
            from pathlib import Path
            init_path = Path(module.__file__).parent.joinpath("shells", "zsh", "init.sh")
            script = init_path.read_text(encoding="utf-8")
        elif which == "ia":
            from machineconfig.setup_linux import INTERACTIVE as script_path
            script = script_path.read_text(encoding="utf-8")
        else:
            typer.echo("Unsupported shell script for macOS.")
            raise typer.Exit(code=1)

    elif platform.system() == "Windows":
        if which == "init":
            import machineconfig.settings as module
            from pathlib import Path
            init_path = Path(module.__file__).parent.joinpath("shells", "powershell", "init.ps1")
            script = init_path.read_text(encoding="utf-8")
        elif which == "ia":
            from machineconfig.setup_windows import INTERACTIVE as script_path
            script = script_path.read_text(encoding="utf-8")
        else:
            typer.echo("Unsupported shell script for Windows.")
            raise typer.Exit(code=1)
    else:
        # raise NotImplementedError("Unsupported platform")
        typer.echo("Unsupported platform for init scripts.")
        raise typer.Exit(code=1)
    print(script)


# def get_app():
#     app = typer.Typer(add_completion=False, no_args_is_help=True)
#     app.command(name="scripts", help="define all scripts", no_args_is_help=False)(define_scripts)
#     return app

# def main():
#     # return app
#     app = get_app()
#     app()

#     define_app = get_define_app()


def get_app():
    app = typer.Typer(help="🛠️ DevOps operations", no_args_is_help=True, add_help_option=False,
                      add_completion=False)
    app.command("install", no_args_is_help=True, help="🛠️ [i] Install essential packages")(install)
    app.command("i", no_args_is_help=True, help="Install essential packages", hidden=True)(install)
    app_repos = cli_repos.get_app()
    app.add_typer(app_repos, name="repos")
    app.add_typer(app_repos, name="r", hidden=True)
    app_config = cli_config.get_app()
    app.add_typer(app_config, name="config")
    app.add_typer(app_config, name="c", hidden=True)
    app_data = cli_data.get_app()
    app.add_typer(app_data, name="data")
    app.add_typer(app_data, name="d", hidden=True)
    app_self = cli_self.get_app()
    app.add_typer(app_self, name="self")
    app.add_typer(app_self, name="s", hidden=True)
    app_nw = cli_network.get_app()
    app.add_typer(app_nw, name="network")
    app.add_typer(app_nw, name="n", hidden=True)

    app.command(name="init", help="🦐 [t] Define and manage configurations", no_args_is_help=False)(init)
    app.command(name="t", hidden=True)(init)

    return app


def main():
    app = get_app()
    app()
