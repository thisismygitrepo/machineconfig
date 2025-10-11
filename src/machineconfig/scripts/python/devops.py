"""devops with emojis"""

import typer
from typing import Optional

import machineconfig.scripts.python.devops_helpers.cli_repos as cli_repos
import machineconfig.scripts.python.devops_helpers.cli_config as cli_config
import machineconfig.scripts.python.devops_helpers.cli_self as cli_self
import machineconfig.scripts.python.devops_helpers.cli_data as cli_data
import machineconfig.scripts.python.devops_helpers.cli_nw as cli_network


def get_app():
    app = typer.Typer(help="🛠️ DevOps operations", no_args_is_help=True, add_completion=True)
    def install(which: Optional[str] = typer.Argument(None, help="Comma-separated list of program names to install, or group name if --group flag is set."),
        group: bool = typer.Option(False, "--group", "-g", help="Treat 'which' as a group name. A group is bundle of apps."),
        interactive: bool = typer.Option(False, "--interactive", "-ia", help="Interactive selection of programs to install."),
    ) -> None:
        """📦 Install essential packages"""
        import machineconfig.utils.installer_utils.installer as installer_entry_point
        installer_entry_point.main(which=which, group=group, interactive=interactive)
    _ = install
    app.command("install", no_args_is_help=True, help="🛠️ [i] Install essential packages")(install)
    app.command("i", no_args_is_help=True, help="Install essential packages", hidden=True)(install)
    app_repos = cli_repos.get_app()
    app.add_typer(app_repos, name="repos")
    app.add_typer(app_repos, name="r", hidden=True)
    app_config = cli_config.get_app()
    app.add_typer(app_config, name="config")
    app.add_typer(app_config, name="c", hidden=True)
    app.add_typer(cli_data.app_data, name="data")
    app.add_typer(cli_data.app_data, name="d", hidden=True)
    app_self = cli_self.get_app()
    app.add_typer(app_self, name="self")
    app.add_typer(app_self, name="s", hidden=True)
    app_nw = cli_network.get_app()
    app.add_typer(app_nw, name="network")
    app.add_typer(app_nw, name="n", hidden=True)
    return app

def main():
    app = get_app()
    app()
