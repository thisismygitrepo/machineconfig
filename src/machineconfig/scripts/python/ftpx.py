#!/usr/bin/env -S uv run --project /home/alex/code/machineconfig --script
"""Sx & Rx

TODO: add support for cases in which source or target has non 22 default port number and is defineda as user@host:port:path which makes 2 colons in the string.
Currently, the only way to work around this is to predifine the host in ~/.ssh/config and use the alias in the source or target which is inconvenient when dealing with newly setup machines.

"""

import argparse
from machineconfig.utils.ssh import SSH
from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.scripts.python.helpers.helpers2 import ES
from machineconfig.utils.utils2 import pprint


def main():
    print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🚀 FTP File Transfer
┃ 📋 Starting transfer process...
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    parser = argparse.ArgumentParser(description="FTP client")

    parser.add_argument("source", help="source path (machine:path)")
    parser.add_argument("target", help="target path (machine:path)")

    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zipFirst", "-z", help="Zip before sending.", action="store_true")  # default is False
    parser.add_argument("--cloud", "-c", help="Transfer through the cloud.", action="store_true")  # default is False

    args = parser.parse_args()

    if ":" in args.source and (args.source[1] != ":" if len(args.source) > 1 else True):  # avoid the case of "C:/":
        source_is_remote = True

        # calculating source:
        source_parts = args.source.split(":")
        machine = source_parts[0]
        if len(source_parts) > 1 and source_parts[1] == ES:  # the source path is to be inferred from target.
            if args.target == ES:
                raise ValueError(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ❌ Configuration Error
┃    Cannot use expand symbol `{ES}` in both source and target
┃    This creates a cyclical inference dependency
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            else:
                target = PathExtended(args.target).expanduser().absolute()
            source = target.collapseuser().as_posix()
        else:
            source = ":".join(args.source.split(":")[1:])
            if args.target == ES:
                target = None
            else:
                target = PathExtended(args.target).expanduser().absolute().as_posix()

    elif ":" in args.target and (args.target[1] != ":" if len(args.target) > 1 else True):  # avoid the case of "C:/":
        source_is_remote = False
        target_parts = args.target.split(":")
        machine = target_parts[0]
        if len(target_parts) > 1 and target_parts[1] == ES:
            if args.source == ES:
                raise ValueError(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ❌ Configuration Error
┃    Cannot use expand symbol `{ES}` in both source and target
┃    This creates a cyclical inference dependency
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
            else:
                source = args.source
            target = None
        else:
            target = ":".join(args.target.split(":")[1:])
            if args.source == ES:
                source = None
            else:
                source = PathExtended(args.source).expanduser().absolute()

    else:
        raise ValueError("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ❌ Path Error
┃    Either source or target must be a remote path
┃    Format should be: machine:path
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    pprint({"source": str(source), "target": str(target), "machine": machine}, "CLI Resolution")

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

    if args.cloud:
        print("""
┌────────────────────────────────────────────────────────────────
│ ☁️  Cloud Transfer Mode
│    Uploading from remote to cloud...
└────────────────────────────────────────────────────────────────""")
        ssh.run(f"cloud_copy {source} :^", desc="Uploading from remote to the cloud.").print()
        print("""
┌────────────────────────────────────────────────────────────────
│ ⬇️  Cloud Transfer Mode
│    Downloading from cloud to local...
└────────────────────────────────────────────────────────────────""")
        ssh.run_locally(f"cloud_copy :^ {target}").print()
        received_file = PathExtended(target)  # type: ignore
    else:
        if source_is_remote:
            assert source is not None, """
❌ Path Error: Source must be a remote path (machine:path)"""
            print(f"""
┌────────────────────────────────────────────────────────────────
│ 📥 Transfer Mode: Remote → Local
│    Source: {source}
│    Target: {target}
│    Options: {"ZIP compression" if args.zipFirst else "No compression"}, {"Recursive" if args.recursive else "Non-recursive"}
└────────────────────────────────────────────────────────────────""")
            received_file = ssh.copy_to_here(source=source, target=target, z=args.zipFirst, r=args.recursive)
        else:
            assert source is not None, """
❌ Path Error: Target must be a remote path (machine:path)"""
            print(f"""
┌────────────────────────────────────────────────────────────────
│ 📤 Transfer Mode: Local → Remote
│    Source: {source}
│    Target: {target}
│    Options: {"ZIP compression" if args.zipFirst else "No compression"}, {"Recursive" if args.recursive else "Non-recursive"}
└────────────────────────────────────────────────────────────────""")
            received_file = ssh.copy_from_here(source=source, target=target, z=args.zipFirst, r=args.recursive)

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


if __name__ == "__main__":
    main()
