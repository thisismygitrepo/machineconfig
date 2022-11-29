
# from crocodile.environment import OneDriveConsumer, OneDriveCommercial
import crocodile.toolbox as tb
import argparse
from crocodile.comms.helper_funcs import process_retrieved_file
import os

def main():
    parser = argparse.ArgumentParser(description='OneDrive Backup')

    # positional argument
    parser.add_argument("file", help="file/folder path to be received.", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--decrypt", "-e", help="Decrypt after receiving.", action="store_true")  # default is False
    parser.add_argument("--unzip", "-z", help="unzip after receiving.", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--which", "-w", help="Which onedrive to use? see: cat: ~/dotfiles/settings/paths.toml", default="default")
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()

    if (onedrive_settings_path := tb.P.home().joinpath("dotfiles/settings/paths.toml")).exists():
        onedrive = onedrive_settings_path.readit()['onedrive']
        onedrive = tb.P.home().joinpath(onedrive[onedrive[args.which]])
    else:
        onedrive = tb.P.home().joinpath(os.environ["OneDrive"])

    target_file = tb.P(args.file).expanduser().absolute()
    source_file = onedrive.joinpath(f"myhome/{target_file.rel2home()}")
    if args.unzip and args.decrypt: source_file = source_file + ".zip.enc"

    tmp_file = source_file.copy(folder=target_file.parent)  # make sure to avoid doing decryption in the storage site.
    process_retrieved_file(tmp_file, decrypt=args.decrypt, unzip=args.unzip, key=args.key, pwd=args.pwd)


if __name__ == "__main__":
    main()
