
import typer
from typing import Optional, Literal, Annotated, TypeAlias

ON_CONFLICT_LOOSE: TypeAlias = Literal[
    "throw-error", "t",
    "overwrite-self-managed", "os",
    "backup-self-managed", "bs",
    "overwrite-default-path", "od",
    "backup-default-path", "bd"
    ]
ON_CONFLICT_STRICT: TypeAlias = Literal["throw-error", "overwrite-self-managed", "backup-self-managed", "overwrite-default-path", "backup-default-path"]
ON_CONFLICT_MAPPER: dict[str, ON_CONFLICT_STRICT] = {
    "t": "throw-error",
    "os": "overwrite-self-managed",
    "bs": "backup-self-managed",
    "od": "overwrite-default-path",
    "bd": "backup-default-path",
    "throw-error": "throw-error",
    "overwrite-self-managed": "overwrite-self-managed",
    "backup-self-managed": "backup-self-managed",
    "overwrite-default-path": "overwrite-default-path",
    "backup-default-path": "backup-default-path",
    }


def main_public_from_parser(method: Annotated[Literal["symlink", "s", "copy", "c"], typer.Option(..., "--method", "-m", help="Method to use for setting up the config file.")],
                            on_conflict: Annotated[ON_CONFLICT_LOOSE, typer.Option(..., "--on-conflict", "-o", help="Action to take on conflict")] = "throw-error",
                            which: Annotated[Optional[str], typer.Option(..., "--which", "-w", help="Specific items to process")] = "all",
                            interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Run in interactive mode")] = False):
    """Terminology:
    SOURCE = Self-Managed-Config-File-Path
    TARGET = Config-File-Default-Path
    For public config files, the source always exists, because we know it comes from machineconfig repo."""
    from machineconfig.profile.create_links import ConfigMapper, read_mapper
    mapper_full = read_mapper()["public"]
    if which is None:
        assert interactive is True
        from machineconfig.utils.options import choose_from_options
        items_chosen = choose_from_options(msg="Which symlink to create?", options=list(mapper_full.keys()), tv=True, multi=True)
    else:
        assert interactive is False
        if which == "all":
            items_chosen = list(mapper_full.keys())
        else:
            items_chosen = which.split(",")
    items_objections: dict[str, list[ConfigMapper]] = {item: mapper_full[item] for item in items_chosen if item in mapper_full}
    if len(items_objections) == 0:
        typer.echo("[red]Error:[/] No valid items selected.")
        typer.Exit(code=1)
        return
    from machineconfig.profile.create_links import apply_mapper
    from machineconfig.profile.create_helper import copy_assets_to_machine
    copy_assets_to_machine(which="settings")  # config files live here and will be linked to.
    method_map: dict[str, Literal["symlink", "copy"]] = {
        "s": "symlink",
        "symlink": "symlink",
        "c": "copy",
        "copy": "copy",
    }
    method = method_map[method]
    apply_mapper(mapper_data=items_objections, on_conflict=ON_CONFLICT_MAPPER[on_conflict], method=method)


def main_private_from_parser(method: Annotated[Literal["symlink", "s", "copy", "c"], typer.Option(..., "--method", "-m", help="Method to use for linking files")],
                             on_conflict: Annotated[ON_CONFLICT_LOOSE, typer.Option(..., "--on-conflict", "-o", help="Action to take on conflict")] = "throw-error",
                             which: Annotated[Optional[str], typer.Option(..., "--which", "-w", help="Specific items to process")] = "all",
                             interactive: Annotated[bool, typer.Option(..., "--interactive", "-i", help="Run in interactive mode")] = False):
    from machineconfig.profile.create_links import ConfigMapper, read_mapper
    mapper_full = read_mapper()["private"]
    if which is None:
        if interactive is False:
            typer.echo("[red]Error:[/] --which must be provided when not running in interactive mode.")
            typer.Exit(code=1)
            return
        from machineconfig.utils.options import choose_from_options
        items_chosen = choose_from_options(msg="Which symlink to create?", options=list(mapper_full.keys()), tv=True, multi=True)
    else:
        if interactive is True:
            typer.echo("[yellow]Warning:[/] --which is provided, but its not allowed to be used together with --interactive. Ignoring --interactive flag.")
            typer.Exit(code=0)
            return
        if which == "all":
            items_chosen = list(mapper_full.keys())
        else:
            items_chosen = which.split(",")
    items_objections: dict[str, list[ConfigMapper]] = {item: mapper_full[item] for item in items_chosen if item in mapper_full}
    if len(items_objections) == 0:
        typer.echo("[red]Error:[/] No valid items selected.")
        typer.Exit(code=1)
        return
    from machineconfig.profile.create_links import apply_mapper
    method_map: dict[str, Literal["symlink", "copy"]] = {
        "s": "symlink",
        "symlink": "symlink",
        "c": "copy",
        "copy": "copy",
    }
    method = method_map[method]
    apply_mapper(mapper_data=items_objections, on_conflict=ON_CONFLICT_MAPPER[on_conflict], method=method)
