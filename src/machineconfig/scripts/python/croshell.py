#!/usr/bin/env -S uv run --no-dev --project

"""croshell - Cross-shell command execution."""

from typing import Annotated, Optional
import typer
from machineconfig.scripts.python.enums import BACKENDS_LOOSE, BACKENDS_MAP


def croshell(
    path: Annotated[Optional[str], typer.Argument(help="path of file to read.")] = None,
    project_path: Annotated[Optional[str], typer.Option("--project", "-p", help="specify uv project to use")] = None,
    uv_with: Annotated[Optional[str], typer.Option("--uv-with", "-w", help="specify uv with packages to use")] = None,
    backend: Annotated[BACKENDS_LOOSE, typer.Option("--backend", "-b", help="specify the backend to use")] = "ipython",
    profile: Annotated[Optional[str], typer.Option("--profile", "-r", help="ipython profile to use, defaults to default profile.")] = None,
    machineconfig_project: Annotated[bool, typer.Option("--self", "-s", help="specify machineconfig project to use.")] = False,
) -> None:
    """Cross-shell command execution."""
    if machineconfig_project:
        from pathlib import Path
        if Path.home().joinpath("code/machineconfig").exists():
            project_path = str(Path.home().joinpath("code/machineconfig"))
        else:
            pass
    from machineconfig.scripts.python.helpers.helpers_croshell.croshell_impl import croshell as impl
    impl(path=path, project_path=project_path, uv_with=uv_with, backend=BACKENDS_MAP[backend], profile=profile)


def main() -> None:
    typer.run(croshell)


if __name__ == "__main__":
    main()
