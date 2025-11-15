"""devops with emojis"""

import typer
from typing import Optional, Annotated

import machineconfig.scripts.python.helpers_devops.cli_repos as cli_repos
import machineconfig.scripts.python.helpers_devops.cli_config as cli_config
import machineconfig.scripts.python.helpers_devops.cli_self as cli_self
import machineconfig.scripts.python.helpers_devops.cli_data as cli_data
import machineconfig.scripts.python.helpers_devops.cli_nw as cli_network
import machineconfig.scripts.python.helpers.run_py_script as run_py_script_module

def install(which: Annotated[Optional[str], typer.Argument(..., help="Comma-separated list of program names to install, or group name if --group flag is set.")] = None,
        group: Annotated[bool, typer.Option(..., "--group", "-g", help="Treat 'which' as a group name. A group is bundle of apps.")] = False,
        interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Interactive selection of programs to install.")] = False,
    ) -> None:
        """📦 Install packages"""
        import machineconfig.utils.installer_utils.installer_cli as installer_entry_point
        installer_entry_point.main_installer_cli(which=which, group=group, interactive=interactive)



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

    cli_app = typer.Typer(help="🛠️ DevOps operations", no_args_is_help=True, add_help_option=False, add_completion=False)
    cli_app.command("install", no_args_is_help=True, help="🛠️ [i] Install essential packages")(install)
    cli_app.command("i", no_args_is_help=True, help="Install essential packages", hidden=True)(install)

    app_repos = cli_repos.get_app()
    cli_app.add_typer(app_repos, name="repos")
    cli_app.add_typer(app_repos, name="r", hidden=True)
    app_config = cli_config.get_app()
    cli_app.add_typer(app_config, name="config")
    cli_app.add_typer(app_config, name="c", hidden=True)
    app_data = cli_data.get_app()
    cli_app.add_typer(app_data, name="data")
    cli_app.add_typer(app_data, name="d", hidden=True)
    app_self = cli_self.get_app()
    cli_app.add_typer(app_self, name="self")
    cli_app.add_typer(app_self, name="s", hidden=True)
    app_nw = cli_network.get_app()
    cli_app.add_typer(app_nw, name="network")
    cli_app.add_typer(app_nw, name="n", hidden=True)

    cli_app.command("python", no_args_is_help=True, help="🐍 [p] python scripts or command/file in the machineconfig environment", context_settings={"show_help_on_error": True})(run_py_script_module.run_py_script)
    cli_app.command("p", no_args_is_help=True, help="RUN python scripts or command/file in the machineconfig environment", hidden=True)(run_py_script_module.run_py_script)

    return cli_app


def main():
    app = get_app()
    app()
