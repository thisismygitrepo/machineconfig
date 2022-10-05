
from crocodile.environment import OneDriveConsumer, DotFiles
import crocodile.toolbox as tb
import argparse



def main():
    parser = argparse.ArgumentParser(description='OneDrive Backup')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")

    args = parser.parse_args()
    OneDriveConsumer()  # load latest from OneDrive.

    target_file = tb.P(args.path).expanduser().absolute()
    source_file = OneDriveConsumer.joinpath(f"AppData/{target_file.rel2home()}" + "_encrypted.zip")
    tmp_file = source_file.copy(folder=target_file.parent)
    # make sure to avoid doing decryption in the storage site.
    target_file = tmp_file.decrypt(key=None, inplace=True).unzip(inplace=True, verbose=True, overwrite=True, content=True)
    print(f"RETRIEVED {repr(source_file)} {'>' * 10} TO {'>' * 10} {repr(target_file)}")


if __name__ == "__main__":
    main()