
from machineconfig.scripts.python.devops import get_app as get_devops_app
from machineconfig.scripts.python.cloud import get_app as get_cloud_app
from machineconfig.scripts.python.agents import get_app as get_agents_app
from machineconfig.scripts.python.sessions import get_app as get_sessions_app
from machineconfig.scripts.python.utils import get_app as get_utils_app

from machineconfig.scripts.python.ftpx import ftpx as ftpx_func
from machineconfig.scripts.python.croshell import croshell as croshell_func
from machineconfig.scripts.python.fire_jobs import fire as get_fire_jobs_app
from machineconfig.scripts.python.terminal import get_app as get_terminal_app

def get_app():
    import typer
    app = typer.Typer(help="MachineConfig CLI - Manage your machine configurations and workflows", no_args_is_help=True, add_help_option=False, add_completion=False)
    devops_app = get_devops_app()
    app.add_typer(devops_app, name="devops", help="[d] DevOps related commands", no_args_is_help=True)
    app.add_typer(devops_app, name="d", hidden=True)  # short alias

    cloud_app = get_cloud_app()
    app.add_typer(cloud_app, name="cloud", help="[c] Cloud management commands", no_args_is_help=True)
    app.add_typer(cloud_app, name="c", hidden=True)  # short alias

    sessions_app = get_sessions_app()
    app.add_typer(sessions_app, name="sessions", help="[s] Session and layout management", no_args_is_help=True)
    app.add_typer(sessions_app, name="s", hidden=True)  # short alias


    agents_app = get_agents_app()
    app.add_typer(agents_app, name="agents", help="[a] 🤖 AI Agents management commands", no_args_is_help=True)
    app.add_typer(agents_app, name="a", hidden=True)  # short alias

    app.command(name="fire", help="[f] Fire and manage jobs", no_args_is_help=False)(get_fire_jobs_app)
    app.command(name="f", hidden=True, no_args_is_help=False)(get_fire_jobs_app)
    app.command("ftpx", no_args_is_help=True, help="[ff] File transfer utility though SSH")(ftpx_func)
    app.command("ff", no_args_is_help=True, hidden=True)(ftpx_func)  # short alias
    app.command("croshell", no_args_is_help=False, help="[r] Cross-shell command execution")(croshell_func)
    app.command("r", no_args_is_help=False, hidden=True)(croshell_func)  # short alias

    utils_app = get_utils_app()
    app.add_typer(utils_app, name="utils", help="[u] Utility commands", no_args_is_help=True)
    app.add_typer(utils_app, name="u", hidden=True)  # short alias


    terminal_app = get_terminal_app()
    app.add_typer(terminal_app, name="terminal", help="[t] Terminal management commands", no_args_is_help=True)
    app.add_typer(terminal_app, name="t", hidden=True)  # short alias

    return app


def main():
    app = get_app()
    app()


if __name__ == "__main__":
    main()
