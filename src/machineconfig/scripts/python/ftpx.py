#!/usr/bin/env -S uv run --no-dev --project /home/alex/code/machineconfig --script
"""Sx & Rx

TODO: add support for cases in which source or target has non 22 default port number and is defineda as user@host:port:path which makes 2 colons in the string.
Currently, the only way to work around this is to predifine the host in ~/.ssh/config and use the alias in the source or target which is inconvenient when dealing with newly setup machines.

"""

import typer
from typing_extensions import Annotated
from machineconfig.utils.ssh import SSH
from machineconfig.utils.path_extended import PathExtended as PathExtended
from machineconfig.scripts.python.helpers.helpers2 import ES
from machineconfig.utils.accessories import pprint


def main(
    source: Annotated[str, typer.Argument(help="Source path (machine:path)")],
    target: Annotated[str, typer.Argument(help="Target path (machine:path)")],
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Send recursively.")] = False,
    zipFirst: Annotated[bool, typer.Option("--zipFirst", "-z", help="Zip before sending.")] = False,
    cloud: Annotated[bool, typer.Option("--cloud", "-c", help="Transfer through the cloud.")] = False,
) -> None:
    print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🚀 FTP File Transfer
┃ 📋 Starting transfer process...
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
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
        ssh = SSH(rf"{machine}")
    except AuthenticationException:
        print("""
┌────────────────────────────────────────────────────────────────
│ 🔑 Authentication Failed
│    Trying manual authentication...
│
│ ⚠️  Caution: Ensure that username is passed appropriately
│    This exception only handles password authentication
└────────────────────────────────────────────────────────────────""")
        import getpass

        pwd = getpass.getpass()
        ssh = SSH(rf"{machine}", pwd=pwd)

    if cloud:
        print("""
┌────────────────────────────────────────────────────────────────
│ ☁️  Cloud Transfer Mode
│    Uploading from remote to cloud...
└────────────────────────────────────────────────────────────────""")
        ssh.run(f"cloud_copy {resolved_source} :^", desc="Uploading from remote to the cloud.").print()
        print("""
┌────────────────────────────────────────────────────────────────
│ ⬇️  Cloud Transfer Mode
│    Downloading from cloud to local...
└────────────────────────────────────────────────────────────────""")
        ssh.run_locally(f"cloud_copy :^ {resolved_target}").print()
        received_file = PathExtended(resolved_target)  # type: ignore
    else:
        if source_is_remote:
            assert resolved_source is not None, """
❌ Path Error: Source must be a remote path (machine:path)"""
            print(f"""
┌────────────────────────────────────────────────────────────────
│ 📥 Transfer Mode: Remote → Local
│    Source: {resolved_source}
│    Target: {resolved_target}
│    Options: {"ZIP compression" if zipFirst else "No compression"}, {"Recursive" if recursive else "Non-recursive"}
└────────────────────────────────────────────────────────────────""")
            received_file = ssh.copy_to_here(source=resolved_source, target=resolved_target, z=zipFirst, r=recursive)
        else:
            assert resolved_source is not None, """
❌ Path Error: Target must be a remote path (machine:path)"""
            print(f"""
┌────────────────────────────────────────────────────────────────
│ 📤 Transfer Mode: Local → Remote
│    Source: {resolved_source}
│    Target: {resolved_target}
│    Options: {"ZIP compression" if zipFirst else "No compression"}, {"Recursive" if recursive else "Non-recursive"}
└────────────────────────────────────────────────────────────────""")
            received_file = ssh.copy_from_here(source=resolved_source, target=resolved_target, z=zipFirst, r=recursive)

    if source_is_remote and isinstance(received_file, PathExtended):
        print(f"""
┌────────────────────────────────────────────────────────────────
│ 📁 File Received
│    Parent: {repr(received_file.parent)}
│    File: {repr(received_file)}
└────────────────────────────────────────────────────────────────""")
    print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ✅ Transfer Complete
┃    File transfer process finished successfully
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")


def main_from_parser() -> None:
    """Entry point function that uses typer to parse arguments and call main."""
    typer.run(main)


if __name__ == "__main__":
    main_from_parser()
