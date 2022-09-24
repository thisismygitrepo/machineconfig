
import argparse
from crocodile.toolbox import SSH


def main():
    parser = argparse.ArgumentParser(description='FTP client')
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zipFirst", "-z", help="Zip before sending.", action="store_true")  # default is False
    # OPTIONAL KEYWORD
    parser.add_argument("--file", "-f", dest="file", help="file/folder path.", default="")
    parser.add_argument("--machine", "-m", dest="machine", help=f"machine ssh address", default="")

    args = parser.parse_args()
    ssh = SSH(rf'{args.machine}')
    ssh.copy_from_here(args.file, zip_first=args.zipFirst, r=args.recursive)
    ssh.print_summary()


if __name__ == '__main__':
    main()
