
import argparse
from crocodile.toolbox import SSH
import crocodile.toolbox as tb


def main():
    parser = argparse.ArgumentParser(description='FTP client')

    parser.add_argument("machine", help=f"machine ssh address", default="")
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zipFirst", "-z", help="Zip before sending.", action="store_true")  # default is False

    parser.add_argument("-d", "--destination", help=f"destination folder", default=None)

    args = parser.parse_args()
    ssh = SSH(rf'{args.machine}')
    received_file = ssh.copy_to_here(source=args.file, target=args.destination, z=args.zipFirst, r=args.recursive)
    # ssh.print_summary()

    if tb.P(args.file).is_dir(): print(f"Use: cd {repr(tb.P(args.file).expanduser())}")
    elif received_file is not None: print(f"Received: {repr(received_file.parent), repr(received_file)}")


if __name__ == '__main__':
    main()
