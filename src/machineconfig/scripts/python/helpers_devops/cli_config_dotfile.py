"""Like yadm and dotter."""

from typing import Annotated

import typer


# @app.command()
# def symlinks_new():
#     """🆕 SYMLINKS new. consider moving to the new config command, then may be merge it with the dotfile subcommand"""
#     import machineconfig.jobs.python.python_ve_symlink as helper
#     helper.main()


def main(
    file: Annotated[str, typer.Argument(help="file/folder path.")],
    overwrite: Annotated[bool, typer.Option("--overwrite", "-o", help="Overwrite.")] = False,
    dest: Annotated[str, typer.Option("--dest", "-d", help="destination folder")] = "",
) -> None:

    from rich.console import Console
    from rich.panel import Panel

    from machineconfig.utils.links import symlink_map
    from machineconfig.utils.path_extended import PathExtended
    from machineconfig.utils.source_of_truth import CONFIG_ROOT
    console = Console()
    orig_path = PathExtended(file).expanduser().absolute()
    if dest == "":
        if "Local" in str(orig_path):
            junction = orig_path.split(at="Local", sep=-1)[1]
        elif "Roaming" in str(orig_path):
            junction = orig_path.split(at="Roaming", sep=-1)[1]
        elif ".config" in str(orig_path):
            junction = orig_path.split(at=".config", sep=-1)[1]
        else:
            junction = orig_path.rel2home()
        new_path = PathExtended(CONFIG_ROOT).parent.parent.joinpath(junction)
    else:
        dest_path = PathExtended(dest).expanduser().absolute()
        dest_path.mkdir(parents=True, exist_ok=True)
        new_path = dest_path.joinpath(orig_path.name)

    symlink_map(config_file_default_path=orig_path, self_managed_config_file_path=new_path, on_conflict="throwError")

    console.print(
        Panel(
            "\n".join(
                [
                    "✅ Symbolic link created successfully!",
                    "🔄 Add the following snippet to mapper.toml to persist this mapping:",
                ]
            ),
            title="Symlink Created",
            border_style="green",
            padding=(1, 2),
        )
    )

    mapper_snippet = "\n".join(
        [
            f"[bold]📝 Edit configuration file:[/] [cyan]nano {PathExtended(CONFIG_ROOT)}/symlinks/mapper.toml[/cyan]",
            "",
            f"[{new_path.parent.name}]",
            f"{orig_path.name.split('.')[0]} = {{ this = '{orig_path.collapseuser().as_posix()}', to_this = '{new_path.collapseuser().as_posix()}' }}",
        ]
    )

    console.print(
        Panel(
            mapper_snippet,
            title="Mapper Entry",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def arg_parser() -> None:
    typer.run(main)


if __name__ == "__main__":
    arg_parser()
