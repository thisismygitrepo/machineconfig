
from crocodile.environment import OneDriveConsumer, OneDriveCommercial
from machineconfig.scripts.python.bu_gdrive_sx import process_file
from crocodile.file_management import P
import argparse


def main():
    parser = argparse.ArgumentParser(description='OneDrive Backup')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zip_first", "-z", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--encrypt_first", "-e", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--commercial", "-c", help="Use onedrive commercial.", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()
    onedrive = OneDriveCommercial if args.commercial else OneDriveConsumer

    file = process_file(args)
    remote_dir = onedrive.joinpath(f"myhome/{file.rel2home().parent}")

    path = file.copy(folder=remote_dir, overwrite=True)
    if args.zip_first or args.encrypt_first:
        P(file).delete(sure=True)
    onedrive()  # push to OneDrive


if __name__ == "__main__":
    main()
