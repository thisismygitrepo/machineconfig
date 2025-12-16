"""Utility commands - lazy loading subcommands."""

import typer
from typing import Annotated, Optional, Literal


def kill_process(interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Interactively choose the process to kill")] = True) -> None:
    """⚔️ Choose a process to kill."""
    from machineconfig.utils.procs import main, ProcessManager
    if interactive:
        main()
        return
    _ = ProcessManager


def upgrade_packages(root: Annotated[str, typer.Argument(help="Root directory of the project")] = ".") -> None:
    """⬆️ Upgrade project dependencies."""
    from machineconfig.utils.upgrade_packages import generate_uv_add_commands
    from pathlib import Path
    root_resolved = Path(root).expanduser().absolute().resolve()
    generate_uv_add_commands(pyproject_path=root_resolved / "pyproject.toml", output_path=root_resolved / "pyproject_init.sh")
def tui_env(which: Annotated[Literal["PATH", "p", "ENV", "e"], typer.Argument(help="Which environment variable to display.")] = "ENV") -> None:
    """📚 NAVIGATE ENV/PATH variable with TUI."""
    from machineconfig.scripts.python.helpers.helpers_utils.python import tui_env as impl
    impl(which=which)


def download(
    url: Annotated[Optional[str], typer.Argument(..., help="The URL to download the file from.")] = None,
    decompress: Annotated[bool, typer.Option(..., "--decompress", "-d", help="Decompress the file if it's an archive.")] = False,
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="The output file path.")] = None,
    output_dir: Annotated[Optional[str], typer.Option("--output-dir", help="Directory to place the downloaded file in.")] = None,
) -> None:
    """⬇️ Download a file from a URL and optionally decompress it."""
    from machineconfig.scripts.python.helpers.helpers_utils.download import download as impl
    impl(url=url, decompress=decompress, output=output, output_dir=output_dir)


def get_machine_specs(hardware: Annotated[bool, typer.Option(..., "--hardware", "-h", help="Show compute capability")] = False) -> None:
    """💻 Get machine specifications."""
    from machineconfig.scripts.python.helpers.helpers_utils.python import get_machine_specs as impl
    impl(hardware=hardware)


def type_hint(path: Annotated[str, typer.Argument(..., help="Path to file/project dir to type hint.")] = ".",
              dependency: Annotated[Literal["self-contained", "import"], typer.Option(..., "--dependency", "-d", help="Generated file is self contained or performs imports")] = "self-contained"
              ) -> None:
    from machineconfig.type_hinting.generators import generate_names_file
    from pathlib import Path
    path_resolved = Path(path).resolve()
    if not path_resolved.exists():
        typer.echo(f"Error: The provided path '{path}' does not exist.", err=True)
        raise typer.Exit(code=1)
    if path_resolved.is_file():
        modules = [path_resolved]
    else:
        if not (path_resolved / "pyproject.toml").exists():
            typer.echo("Error: Provided directory path is not a project root (missing pyproject.toml).", err=True)
            raise typer.Exit(code=1)
        else:
            modules = [file for file in path_resolved.rglob("dtypes.py") if ".venv" not in str(file)]
    for input_file in modules:
        print(f"Worked on: {input_file}")
        output_file = input_file.parent.joinpath(f"{input_file.stem}_names.py")
        generated_file = generate_names_file(input_file, output_file, search_paths=None, dependency=dependency)
        print(f"Generated: {generated_file}")


def init_project(
    name: Annotated[Optional[str], typer.Option("--name", "-n", help="Name of the project.")] = None,
    tmp_dir: Annotated[bool, typer.Option("--tmp-dir", "-t", help="Use a temporary directory for the project initialization.")] = False,
    python: Annotated[Literal["3.11", "3.12", "3.13", "3.14"], typer.Option("--python", "-p", help="Python sub version for the uv virtual environment.")] = "3.13",
    libraries: Annotated[Optional[str], typer.Option("--libraries", "-l", help="Additional packages to include in the uv virtual environment (space separated).")] = None,
    group: Annotated[Optional[str], typer.Option("--group", "-g", help="group of packages names (no separation) p:plot, t:types, l:linting, i:interactive, d:data")] = "p,t,l,i,d",
) -> None:
    """🚀 Initialize a project with a uv virtual environment and install dev packages."""
    from machineconfig.scripts.python.helpers.helpers_utils.python import init_project as impl
    impl(name=name, tmp_dir=tmp_dir, python=python, libraries=libraries, group=group)


