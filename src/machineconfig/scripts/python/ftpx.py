
"""Sx & Rx
"""

import argparse
from crocodile.meta import SSH, P, Struct


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
        if len(source_parts) > 1 and source_parts[1] == "$":  # the source path is to be inferred from target.
            if args.target == "$":
                raise ValueError("You can't use $ in both source and target. Cyclical inference dependency arised.")
            else:
                target = P(args.target).expanduser().absolute()
            source = target.collapseuser().as_posix()
        else:
            source = ":".join(args.source.split(":")[1:])
            if args.target == "$":
                target = None
            else: target = P(args.target).expanduser().absolute().as_posix()

    elif ":" in args.target and (args.target[1] != ":" if len(args.target) > 1 else True):  # avoid the case of "C:/":
        source_is_remote = False
        target_parts = args.target.split(":")
        machine = target_parts[0]
        if len(target_parts) > 1 and target_parts[1] == "$":
            if args.source == "$":
                raise ValueError("You can't use $ in both source and target. Cyclical inference dependency arised.")
            else:
                source = args.source
            target = None
        else:
            target = ":".join(args.target.split(":")[1:])
            if args.source == "$":
                source = None
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
        print(f"Running: received_file = ssh.copy_to_here(source={source}, target={target}, z={args.zipFirst}, r={args.recursive})")
        received_file = ssh.copy_to_here(source=source, target=target, z=args.zipFirst, r=args.recursive)
    else:
        print(f"Running: received_file = ssh.copy_from_here(source={source}, target={target}, z={args.zipFirst}, r={args.recursive})")
        received_file = ssh.copy_from_here(source=source, target=target, z=args.zipFirst, r=args.recursive)
    # ssh.print_summary()
    # if P(args.file).is_dir(): print(f"Use: cd {repr(P(args.file).expanduser())}")
    if isinstance(received_file, P):
        print(f"Received: {repr(received_file.parent), repr(received_file)}")


if __name__ == '__main__':
    main()
