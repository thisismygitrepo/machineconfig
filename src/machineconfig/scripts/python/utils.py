

from machineconfig.scripts.python.helpers_devops.cli_utils import download, merge_pdfs, get_machine_specs
import typer



def get_app() -> typer.Typer:
    app = typer.Typer(help="🛠️ utilities operations", no_args_is_help=True, add_help_option=False, add_completion=False)
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
