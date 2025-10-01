import typer
from machineconfig.profile.create import SymlinkMapper, read_mapper
from machineconfig.utils.options import choose_from_options
from machineconfig.utils.path_extended import PathExtended
from typing import Optional

from typing import Literal


def mail_public_from_parser(method: Literal["symlink", "copy"] = typer.Option(..., help="Method to use for linking files"), on_conflict: Literal["throwError", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option(..., help="Action to take on conflict"), which: Optional[str] = typer.Option(None, help="Specific items to process"), interactive: bool = typer.Option(False, help="Run in interactive mode")):
    """target always exists, because we know it comes from machineconfig repo."""
    if method == "symlink":
        machineconfig_repo_path = PathExtended.home().joinpath("code/machineconfig")
        if not machineconfig_repo_path.exists() or not machineconfig_repo_path.is_dir():
            raise FileNotFoundError(f"machineconfig repo not found at {machineconfig_repo_path}. Cannot create symlinks to non-existing source files.")

    mapper = read_mapper()["public"]
    if which is None:
        assert interactive is True
        items = choose_from_options(msg="Which symlink to create?", options=list(mapper.keys()), fzf=True, multi=True)
    else:
        assert interactive is False
        if which == "all":
            items = list(mapper.keys())
        else:
            items = which.split(",")
    items_objections: list[dict[str, SymlinkMapper]] = [mapper[item] for item in items if item in mapper]
    return items_objections


def mail_private_from_parser(method: Literal["symlink", "copy"] = typer.Option(..., help="Method to use for linking files"), on_conflict: Literal["throwError", "overwriteSelfManaged", "backupSelfManaged", "overwriteDefaultPath", "backupDefaultPath"] = typer.Option("throwError", help="Action to take on conflict"), which: Optional[str] = typer.Option(None, help="Specific items to process"), interactive: bool = typer.Option(False, help="Run in interactive mode")):
    # call them: selfManagedConfigFilePath --> configFileDefaultPath
    # the latter points to the former, or the latter is copied to the former.
    pass
