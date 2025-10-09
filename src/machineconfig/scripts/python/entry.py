
from machineconfig.scripts.python.devops import get_app as get_devops_app
from machineconfig.scripts.python.cloud import app as cloud_app
from machineconfig.scripts.python.agents import get_app as get_agents_app
from machineconfig.scripts.python.fire_jobs import get_app as get_fire_jobs_app
from machineconfig.scripts.python.sessions import get_app as get_sessions_app

from machineconfig.scripts.python.ftpx import main as ftpx_func
from machineconfig.scripts.python.croshell import main as croshell_func


import typer


app = typer.Typer(help="MachineConfig CLI - Manage your machine configurations and workflows", no_args_is_help=True)
app.add_typer(get_devops_app(), name="devops", help="DevOps related commands")
app.add_typer(cloud_app, name="cloud", help="Cloud management commands")
app.add_typer(get_sessions_app(), name="sessions", help="Session and layout management")
app.add_typer(get_fire_jobs_app(), name="fire", help="Fire and manage jobs")
app.add_typer(get_agents_app(), name="agents", help="🤖 AI Agents management commands")

app.command("ftpx", no_args_is_help=True, help="File transfer utility though SSH")(ftpx_func)
app.command("croshell", no_args_is_help=False, help="Cross-shell command execution")(croshell_func)
