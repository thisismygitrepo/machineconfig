
from crocodile.environment import OneDriveConsumer, DotFiles
import crocodile.toolbox as tb
import argparse


def retrieve_from_onedrive(target_file):
    """Decrypts and brings a copy of `path` from OneDrive"""
    OneDriveConsumer()  # load latest from OneDrive.
    key = DotFiles.joinpath("creds/encrypted_files_key.bytes")
    if not key.exists(): key = tb.P(input(f"path to key (DONT'T use quotation marks nor raw prefix):")).unzip(inplace=False, verbose=True).find()
    target_file = tb.P(target_file).expanduser().absolute()
    source_file = OneDriveConsumer.joinpath(f"AppData/{target_file.rel2home()}" + "_encrypted.zip")
    tmp_file = source_file.copy(folder=target_file.parent)
    # make sure to avoid doing decryption in the storage site.
    target_file = tmp_file.decrypt(key=key, inplace=True).unzip(inplace=True, verbose=True, overwrite=True, content=True)
    print(f"RETRIEVED {repr(source_file)} {'>' * 10} TO {'>' * 10} {repr(target_file)}")


def main():
    parser = argparse.ArgumentParser(description='OneDrive Backup')

    # positional argument
    parser.add_argument("file", help="file/folder path.", default="")
    # FLAGS
    parser.add_argument("--recursive", "-r", help="Send recursively.", action="store_true")  # default is False
    # optional argument
    parser.add_argument("--remote_dir", "-d", help="Remote directory to send to.", default="")

    args = parser.parse_args()


if __name__ == "__main__":
    main()
