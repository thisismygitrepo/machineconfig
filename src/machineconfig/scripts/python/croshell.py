#!/usr/bin/env -S uv run --no-dev --project

"""croshell - Cross-shell command execution."""

from typing import Annotated, Optional
import typer


def croshell(
    path: Annotated[Optional[str], typer.Argument(help="path of file to read.")] = None,
    project_path: Annotated[Optional[str], typer.Option("--project", "-p", help="specify uv project to use")] = None,
    uv_with: Annotated[Optional[str], typer.Option("--uv-with", "-w", help="specify uv with packages to use")] = None,
    marimo: Annotated[bool, typer.Option("--marimo", "-m", help="open the notebook using marimo if available")] = False,
    jupyter: Annotated[bool, typer.Option("--jupyter", "-j", help="run in jupyter interactive console")] = False,
    vscode: Annotated[bool, typer.Option("--vscode", "-c", help="open the script in vscode")] = False,
    visidata: Annotated[bool, typer.Option("--visidata", "-v", help="open data file in visidata")] = False,
    python: Annotated[bool, typer.Option("--python", "-P", help="flag to use python over IPython.")] = False,
    profile: Annotated[Optional[str], typer.Option("--profile", "-r", help="ipython profile to use, defaults to default profile.")] = None,
) -> None:
    """Cross-shell command execution."""
    from machineconfig.scripts.python.helpers.helpers_croshell.croshell_impl import croshell as impl
    impl(path=path, project_path=project_path, uv_with=uv_with, marimo=marimo, jupyter=jupyter, vscode=vscode, visidata=visidata, python=python, profile=profile)


def main() -> None:
    typer.run(croshell)


if __name__ == "__main__":
    main()