def edit_file_with_hx(path: Annotated[Optional[str], typer.Argument(..., help="The root directory of the project to edit, or a file path.")] = None) -> None:
    """✏️ Open a file in the default editor."""
    from machineconfig.scripts.python.helpers.helpers_utils.python import edit_file_with_hx as impl
    impl(path=path)


def merge_pdfs(
    pdfs: Annotated[list[str], typer.Argument(..., help="Paths to the PDF files to merge.")],
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output merged PDF file path.")] = None,
    compress: Annotated[bool, typer.Option("--compress", "-c", help="Compress the output PDF.")] = False,
) -> None:
    """📄 Merge two PDF files into one."""
    from machineconfig.scripts.python.helpers.helpers_utils.pdf import merge_pdfs as impl
    impl(pdfs=pdfs, output=output, compress=compress)


def compress_pdf(
    pdf_input: Annotated[str, typer.Argument(..., help="Path to the input PDF file to compress.")],
    output: Annotated[Optional[str], typer.Option("--output", "-o", help="Output compressed PDF file path.")] = None,
    quality: Annotated[int, typer.Option("--quality", "-q", help="JPEG quality for image compression (0-100, 0=no change, 100=best).")] = 85,
    image_dpi: Annotated[int, typer.Option("--image-dpi", "-d", help="Target DPI for image resampling.")] = 0,
    compress_streams: Annotated[bool, typer.Option("--compress-streams", "-c", help="Compress uncompressed streams.")] = True,
    use_objstms: Annotated[bool, typer.Option("--object-streams", "-s", help="Use object streams for additional compression.")] = True,
) -> None:
    """📦 Compress a PDF file."""
    from machineconfig.scripts.python.helpers.helpers_utils.pdf import compress_pdf as impl
    impl(pdf_input=pdf_input, output=output, quality=quality, image_dpi=image_dpi, compress_streams=compress_streams, use_objstms=use_objstms)


def get_app() -> typer.Typer:
    app = typer.Typer(help="🛠️ utilities operations", no_args_is_help=True, add_help_option=True, add_completion=False)
    app.command(name="kill-process", no_args_is_help=False, help="⚔️ [k] Choose a process to kill")(kill_process)
    app.command(name="k", no_args_is_help=False, hidden=True)(kill_process)

    app.command("environment", no_args_is_help=False, help="📚 [v] NAVIGATE ENV/PATH variable with TUI")(tui_env)
    app.command("v", no_args_is_help=False, hidden=True)(tui_env)

    app.command(name="upgrade-packages", no_args_is_help=False, help="⬆️ [up] Upgrade project dependencies.")(upgrade_packages)
    app.command(name="up", no_args_is_help=False, hidden=True)(upgrade_packages)

    app.command(name="download", no_args_is_help=True, help="⬇️ [d] Download a file from a URL and optionally decompress it.")(download)
    app.command(name="d", no_args_is_help=True, hidden=True)(download)
    app.command(name="get-machine-specs", no_args_is_help=False, help="💻 [g] Get machine specifications.")(get_machine_specs)
    app.command(name="g", no_args_is_help=False, hidden=True)(get_machine_specs)
    app.command(name="init-project", no_args_is_help=False, help="🚀 [i] Initialize a project with a uv virtual environment and install dev packages.")(init_project)
    app.command(name="i", no_args_is_help=False, hidden=True)(init_project)
    app.command(name="edit", no_args_is_help=False, help="✏️ [e] Open a file in the default editor.")(edit_file_with_hx)
    app.command(name="e", no_args_is_help=False, hidden=True)(edit_file_with_hx)

    app.command(name="pdf-merge", no_args_is_help=True, help="📄 [pm] Merge two PDF files into one.")(merge_pdfs)
    app.command(name="pm", no_args_is_help=True, hidden=True)(merge_pdfs)
    app.command(name="pdf-compress", no_args_is_help=True, help="📦 [pc] Compress a PDF file.")(compress_pdf)
    app.command(name="pc", no_args_is_help=True, hidden=True)(compress_pdf)

    app.command(name="type-hint", no_args_is_help=True, help="📝 [t] Type hint a file or project directory.")(type_hint)
    app.command(name="t", no_args_is_help=True, hidden=True)(type_hint)

    return app


def main():
    app = get_app()
    app()
