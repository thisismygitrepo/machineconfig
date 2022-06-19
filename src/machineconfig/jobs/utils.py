
from crocodile.environment import OneDriveConsumer, OneDriveExe, DotFiles
import crocodile.toolbox as tb


def backup(path):
    """Encrypts and saves a copy of `dotfiles` to OneDrive"""
    key = DotFiles.joinpath("creds/encrypted_files_key.bytes")
    downloaded_key_from_lastpass = False
    if not key.exists():
        key = tb.P.home().joinpath("Downloads/key.zip").unzip(inplace=False, verbose=True).find()
        downloaded_key_from_lastpass = True
    tb.P(path).zip_n_encrypt(key=key, inplace=False, verbose=True).move(folder=OneDriveConsumer.joinpath("AppData"), overwrite=True)
    if downloaded_key_from_lastpass: key.delete(sure=True)
    print(f" ========================= SUCCESSFULLY BACKEDUP {path} ===============================")
    OneDriveExe()  # push to OneDrive


def retrieve(source_file, target_folder):
    """Decrypts and brings a copy of `dotfiles` from OneDrive"""
    OneDriveExe()  # load latest from OneDrive.
    key = DotFiles.joinpath("creds/encrypted_files_key.bytes")
    if not key.exists(): key = tb.P(input(f"path to key (DONT'T use quotation marks nor raw prefix):")).unzip(inplace=False, verbose=True).find()
    dotfiles = OneDriveConsumer.joinpath(f"AppData/{source_file}").copy(folder=target_folder)
    # make sure to avoid doing decryption in the storage site.
    dotfiles.decrypt(key=key, inplace=True).unzip(folder=target_folder, inplace=True, verbose=True)
    print(f" ========================= SUCCESSFULLY RETRIEVED {source_file} ===============================")


if __name__ == '__main__':
    pass
