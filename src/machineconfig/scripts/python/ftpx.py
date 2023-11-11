
"""Sx & Rx
"""

import argparse
from crocodile.toolbox import SSH, P


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    parser.add_argument("source", help=f"source path (machine:path)")
    parser.add_argument("target", help="target path (machine:path)")

    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zipFirst", "-z", help="Zip before sending.", action="store_true")  # default is False

    args = parser.parse_args()

    if ":" in args.source and (args.source[1] != ":" if len(args.source) > 1 else True):  # avoid the case of "C:/":
        machine = args.source.split(":")[0]
        source = args.source.split(":")[1]
        target = P(args.target).expanduser().absolute()
        source_is_remote = True
    elif ":" in args.target and (args.target[1] != ":" if len(args.target) > 1 else True):  # avoid the case of "C:/":
        machine = args.target.split(":")[0]
        target = args.target.split(":")[1]
        source = P(args.source).expanduser().absolute()
        source_is_remote = False
    else:
        raise ValueError("Either source or target must be a remote path (i.e. machine:path)")

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
        received_file = ssh.copy_to_here(source=source, target=target, z=args.zipFirst, r=args.recursive)
    else:
        received_file = ssh.copy_from_here(source=source, target=target, z=args.zipFirst, r=args.recursive)
    # ssh.print_summary()
    # if P(args.file).is_dir(): print(f"Use: cd {repr(P(args.file).expanduser())}")
    if isinstance(received_file, P):
        print(f"Received: {repr(received_file.parent), repr(received_file)}")


if __name__ == '__main__':
    main()
