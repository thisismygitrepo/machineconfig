"""Sx & Rx

TODO: add support for cases in which source or target has non 22 default port number and is defineda as user@host:port:path which makes 2 colons in the string.
Currently, the only way to work around this is to predifine the host in ~/.ssh/config and use the alias in the source or target which is inconvenient when dealing with newly setup machines.

"""

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
    from pathlib import Path
    if target == "wsl" or source == "wsl":
        from machineconfig.utils.ssh_utils.wsl import copy_when_inside_windows
        if target == "wsl":
            target_obj = Path(source).expanduser().absolute().relative_to(Path.home())
            source_obj = target_obj
        else:
            source_obj = Path(target).expanduser().absolute().relative_to(Path.home())
            target_obj = source_obj
        copy_when_inside_windows(source_obj, target_obj, overwrite_existing)
        return
    elif source == "win" or target == "win":
        if source == "win":
            source_obj = Path(target).expanduser().absolute().relative_to(Path.home())
            target_obj = source_obj
        else:
            target_obj = Path(source).expanduser().absolute().relative_to(Path.home())
            source_obj = target_obj
        from machineconfig.utils.ssh_utils.wsl import copy_when_inside_wsl
        copy_when_inside_wsl(source_obj, target_obj, overwrite_existing)
        return

    from rich.console import Console
    from rich.panel import Panel

    from machineconfig.utils.ssh import SSH
    from machineconfig.utils.path_extended import PathExtended
    from machineconfig.scripts.python.helpers_cloud.helpers2 import ES
    from machineconfig.utils.accessories import pprint


    console = Console()

    console.print(
        Panel(
            "\n".join(
                [
                    "🚀 FTP File Transfer",
                    "📋 Starting transfer process...",
                ]
            ),
            title="Transfer Initialisation",
            border_style="blue",
            padding=(1, 2),
        )
    )
    
    # Initialize variables
    resolved_source: str | None = None
    resolved_target: str | None = None
    machine: str = ""
    
    if ":" in source and (source[1] != ":" if len(source) > 1 else True):  # avoid the case of "C:/":
        source_is_remote = True

        # calculating source:
        source_parts = source.split(":")
        machine = source_parts[0]
        if len(source_parts) > 1 and source_parts[1] == ES:  # the source path is to be inferred from target.
            if target == ES:
                raise ValueError(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ❌ Configuration Error
┃    Cannot use expand symbol `{ES}` in both source and target
┃    This creates a cyclical inference dependency
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            else:
                target_path_obj = PathExtended(target).expanduser().absolute()
            resolved_source = target_path_obj.collapseuser().as_posix()
            resolved_target = target
        else:
            resolved_source = ":".join(source.split(":")[1:])
            if target == ES:
                resolved_target = None
            else:
                resolved_target = PathExtended(target).expanduser().absolute().as_posix()

    elif ":" in target and (target[1] != ":" if len(target) > 1 else True):  # avoid the case of "C:/":
        source_is_remote = False
        target_parts = target.split(":")
        machine = target_parts[0]
        if len(target_parts) > 1 and target_parts[1] == ES:
            if source == ES:
                raise ValueError(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ❌ Configuration Error
┃    Cannot use expand symbol `{ES}` in both source and target
┃    This creates a cyclical inference dependency
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            else:
                resolved_source = source
            resolved_target = None
        else:
            resolved_target = ":".join(target.split(":")[1:])
            if source == ES:
                resolved_source = None
            else:
                resolved_source = PathExtended(source).expanduser().absolute().as_posix()

    else:
        raise ValueError("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ❌ Path Error
┃    Either source or target must be a remote path
┃    Format should be: machine:path
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    pprint({"source": str(resolved_source), "target": str(resolved_target), "machine": machine}, "CLI Resolution")

    from paramiko.ssh_exception import AuthenticationException  # type: ignore

    try:
        ssh = SSH(host=rf"{machine}", username=None, hostname=None, ssh_key_path=None, password=None, port=22, enable_compression=True)
    except AuthenticationException:
        console.print(
            Panel(
                "\n".join(
                    [
                        "🔑 Authentication failed. Trying manual authentication...",
                        "⚠️  Ensure that the username is provided correctly; only password prompts are handled here.",
                    ]
                ),
                title="Authentication Required",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        import getpass

        pwd = getpass.getpass()
        ssh = SSH(host=rf"{machine}", username=None, hostname=None, ssh_key_path=None, password=pwd, port=22, enable_compression=True)

    if cloud:
        console.print(
            Panel.fit(
                "☁️  Cloud transfer mode — uploading from remote to cloud...",
                title="Cloud Upload",
                border_style="cyan",
            )
        )
        ssh.run_shell_cmd_on_remote(command=f"cloud_copy {resolved_source} :^", verbose_output=True, description="Uploading from remote to the cloud.", strict_stderr=False, strict_return_code=False)
        console.print(
            Panel.fit(
                "⬇️  Cloud transfer mode — downloading from cloud to local...",
                title="Cloud Download",
                border_style="cyan",
            )
        )
        ssh.run_shell_cmd_on_local(command=f"cloud_copy :^ {resolved_target}")
        received_file = PathExtended(resolved_target)  # type: ignore
    else:
        if source_is_remote:
            if resolved_source is None:
                typer.echo("""❌ Path Error: Source must be a remote path (machine:path)""")
                typer.Exit(code=1)
                return                
            target_display = resolved_target or "<auto>"
            console.print(
                Panel(
                    "\n".join(
                        [
                            "📥 Transfer Mode: Remote → Local",
                            f"Source: [cyan]{resolved_source}[/cyan]",
                            f"Target: [cyan]{target_display}[/cyan]",
                            f"Options: {'ZIP compression' if zipFirst else 'No compression'}, {'Recursive' if recursive else 'Non-recursive'}",
                        ]
                    ),
                    title="Transfer Details",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
            received_file = ssh.copy_to_here(source=resolved_source, target=resolved_target, compress_with_zip=zipFirst, recursive=recursive)
        else:
            assert resolved_source is not None, """
❌ Path Error: Target must be a remote path (machine:path)"""
            target_display = resolved_target or "<auto>"
            console.print(
                Panel(
                    "\n".join(
                        [
                            "📤 Transfer Mode: Local → Remote",
                            f"Source: [cyan]{resolved_source}[/cyan]",
                            f"Target: [cyan]{target_display}[/cyan]",
                            f"Options: {'ZIP compression' if zipFirst else 'No compression'}, {'Recursive' if recursive else 'Non-recursive'}",
                        ]
                    ),
                    title="Transfer Details",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
            received_file = ssh.copy_from_here(source_path=resolved_source, target_rel2home=resolved_target, compress_with_zip=zipFirst, recursive=recursive, overwrite_existing=overwrite_existing)

    if source_is_remote and isinstance(received_file, PathExtended):
        console.print(
            Panel(
                "\n".join(
                    [
                        "📁 File Received",
                        f"Parent: [cyan]{repr(received_file.parent)}[/cyan]",
                        f"File: [cyan]{repr(received_file)}[/cyan]",
                    ]
                ),
                title="Transfer Result",
                border_style="green",
                padding=(1, 2),
            )
        )
    console.print(
        Panel(
            "File transfer process finished successfully",
            title="✅ Transfer Complete",
            border_style="green",
            padding=(1, 2),
        )
    )


def main() -> None:
    """Entry point function that uses typer to parse arguments and call main."""
    app = typer.Typer()
    app.command(no_args_is_help=True, help="File transfer utility though SSH.")(ftpx)
    app()


if __name__ == "__main__":
    main()
