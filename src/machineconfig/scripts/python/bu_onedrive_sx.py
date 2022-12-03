
from crocodile.environment import OneDriveExe
from crocodile.comms.helper_funcs import process_sent_file
from crocodile.file_management import P
import argparse
import os


def main(which, file, zip_first, encrypt_first, key, pwd, overwrite):
    if (onedrive_settings_path := P.home().joinpath("dotfiles/settings/paths.toml")).exists():
        onedrive = onedrive_settings_path.readit()['onedrive']
        onedrive = P.home().joinpath(onedrive[onedrive[which]])
    else:
        onedrive = P.home().joinpath(os.environ["OneDrive"])

    file = process_sent_file(file=file, zip_first=zip_first, encrypt_first=encrypt_first, key=key, pwd=pwd)
    remote_dir = onedrive.joinpath(f"myhome/{file.rel2home().parent}")
    path = file.copy(folder=remote_dir, overwrite=overwrite)
    if zip_first or encrypt_first: P(file).delete(sure=True)
    OneDriveExe()  # push to OneDrive


def arg_parser():
    parser = argparse.ArgumentParser(description='OneDrive Backup')

    # positional argument
    parser.add_argument("file", help="file/folder path to be backed up", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--zip_first", "-z", help="Zip before backing up.", action="store_true")  # default is False
    parser.add_argument("--encrypt_first", "-e", help="Encrypt before backing up.", action="store_true")  # default is False
    parser.add_argument("--overwrite", "-o", help="Overwrite existing file.", action="store_true")  # default is False

    # optional argument
    parser.add_argument("--which", "-w", help="Which onedrive to use? see: cat: ~/dotfiles/settings/paths.toml", default="default")
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--relative_to_home", "-R", help="Relative to `myhome` folder", action="store_true")  # default is False
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()
    main(which=args.which, file=args.file, zip_first=args.zip_first, encrypt_first=args.encrypt_first, pwd=args.pwd, key=args.key, overwrite=True)


if __name__ == "__main__":
    arg_parser()
