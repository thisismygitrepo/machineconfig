

from machineconfig.scripts.python.helpers_devops.cli_utils import download, merge_pdfs, get_machine_specs, init_project, compress_pdf
import typer
from typing import Annotated, Optional
from pathlib import Path


def kill_process(
        # name: Annotated[Optional[str], typer.Option(..., "--name", "-n", help="Name of the process to kill")],
                #  command: Annotated[str, typer.Option(..., "--command", "-c", help="Match by command line instead of process name")] = "",
                 interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Interactively choose the process to kill")] = True):
    from machineconfig.utils.procs import main, ProcessManager
    if interactive:
        main()
        return
    _ = ProcessManager
    # pm = ProcessManager()
    # if command:
    #     pm.filter_and_kill(name=command
                        #    )


def add_dev_packages(repo_dir: Annotated[Optional[str], typer.Option(..., "--repo-dir", "-r", help="Path to the repository root directory")] = None):
    if repo_dir is None:
        r_dir = Path.cwd()
    else:
        r_dir = Path(repo_dir).resolve()
    if not r_dir.exists() or not r_dir.is_dir() or not (r_dir / "pyproject.toml").exists():
        typer.echo(f"❌ The provided repo directory `{r_dir}` is not valid or does not contain a `pyproject.toml` file.")
        raise typer.Exit(code=1)
    command = f"""
cd "{r_dir}" || exit 1
uv add nbformat ipdb ipykernel ipython pylint pyright mypy pyrefly ty pytest
"""
    from machineconfig.utils.code import run_shell_script
    typer.echo(f"➡️  Installing dev packages in repo at `{r_dir}`...")
    run_shell_script(command)
    typer.echo(f"✅ Dev packages installed successfully in repo at `{r_dir}`.")
    # TODO: see upgrade packages.


def wifi_select(
    ssid: Annotated[str, typer.Option("-n", "--ssid", help="🔗 SSID of WiFi (from config)")] = "MyPhoneHotSpot",
    manual: Annotated[bool, typer.Option("-m", "--manual", help="🔍 Manual network selection mode")] = False,
    list_: Annotated[bool, typer.Option("-l", "--list", help="📡 List available networks only")] = False,
) -> None:
    """Main function with fallback network selection"""
    from rich.panel import Panel
    from rich.prompt import Confirm
    from rich.console import Console
    from machineconfig.scripts.python.nw.wifi_conn import try_config_connection, manual_network_selection, display_available_networks
    console = Console()
    console.print(Panel("📶 Welcome to the WiFi Connector Tool", title="[bold blue]WiFi Connection[/bold blue]", border_style="blue"))

    # If user just wants to list networks
    if list_:
        display_available_networks()
        return

    # If user wants manual mode, skip config and go straight to selection
    if manual:
        console.print("[blue]🔍 Manual network selection mode[/blue]")
        if manual_network_selection():
            console.print("[green]🎉 Successfully connected![/green]")
        else:
            console.print("[red]❌ Failed to connect[/red]")
        return

    # Try to connect using configuration first
    console.print(f"[blue]🔍 Attempting to connect to configured network: {ssid}[/blue]")

    if try_config_connection(ssid):
        console.print("[green]🎉 Successfully connected using configuration![/green]")
        return

    # Configuration failed, offer fallback options
    console.print("\n[yellow]⚠️  Configuration connection failed or not available[/yellow]")

    if Confirm.ask("[blue]Would you like to manually select a network?[/blue]", default=True):
        if manual_network_selection():
            console.print("[green]🎉 Successfully connected![/green]")
        else:
            console.print("[red]❌ Failed to connect[/red]")
    else:
        console.print("[blue]👋 Goodbye![/blue]")


def get_app() -> typer.Typer:
    app = typer.Typer(help="🛠️ utilities operations", no_args_is_help=True, add_help_option=False, add_completion=False)
    app.command(name="kill-process", no_args_is_help=False, help="[k] Choose a process to kill")(kill_process)
    app.command(name="k", no_args_is_help=False, help="Choose a process to kill", hidden=True)(kill_process)
    app.command(name="download", no_args_is_help=True, help="[d] Download a file from a URL and optionally decompress it.")(download)
    app.command(name="d", no_args_is_help=True, hidden=True)(download)
    app.command(name="get-machine-specs", no_args_is_help=False, help="[g] Get machine specifications.")(get_machine_specs)
    app.command(name="g", no_args_is_help=False, hidden=True)(get_machine_specs)
    app.command(name="init-project", no_args_is_help=False, help="[i] Initialize a project with a uv virtual environment and install dev packages.")(init_project)
    app.command(name="i", no_args_is_help=False, hidden=True)(init_project)

    app.command(name="pdf-merge", no_args_is_help=True, help="[pm] Merge two PDF files into one.")(merge_pdfs)
    app.command(name="pm", no_args_is_help=True, hidden=True)(merge_pdfs)
    app.command(name="pdf-compress", no_args_is_help=True, help="[pc] Compress a PDF file.")(compress_pdf)
    app.command(name="pc", no_args_is_help=True, hidden=True)(compress_pdf)

    app.command(name="wifi-select", no_args_is_help=True, help="[w] WiFi connection utility.")(wifi_select)
    app.command(name="w", no_args_is_help=True, hidden=True)(wifi_select)
    return app

# def func():
#     import pycr

def main():
    app = get_app()
    app()
