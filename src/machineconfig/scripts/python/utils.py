

from machineconfig.scripts.python.helpers_devops.cli_utils import download, merge_pdfs, get_machine_specs
import typer
from typing import Annotated


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
    

def get_app() -> typer.Typer:
    app = typer.Typer(help="🛠️ utilities operations", no_args_is_help=True, add_help_option=False, add_completion=False)
    app.command(name="kill-process", no_args_is_help=False, help="[k] Choose a process to kill")(kill_process)
    app.command(name="k", no_args_is_help=False, help="Choose a process to kill", hidden=True)(kill_process)
    app.command(name="download", no_args_is_help=True, help="[d] Download a file from a URL and optionally decompress it.")(download)
    app.command(name="d", no_args_is_help=True, hidden=True)(download)
    app.command(name="merge-pdfs", no_args_is_help=True, help="[m] Merge two PDF files into one.")(merge_pdfs)
    app.command(name="m", no_args_is_help=True, hidden=True)(merge_pdfs)
    app.command(name="get-machine-specs", no_args_is_help=False, help="[g] Get machine specifications.")(get_machine_specs)
    app.command(name="g", no_args_is_help=False, hidden=True)(get_machine_specs)
    return app



def main():
    app = get_app()
    app()
