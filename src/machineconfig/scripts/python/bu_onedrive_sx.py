
# from crocodile.environment import OneDriveConsumer, OneDriveCommercial
from crocodile.comms.helper_funcs import process_sent_file
from crocodile.file_management import P
import argparse


def main():
    parser = argparse.ArgumentParser(description='OneDrive Backup')

    # positional argument
    parser.add_argument("file", help="file/folder path to be backed up", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zip_first", "-z", help="Zip before backing up.", action="store_true")  # default is False
    parser.add_argument("--encrypt_first", "-e", help="Encrypt before backing up.", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--which", "-w", help="Which onedrive to use? see: cat: ~/dotfiles/settings/paths.toml", default="default")
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()

    onedrive = P.home().joinpath("dotfiles/settings/paths.toml").readit()['onedrive']
    onedrive = P.home().joinpath(onedrive[onedrive[args.which]])

    file = process_sent_file(file=args.file, zip_first=args.zip_first, encrypt_first=args.encrypt_first, key=args.key, pwd=args.pwd)
    remote_dir = onedrive.joinpath(f"myhome/{file.rel2home().parent}")
    path = file.copy(folder=remote_dir, overwrite=True)
    if args.zip_first or args.encrypt_first: P(file).delete(sure=True)
    onedrive()  # push to OneDrive


if __name__ == "__main__":
    main()
