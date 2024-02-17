
"""Sx & Rx

TODO: add support for cases in which source or target has non 22 default port number and is defineda as user@host:port:path which makes 2 colons in the string.
Currently, the only way to work around this is to predifine the host in ~/.ssh/config and use the alias in the source or target which is inconvenient when dealing with newly setup machines.
"""

import argparse
from crocodile.meta import SSH, P, Struct
from machineconfig.scripts.python.cloud_sync import ES


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    parser.add_argument("source", help=f"source path (machine:path)")
    parser.add_argument("target", help="target path (machine:path)")

    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zipFirst", "-z", help="Zip before sending.", action="store_true")  # default is False

    args = parser.parse_args()

    if ":" in args.source and (args.source[1] != ":" if len(args.source) > 1 else True):  # avoid the case of "C:/":
        source_is_remote = True

        # calculating source:
        source_parts = args.source.split(":")
        machine = source_parts[0]
        if len(source_parts) > 1 and source_parts[1] == ES:  # the source path is to be inferred from target.
            if args.target == ES: raise ValueError(f"You can't use expand symbol `{ES}` in both source and target. Cyclical inference dependency arised.")
            else: target = P(args.target).expanduser().absolute()
            source = target.collapseuser().as_posix()
        else:
            source = ":".join(args.source.split(":")[1:])
            if args.target == ES: target = None
            else: target = P(args.target).expanduser().absolute().as_posix()

    elif ":" in args.target and (args.target[1] != ":" if len(args.target) > 1 else True):  # avoid the case of "C:/":
        source_is_remote = False
        target_parts = args.target.split(":")
        machine = target_parts[0]
        if len(target_parts) > 1 and target_parts[1] == ES:
            if args.source == ES: raise ValueError(f"You can't use expand symbol `{ES}` in both source and target. Cyclical inference dependency arised.")
            else: source = args.source
            target = None
        else:
            target = ":".join(args.target.split(":")[1:])
            if args.source == ES: source = None
            else: source = P(args.source).expanduser().absolute()

    else:
        raise ValueError("Either source or target must be a remote path (i.e. machine:path)")

    Struct({"source": str(source), "target": str(target), "machine": machine}).print(as_config=True, title="CLI Resolution")
    from paramiko.ssh_exception import AuthenticationException  # type: ignore
    try:
        ssh = SSH(rf'{machine}')
    except AuthenticationException:
        print("Authentication failed, trying manually:")
        print(f"Caution: Ensure that username is passed appropriately as this exception only handles password.")
        import getpass
        pwd = getpass.getpass()
        ssh = SSH(rf'{machine}', pwd=pwd)

    if source_is_remote:
        assert source is not None, "source must be a remote path (i.e. machine:path)"
        print(f"Running: received_file = ssh.copy_to_here(source={source}, target={target}, z={args.zipFirst}, r={args.recursive})")
        received_file = ssh.copy_to_here(source=source, target=target, z=args.zipFirst, r=args.recursive)
    else:
        assert source is not None, "target must be a remote path (i.e. machine:path)"
        print(f"Running: received_file = ssh.copy_from_here(source={source}, target={target}, z={args.zipFirst}, r={args.recursive})")
        received_file = ssh.copy_from_here(source=source, target=target, z=args.zipFirst, r=args.recursive)
    # ssh.print_summary()
    # if P(args.file).is_dir(): print(f"Use: cd {repr(P(args.file).expanduser())}")
    if source_is_remote and isinstance(received_file, P):
        print(f"Received: {repr(received_file.parent), repr(received_file)}")


if __name__ == '__main__':
    main()
