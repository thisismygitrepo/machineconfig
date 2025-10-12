
import typer
from typing import Optional, Literal, Annotated


def main_public_from_parser(method: Annotated[Literal["symlink", "copy"], typer.Option(..., help="Method to use for setting up the config file.")],
                            on_conflict: Annotated[Literal["throwError", "overwriteDefaultPath", "backupDefaultPath"], typer.Option(..., help="Action to take on conflict")],
                            which: Annotated[Optional[str], typer.Option(..., help="Specific items to process")] = None,
                            interactive: Annotated[bool, typer.Option(..., help="Run in interactive mode")] = False):
    """Terminology:
    SOURCE = Self-Managed-Config-File-Path
    TARGET = Config-File-Default-Path
    For public config files, the source always exists, because we know it comes from machineconfig repo."""
    from machineconfig.profile.create_links import ConfigMapper, read_mapper
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

    from machineconfig.profile.create_links import apply_mapper
    from machineconfig.profile.create_helper import copy_assets_to_machine
    copy_assets_to_machine(which="settings")  # config files live here and will be linked to.
    apply_mapper(mapper_data=items_objections, on_conflict=on_conflict, method=method)


def main_private_from_parser(method: Annotated[Literal["symlink", "copy"], typer.Option(..., help="Method to use for linking files")],
                             on_conflict: Annotated[Literal["throwError", "overwriteSelfManaged", "backupSelfManaged", "overwriteDefaultPath", "backupDefaultPath"], typer.Option(..., help="Action to take on conflict")] = "throwError",
                             which: Annotated[Optional[str], typer.Option(..., help="Specific items to process")] = None,
                             interactive: Annotated[bool, typer.Option(..., help="Run in interactive mode")] = False):
    from machineconfig.profile.create_links import ConfigMapper, read_mapper

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

    from machineconfig.profile.create_links import apply_mapper
    apply_mapper(mapper_data=items_objections, on_conflict=on_conflict, method=method)
