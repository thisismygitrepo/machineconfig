"""devops with emojis - lazy loading subcommands."""

import typer
from typing import Optional, Annotated, Literal


def install(which: Annotated[Optional[str], typer.Argument(..., help="Comma-separated list of program names to install, or group name if --group flag is set.")] = None,
        group: Annotated[bool, typer.Option(..., "--group", "-g", help="Treat 'which' as a group name. A group is bundle of apps.")] = False,
        interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Interactive selection of programs to install.")] = False,
    ) -> None:
        """📦 Install packages"""
        import machineconfig.utils.installer_utils.installer_cli as installer_entry_point
        installer_entry_point.main_installer_cli(which=which, group=group, interactive=interactive)


def repos(ctx: typer.Context) -> None:
    """📁 [r] Manage development repositories"""
    import machineconfig.scripts.python.helpers.helpers_devops.cli_repos as cli_repos
    cli_repos.get_app()(ctx.args, standalone_mode=False)


def config(ctx: typer.Context) -> None:
    """⚙️ [c] Configuration management"""
    import machineconfig.scripts.python.helpers.helpers_devops.cli_config as cli_config
    cli_config.get_app()(ctx.args, standalone_mode=False)


def data(ctx: typer.Context) -> None:
    """💾 [d] Data management"""
    import machineconfig.scripts.python.helpers.helpers_devops.cli_data as cli_data
    cli_data.get_app()(ctx.args, standalone_mode=False)


def self_cmd(ctx: typer.Context) -> None:
    """🔧 [s] Self management"""
    import machineconfig.scripts.python.helpers.helpers_devops.cli_self as cli_self
    cli_self.get_app()(ctx.args, standalone_mode=False)


def network(ctx: typer.Context) -> None:
    """🌐 [n] Network management"""
    import machineconfig.scripts.python.helpers.helpers_devops.cli_nw as cli_network
    cli_network.get_app()(ctx.args, standalone_mode=False)


def execute(
    name: Annotated[str, typer.Argument(help="Name of script to run, e.g., 'a' for a.py, or command to execute")] = "",
    where: Annotated[Literal["all", "a", "private", "p", "public", "b", "library", "l", "dynamic", "d", "custom", "c"], typer.Option("--where", "-w", help="Where to look for the script")] = "all",
    interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Interactive selection of scripts to run")] = False,
    command: Annotated[Optional[bool], typer.Option(..., "--command", "-c", help="Run as command")] = False,
    list_scripts: Annotated[bool, typer.Option(..., "--list", "-l", help="List available scripts in all locations")] = False,
) -> None:
    """▶️ Execute python/shell scripts from pre-defined directories or as command."""
    import machineconfig.scripts.python.helpers.helpers_devops.run_script as run_py_script_module
    run_py_script_module.run_py_script(name=name, where=where, interactive=interactive, command=command, list_scripts=list_scripts)


def get_app() -> typer.Typer:
    cli_app = typer.Typer(help="🛠️ DevOps operations", no_args_is_help=True, add_help_option=True, add_completion=False)
    ctx_settings: dict[str, object] = {"allow_extra_args": True, "allow_interspersed_args": True, "ignore_unknown_options": True, "help_option_names": []}

    cli_app.command("install", no_args_is_help=True, help=install.__doc__, short_help="🛠️ [i] Install essential packages")(install)
    cli_app.command("i", no_args_is_help=True, help=install.__doc__, hidden=True)(install)

    cli_app.command("repos", help="📁 [r] Manage development repositories", context_settings=ctx_settings)(repos)
    cli_app.command("r", hidden=True, context_settings=ctx_settings)(repos)
    cli_app.command("config", help="⚙️ [c] Configuration management", context_settings=ctx_settings)(config)
    cli_app.command("c", hidden=True, context_settings=ctx_settings)(config)
    cli_app.command("data", help="💾 [d] Data management", context_settings=ctx_settings)(data)
    cli_app.command("d", hidden=True, context_settings=ctx_settings)(data)
    cli_app.command("self", help="🔧 [s] Self management", context_settings=ctx_settings)(self_cmd)
    cli_app.command("s", hidden=True, context_settings=ctx_settings)(self_cmd)
    cli_app.command("network", help="🌐 [n] Network management", context_settings=ctx_settings)(network)
    cli_app.command("n", hidden=True, context_settings=ctx_settings)(network)

    cli_app.command("execute", no_args_is_help=True, short_help="▶️ [e] Execute python/shell scripts from pre-defined directories or as command")(execute)
    cli_app.command("e", no_args_is_help=True, hidden=True)(execute)

    return cli_app


def main():
    app = get_app()
    app()
