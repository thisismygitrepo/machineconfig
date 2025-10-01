
import typer
from typing import Optional, Literal
from pathlib import Path


def main_public_from_parser(method: Literal["symlink", "copy"] = typer.Option(..., help="Method to use for setting up the config file."),
                            on_conflict: Literal["throwError", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option(..., help="Action to take on conflict"),
                            which: Optional[str] = typer.Option(None, help="Specific items to process"),
                            interactive: bool = typer.Option(False, help="Run in interactive mode")):
    """Terminology:
    SOURCE = Self-Managed-Config-File-Path
    TARGET = Config-File-Default-Path
    For public config files, the source always exists, because we know it comes from machineconfig repo."""
    from machineconfig.profile.create import ConfigMapper, read_mapper
    if method == "symlink":
        machineconfig_repo_path = Path.home().joinpath("code/machineconfig")
        if not machineconfig_repo_path.exists() or not machineconfig_repo_path.is_dir():
            raise FileNotFoundError(f"machineconfig repo not found at {machineconfig_repo_path}. Cannot create symlinks to non-existing source files.")

    mapper_full = read_mapper()["public"]
    if which is None:
        assert interactive is True
        from machineconfig.utils.options import choose_from_options
        items_chosen = choose_from_options(msg="Which symlink to create?", options=list(mapper_full.keys()), fzf=True, multi=True)
    else:
        assert interactive is False
        if which == "all":
            items_chosen = list(mapper_full.keys())
        else:
            items_chosen = which.split(",")
    items_objections: dict[str, list[ConfigMapper]] = {item: mapper_full[item] for item in items_chosen if item in mapper_full}

    from machineconfig.profile.create import apply_mapper
    apply_mapper(mapper_data=items_objections, on_conflict=on_conflict, method=method)


def main_private_from_parser(method: Literal["symlink", "copy"] = typer.Option(..., help="Method to use for linking files"),
                             on_conflict: Literal["throwError", "overwriteSelfManaged", "backupSelfManaged", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option("throwError", help="Action to take on conflict"),
                             which: Optional[str] = typer.Option(None, help="Specific items to process"),
                             interactive: bool = typer.Option(False, help="Run in interactive mode")):
    from machineconfig.profile.create import ConfigMapper, read_mapper

    mapper_full = read_mapper()["private"]
    if which is None:
        assert interactive is True
        from machineconfig.utils.options import choose_from_options
        items_chosen = choose_from_options(msg="Which symlink to create?", options=list(mapper_full.keys()), fzf=True, multi=True)
    else:
        assert interactive is False
        if which == "all":
            items_chosen = list(mapper_full.keys())
        else:
            items_chosen = which.split(",")
    items_objections: dict[str, list[ConfigMapper]] = {item: mapper_full[item] for item in items_chosen if item in mapper_full}

    from machineconfig.profile.create import apply_mapper
    apply_mapper(mapper_data=items_objections, on_conflict=on_conflict, method=method)
