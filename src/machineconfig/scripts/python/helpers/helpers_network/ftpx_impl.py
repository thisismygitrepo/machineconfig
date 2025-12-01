"""Pure Python implementation for ftpx command - no typer dependencies."""

from pathlib import Path
from typing import Optional


def ftpx(source: str, target: str, recursive: bool, zipFirst: bool, cloud: bool, overwrite_existing: bool) -> None:
    """File transfer utility through SSH."""
    if target == "wsl" or source == "wsl":
        _handle_wsl_transfer(source=source, target=target, overwrite_existing=overwrite_existing, )
        return
    elif source == "win" or target == "win":
        _handle_win_transfer(source=source, target=target, overwrite_existing=overwrite_existing, windows_username=None)
        return

    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    console.print(
        Panel(
            "\n".join([
                "🚀 FTP File Transfer",
                "📋 Starting transfer process...",
            ]),
            title="Transfer Initialisation",
            border_style="blue",
            padding=(1, 2),
        )
    )

    resolved_source, resolved_target, machine, source_is_remote = _resolve_paths(source=source, target=target)

    from machineconfig.utils.accessories import pprint
    pprint({"source": str(resolved_source), "target": str(resolved_target), "machine": machine}, "CLI Resolution")

    ssh = _create_ssh_connection(machine=machine, console=console)

    if cloud:
        received_file = _handle_cloud_transfer(ssh=ssh, resolved_source=resolved_source, resolved_target=resolved_target, console=console)
    else:
        received_file = _handle_direct_transfer(
            ssh=ssh, resolved_source=resolved_source, resolved_target=resolved_target,
            source_is_remote=source_is_remote, zipFirst=zipFirst, recursive=recursive,
            overwrite_existing=overwrite_existing, console=console
        )

    if source_is_remote and received_file is not None:
        from machineconfig.utils.path_extended import PathExtended
        if isinstance(received_file, PathExtended):
            console.print(
                Panel(
                    "\n".join([
                        "📁 File Received",
                        f"Parent: [cyan]{repr(received_file.parent)}[/cyan]",
                        f"File: [cyan]{repr(received_file)}[/cyan]",
                    ]),
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


def _handle_wsl_transfer(source: str, target: str, overwrite_existing: bool) -> None:
    """Handle WSL transfer when inside Windows."""
    from machineconfig.utils.ssh_utils.wsl import copy_when_inside_windows
    if target == "wsl":
        target_obj = Path(source).expanduser().absolute().relative_to(Path.home())
        source_obj = target_obj
    else:
        source_obj = Path(target).expanduser().absolute().relative_to(Path.home())
        target_obj = source_obj
    copy_when_inside_windows(source_obj, target_obj, overwrite_existing)


def _handle_win_transfer(source: str, target: str, overwrite_existing: bool, windows_username: str | None) -> None:
    """Handle Windows transfer when inside WSL."""
    from machineconfig.utils.ssh_utils.wsl import copy_when_inside_wsl
    if source == "win":
        source_obj = Path(target).expanduser().absolute().relative_to(Path.home())
        target_obj = source_obj
    else:
        target_obj = Path(source).expanduser().absolute().relative_to(Path.home())
        source_obj = target_obj
    copy_when_inside_wsl(source_obj, target_obj, overwrite_existing, windows_username=windows_username)


def _resolve_paths(source: str, target: str) -> tuple[Optional[str], Optional[str], str, bool]:
    """Resolve source and target paths, determine machine and direction."""
    from machineconfig.utils.path_extended import PathExtended
    from machineconfig.scripts.python.helpers.helpers_cloud.helpers2 import ES

    resolved_source: Optional[str] = None
    resolved_target: Optional[str] = None
    machine: str = ""
    source_is_remote: bool = False

    if ":" in source and (source[1] != ":" if len(source) > 1 else True):
        source_is_remote = True
        source_parts = source.split(":")
        machine = source_parts[0]
        if len(source_parts) > 1 and source_parts[1] == ES:
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

    elif ":" in target and (target[1] != ":" if len(target) > 1 else True):
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

    return resolved_source, resolved_target, machine, source_is_remote


def _create_ssh_connection(machine: str, console: "Console") -> "SSH":  # type: ignore[name-defined]
    """Create SSH connection, handling authentication."""
    from machineconfig.utils.ssh import SSH
    from paramiko.ssh_exception import AuthenticationException  # type: ignore
    from rich.panel import Panel

    try:
        ssh = SSH(host=rf"{machine}", username=None, hostname=None, ssh_key_path=None, password=None, port=22, enable_compression=True)
    except AuthenticationException:
        console.print(
            Panel(
                "\n".join([
                    "🔑 Authentication failed. Trying manual authentication...",
                    "⚠️  Ensure that the username is provided correctly; only password prompts are handled here.",
                ]),
                title="Authentication Required",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        import getpass
        pwd = getpass.getpass()
        ssh = SSH(host=rf"{machine}", username=None, hostname=None, ssh_key_path=None, password=pwd, port=22, enable_compression=True)

    return ssh


def _handle_cloud_transfer(ssh: "SSH", resolved_source: Optional[str], resolved_target: Optional[str], console: "Console") -> Optional["PathExtended"]:  # type: ignore[name-defined]
    """Handle cloud transfer mode."""
    from machineconfig.utils.path_extended import PathExtended
    from rich.panel import Panel

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
    return PathExtended(resolved_target)  # type: ignore


def _handle_direct_transfer(ssh: "SSH", resolved_source: Optional[str], resolved_target: Optional[str], source_is_remote: bool, zipFirst: bool, recursive: bool, overwrite_existing: bool, console: "Console") -> Optional["PathExtended"]:  # type: ignore[name-defined]
    """Handle direct SSH transfer."""
    from rich.panel import Panel

    if source_is_remote:
        if resolved_source is None:
            print("❌ Path Error: Source must be a remote path (machine:path)")
            return None
        target_display = resolved_target or "<auto>"
        console.print(
            Panel(
                "\n".join([
                    "📥 Transfer Mode: Remote → Local",
                    f"Source: [cyan]{resolved_source}[/cyan]",
                    f"Target: [cyan]{target_display}[/cyan]",
                    f"Options: {'ZIP compression' if zipFirst else 'No compression'}, {'Recursive' if recursive else 'Non-recursive'}",
                ]),
                title="Transfer Details",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        received_file = ssh.copy_to_here(source=resolved_source, target=resolved_target, compress_with_zip=zipFirst, recursive=recursive)
    else:
        assert resolved_source is not None, "❌ Path Error: Target must be a remote path (machine:path)"
        target_display = resolved_target or "<auto>"
        console.print(
            Panel(
                "\n".join([
                    "📤 Transfer Mode: Local → Remote",
                    f"Source: [cyan]{resolved_source}[/cyan]",
                    f"Target: [cyan]{target_display}[/cyan]",
                    f"Options: {'ZIP compression' if zipFirst else 'No compression'}, {'Recursive' if recursive else 'Non-recursive'}",
                ]),
                title="Transfer Details",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        received_file = ssh.copy_from_here(source_path=resolved_source, target_rel2home=resolved_target, compress_with_zip=zipFirst, recursive=recursive, overwrite_existing=overwrite_existing)

    return received_file
