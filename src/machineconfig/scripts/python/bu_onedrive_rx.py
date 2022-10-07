
from crocodile.environment import OneDriveConsumer, OneDriveCommercial
import crocodile.toolbox as tb
import argparse
from machineconfig.scripts.python.bu_gdrive_rx import process_retrieved_file


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
    parser.add_argument("--key", "-k", help="Key for encryption", default=None)
    parser.add_argument("--pwd", "-p", help="Password for encryption", default=None)

    args = parser.parse_args()
    onedrive = OneDriveCommercial if args.commercial else OneDriveConsumer

    target_file = tb.P(args.file).expanduser().absolute()
    source_file = onedrive.joinpath(f"myhome/{target_file.rel2home()}")
    if args.unzip and args.decrypt:
        source_file = source_file.parent / (source_file.trunk + "_encrypted" + "".join(source_file.suffixes) + ".zip")

    tmp_file = source_file.copy(folder=target_file.parent)  # make sure to avoid doing decryption in the storage site.
    process_retrieved_file(args, tmp_file)


if __name__ == "__main__":
    main()
