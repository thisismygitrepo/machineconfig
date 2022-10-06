
from crocodile.environment import OneDriveConsumer, OneDriveCommercial
import crocodile.toolbox as tb
import argparse


def main():
    parser = argparse.ArgumentParser(description='OneDrive Backup')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--commercial", "-c", help="Use onedrive commercial.", action="store_true")  # default is False
    parser.add_argument("--decrypt", "-e", help="Send recursively.", action="store_true")  # default is False
    parser.add_argument("--unzip", "-z", help="unzip file.", action="store_true")  # default is False

    # optional argument

    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")

    args = parser.parse_args()
    onedrive = OneDriveCommercial if args.commercial else OneDriveConsumer

    target_file = tb.P(args.file).expanduser().absolute()
    source_file = onedrive.joinpath(f"myhome/{target_file.rel2home()}")  # + "_encrypted.zip"
    tmp_file = source_file.copy(folder=target_file.parent)  # make sure to avoid doing decryption in the storage site.



if __name__ == "__main__":
    main()
