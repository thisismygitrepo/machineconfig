
"""Like yadm and dotter."""

from machineconfig.profile.create_links_export import ON_CONFLICT_LOOSE, ON_CONFLICT_MAPPER
from typing import Annotated, Literal
import typer



def main(
    file: Annotated[str, typer.Argument(help="file/folder path.")],
    method: Annotated[Literal["symlink", "s", "copy", "c"], typer.Option(..., "--method", "-m", help="Method to use for linking files")] = "copy",
    on_conflict: Annotated[ON_CONFLICT_LOOSE, typer.Option(..., "--on-conflict", "-o", help="Action to take on conflict")] = "throw-error",
    sensitivity: Annotated[Literal["private", "v", "public", "b"], typer.Option(..., "--sensitivity", "-s", help="Sensitivity of the config file.")] = "private",
    destination: Annotated[str, typer.Option("--destination", "-d", help="destination folder (override the default, use at your own risk)")] = "",
    shared: Annotated[bool, typer.Option("--shared", "-sh", help="Whether the config file is shared across destinations directory.")] = False,
    ) -> None:
    from rich.console import Console
    from rich.panel import Panel
    from machineconfig.utils.links import symlink_map, copy_map
    from pathlib import Path
    match sensitivity:
        case "private" | "v":
            backup_root = Path.home().joinpath("dotfiles/mapper")
        case "public" | "b":
            from machineconfig.utils.source_of_truth import CONFIG_ROOT
            backup_root = Path(CONFIG_ROOT).joinpath("dotfiles/mapper")

    console = Console()
    orig_path = Path(file).expanduser().absolute()
    if destination == "":
        if shared:
            new_path = backup_root.joinpath("shared").joinpath(orig_path.name)
            new_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            new_path = backup_root.joinpath(orig_path.relative_to(Path.home()))
            new_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if shared:
            dest_path = Path(destination).expanduser().absolute()
            dest_path.mkdir(parents=True, exist_ok=True)
            new_path = dest_path.joinpath("shared").joinpath(orig_path.name)
            new_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            dest_path = Path(destination).expanduser().absolute()
            dest_path.mkdir(parents=True, exist_ok=True)
            new_path = dest_path.joinpath(orig_path.name)
    match method:
        case "copy" | "c":
            try:
                copy_map(config_file_default_path=orig_path, self_managed_config_file_path=new_path, on_conflict=ON_CONFLICT_MAPPER[on_conflict])  # type: ignore[arg-type]
            except Exception as e:
                typer.echo(f"[red]Error:[/] {e}")
                typer.Exit(code=1)
                return
        case "symlink" | "s":
            try:
                symlink_map(config_file_default_path=orig_path, self_managed_config_file_path=new_path, on_conflict=ON_CONFLICT_MAPPER[on_conflict])  # type: ignore[arg-type]
            except Exception as e:
                typer.echo(f"[red]Error:[/] {e}")
                typer.Exit(code=1)
        case _:
            raise ValueError(f"Unknown method: {method}")
    console.print(Panel("\n".join(["✅ Symbolic link created successfully!", "🔄 Add the following snippet to mapper.toml to persist this mapping:",]), title="Symlink Created", border_style="green", padding=(1, 2),))

    # mapper_snippet = "\n".join(
    #     [
    #         f"[bold]📝 Edit configuration file:[/] [cyan]nano {Path(CONFIG_ROOT)}/symlinks/mapper.toml[/cyan]",
    #         "",
    #         f"[{new_path.parent.name}]",
    #         f"{orig_path.name.split('.')[0]} = {{ this = '{orig_path.as_posix()}', to_this = '{new_path.as_posix()}' }}",
    #     ]
    # )
    # console.print(
    #     Panel(
    #         mapper_snippet,
    #         title="Mapper Entry",
    #         border_style="cyan",
    #         padding=(1, 2),
    #     )
    # )


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
