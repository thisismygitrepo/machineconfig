
from machineconfig.scripts.python.devops import app as devops_app
from machineconfig.scripts.python.cloud import app as cloud_app

from machineconfig.scripts.python.ftpx import main_from_parser as ftpx_app
from machineconfig.scripts.python.agents import main_from_parser as agents_app
from machineconfig.scripts.python.croshell import main as croshell_app
from machineconfig.scripts.python.fire_jobs import main_from_parser as fire_jobs_app
from machineconfig.scripts.python.sessions import main_from_parser as sessions_app

import typer


app = typer.Typer(help="MachineConfig CLI - Manage your machine configurations and workflows", no_args_is_help=True)
app.add_typer(devops_app, name="devops", help="DevOps related commands")
app.add_typer(cloud_app, name="cloud", help="Cloud management commands")

app.command("ftpx", no_args_is_help=True, help="File transfer utility though SSH")(ftpx_app)
app.command("agents", no_args_is_help=True, help="🤖 AI Agents management commands")(agents_app)
app.command("croshell", no_args_is_help=True, help="Cross-shell command execution")(croshell_app)
app.command("fire-jobs", no_args_is_help=True, help="Fire and manage jobs")(fire_jobs_app)
app.command("sessions", no_args_is_help=True, help="Session and layout management")(sessions_app)

