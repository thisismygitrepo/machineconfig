"""devops with emojis"""

import typer
from typing import Optional

import machineconfig.scripts.python.devops_helpers.cli_repos as cli_repos
import machineconfig.scripts.python.devops_helpers.cli_config as cli_config
import machineconfig.scripts.python.devops_helpers.cli_self as cli_self
import machineconfig.scripts.python.devops_helpers.cli_data as cli_data
import machineconfig.scripts.python.devops_helpers.cli_nw as cli_network


app = typer.Typer(help="🛠️ DevOps operations", no_args_is_help=True, add_completion=True)
@app.command(no_args_is_help=True)
def install( which: Optional[str] = typer.Option(None, "--which", "-w", help="Comma-separated list of program names to install."),
    group: Optional[str] = typer.Option(None, "--group", "-g", help="Groups names. A group is bundle of apps. See available groups when running interactively."),
    interactive: bool = typer.Option(False, "--interactive", "-ia", help="Interactive selection of programs to install."),
) -> None:
    """📦 Install essential packages"""
    import machineconfig.utils.installer_utils.installer as installer_entry_point
    installer_entry_point.main(which=which, group=group, interactive=interactive)


app.add_typer(cli_repos.app, name="repos")
app.add_typer(cli_config.config_apps, name="config")
app.add_typer(cli_data.app_data, name="data")
app.add_typer(cli_self.cli_app, name="self")
app.add_typer(cli_network.nw_apps, name="network")




if __name__ == "__main__":
    app()
