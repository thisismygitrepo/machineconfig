
from crocodile.environment import OneDriveConsumer, DotFiles
from machineconfig.scripts.python.bu_gdrive_sx import process_file
import crocodile.toolbox as tb
import argparse


def main():
    parser = argparse.ArgumentParser(description='OneDrive Backup')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zip_first", "-z", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--encrypt_first", "-e", help="Send recursively.", action="store_true")  # default is False

    # optional argument
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")

    args = parser.parse_args()

    path = tb.P(args.file).expanduser().absolute()
    file = process_file(args)
    path = path.move(path=OneDriveConsumer.joinpath(f"AppData/{path.rel2home()}"), overwrite=True)
    print(f"BACKEDUP {repr(path)} {'>' * 10} TO {'>' * 10} {repr(path)}")
    OneDriveConsumer()  # push to OneDrive


if __name__ == "__main__":
    main()
