
import argparse
from crocodile.toolbox import SSH


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    parser.add_argument("machine", help=f"machine ssh address", default="")
    parser.add_argument("file", help="file/folder path.", default="")

    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zipFirst", "-z", help="Zip before sending.", action="store_true")  # default is False

    # optional
    parser.add_argument("-d", "--destination", help=f"destination folder", default=None)
    # parser.add_argument("-d", "--destination", help=f"destination folder", default=None)

    args = parser.parse_args()
    import paramiko
    try:
        ssh = SSH(rf'{args.machine}')
    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication failed, trying manually:")
        print(f"Caution: Ensure that username is passed appropriately as this exception only handles password.")
        import getpass
        pwd = getpass.getpass()
        ssh = SSH(rf'{args.machine}', pwd=pwd)

    ssh.copy_from_here(source=args.file, target=args.destination, z=args.zipFirst, r=args.recursive)
    # ssh.print_summary()


if __name__ == '__main__':
    main()
