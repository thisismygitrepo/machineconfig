
from crocodile.environment import OneDriveConsumer, DotFiles
import crocodile.toolbox as tb
import argparse


def backup_to_onedrive(path):
    """Zips, encrypts and saves a copy of `path` to OneDrive's AppData folder"""
    key = DotFiles.joinpath("creds/encrypted_files_key.bytes")
    downloaded_key_from_lastpass = False
    if not key.exists():
        key = tb.P.home().joinpath("Downloads/key.zip").unzip(inplace=False, verbose=True).find()
        downloaded_key_from_lastpass = True
    path = tb.P(path).expanduser().absolute()
    res_path = path.zip_n_encrypt(key=key, inplace=False, verbose=True, content=False)
    res_path = res_path.move(path=OneDriveConsumer.joinpath(f"AppData/{res_path.rel2home()}"), overwrite=True)
    if downloaded_key_from_lastpass: key.delete(sure=True)
    print(f"BACKEDUP {repr(path)} {'>' * 10} TO {'>' * 10} {repr(res_path)}")
    OneDriveConsumer()  # push to OneDrive


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
