
import typer
from typing import Literal, Annotated, Optional, TypeAlias


ON_CONFLICT_LOOSE: TypeAlias = Literal[
    "throw-error", "t",
    "overwrite-self-managed", "os",
    "backup-self-managed", "bs",
    "overwrite-default-path", "od",
    "backup-default-path", "bd"
    ]
ON_CONFLICT_STRICT: TypeAlias = Literal["throw-error", "overwrite-self-managed", "backup-self-managed", "overwrite-default-path", "backup-default-path"]
ON_CONFLICT_MAPPER: dict[ON_CONFLICT_LOOSE, ON_CONFLICT_STRICT] = {
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

SENSITIVITY_LOOSE: TypeAlias = Literal["private", "p", "public", "b", "all", "a"]
SENSITIVITY_STRICT: TypeAlias = Literal["private", "public", "all"]
SENSITIVITY_MAP: dict[SENSITIVITY_LOOSE, SENSITIVITY_STRICT] = {
    "private": "private",
    "p": "private",
    "public": "public",
    "b": "public",
    "all": "all",
    "a": "all",
}

REPO_STRICT: TypeAlias = Literal["library", "user", "all"]
REPO_LOOSE: TypeAlias = Literal["library", "l", "user", "u", "all", "a"]
REPO_MAP: dict[REPO_LOOSE, REPO_STRICT] = {
    "library": "library",
    "l": "library",
    "user": "user",
    "u": "user",
    "a": "all",
    "all": "all",
}

METHOD_STRICT: TypeAlias = Literal["symlink", "copy"]
METHOD_LOOSE: TypeAlias = Literal["symlink", "s", "copy", "c"]
METHOD_MAP: dict[METHOD_LOOSE, METHOD_STRICT] = {
    "symlink": "symlink",
    "s": "symlink",
    "copy": "copy",
    "c": "copy",
}



def main_from_parser(
    sensitivity: Annotated[SENSITIVITY_LOOSE, typer.Option(..., "--sensitivity", "-s", help="Sensitivity of the configuration files to manage.")],
    method: Annotated[METHOD_LOOSE, typer.Option(..., "--method", "-m", help="Method to use for linking files")],
    repo: Annotated[REPO_LOOSE, typer.Option(..., "--repo", "-r", help="Mapper source to use for config files.")] = "library",
    on_conflict: Annotated[ON_CONFLICT_LOOSE, typer.Option(..., "--on-conflict", "-o", help="Action to take on conflict")] = "throw-error",
    which: Annotated[Optional[str], typer.Option(..., "--which", "-w", help="Specific items to process ('all' for all items) (default is None, selection is interactive)")] = None,
):
    """Terminology:
    SOURCE = Self-Managed-Config-File-Path
    TARGET = Config-File-Default-Path
    For public config files in the library repo, the source always exists."""
    from machineconfig.profile.create_links import ConfigMapper, read_mapper
    repo_key = REPO_MAP[repo]
    mapper_full_obj = read_mapper(repo=repo_key)
    match sensitivity:
        case "private" | "p":
            mapper_full = mapper_full_obj["private"]
        case "public" | "b":
            mapper_full = mapper_full_obj["public"]
        case "all" | "a":
            mapper_full = {**mapper_full_obj["private"], **mapper_full_obj["public"]}
            
    if which is None:
        from machineconfig.utils.options_utils.tv_options import choose_from_dict_with_preview
        import pprint
        options_with_preview: dict[str, str] = {key: pprint.pformat(value, width=88, sort_dicts=True) for key, value in mapper_full.items()}
        items_chosen = choose_from_dict_with_preview(options_with_preview, extension="toml", multi=True, preview_size_percent=75.0)
    else:
        if which == "all":
            items_chosen = list(mapper_full.keys())
        else:
            items_chosen = which.split(",")
    items_objections: dict[str, list[ConfigMapper]] = {item: mapper_full[item] for item in items_chosen if item in mapper_full}
    if len(items_objections) == 0:
        msg = typer.style("Error: ", fg=typer.colors.RED) + "No valid items selected."
        typer.echo(msg)
        typer.Exit(code=1)
        return

    if (sensitivity == "public" or sensitivity == "b") and repo_key == "library":
        from machineconfig.profile.create_helper import copy_assets_to_machine
        copy_assets_to_machine(which="settings")  # config files live here and will be linked to.

    method = METHOD_MAP[method]
    from machineconfig.profile.create_links import apply_mapper
    apply_mapper(mapper_data=items_objections, on_conflict=ON_CONFLICT_MAPPER[on_conflict], method=method)
