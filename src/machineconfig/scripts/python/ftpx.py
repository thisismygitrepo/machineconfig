"""ftpx - File transfer utility through SSH."""

import typer
from typing import Annotated


def ftpx(
    source: Annotated[str, typer.Argument(help="Source path (machine:path)")],
    target: Annotated[str, typer.Argument(help="Target path (machine:path)")],
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Send recursively.")] = False,
    zipFirst: Annotated[bool, typer.Option("--zipFirst", "-z", help="Zip before sending.")] = False,
    cloud: Annotated[bool, typer.Option("--cloud", "-c", help="Transfer through the cloud.")] = False,
    overwrite_existing: Annotated[bool, typer.Option("--overwrite-existing", "-o", help="Overwrite existing files on remote when sending from local to remote.")] = False,
) -> None:
    """File transfer utility through SSH."""
    from machineconfig.scripts.python.helpers.helpers_network.ftpx_impl import ftpx as impl
    try:
        impl(source=source, target=target, recursive=recursive, zipFirst=zipFirst, cloud=cloud, overwrite_existing=overwrite_existing)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from e
    except RuntimeError as e:
        message = str(e).strip()
        if message.startswith("SSH Error: "):
            message = message.removeprefix("SSH Error: ").strip()
        if "source `" in message and " does not exist!" in message:
            raise typer.BadParameter(message, param_hint="source") from e
        typer.echo(f"Error: {message}", err=True)
        raise typer.Exit(code=1) from e


def main() -> None:
    """Entry point function that uses typer to parse arguments and call main."""
    app = typer.Typer()
    app.command(no_args_is_help=True, help=ftpx.__doc__, short_help="File transfer utility through SSH.")(ftpx)
    app()


if __name__ == "__main__":
    main()
