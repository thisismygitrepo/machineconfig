
from crocodile.environment import OneDriveConsumer, DotFiles
import crocodile.toolbox as tb
# import crocodile.environment as env


def symlink(this: tb.P, to_this: tb.P, overwrite=True):
    """helper function. creates a symlink from `this` to `to_this`.
    What can go wrong?
    depending on this and to_this existence, one will be prioretized depending on overwrite value.
    True means this will potentially be overwritten (depending on whether to_this exists or not)
    False means to_this will potentially be overwittten."""
    if this.is_symlink(): this.delete(sure=True)  # delete if it exists as symblic link, not a concrete path.
    if this.exists():  # this is a problem. It will be resolved via `overwrite`
        if overwrite is True:  # it *can* be deleted, but let's look at target first.
            if to_this.exists(): this.delete(sure=True)  # this exists, to_this as well. to_this is prioritized.
            else: this.move(path=to_this)  # this exists, to_this doesn't. to_this is prioritized.
        elif overwrite is False:  # don't sacrefice this, sacrefice to_this.
            if to_this.exists(): this.move(path=to_this, overwrite=True)  # this exists, to_this as well, this is prioritized.   # now we are readly to make the link
            else: this.move(path=to_this)  # this exists, to_this doesn't, this is prioritized.
    else:  # this doesn't exist.
        if not to_this.exists(): to_this.touch()  # we have to touch it (file) or create it (folder)
    try: tb.P(this).symlink_to(to_this, verbose=True, overwrite=True)
    except Exception as ex: print(f"Failed at linking {this} ==> {to_this}.\nReason: {ex}")


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


def get_latest_release(repo_url):
    import requests  # https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases
    latest_version = requests.get(repo_url + "/releases/latest").url.split("/")[-1]  # this is to resolve the redirection that occures: https://stackoverflow.com/questions/36070821/how-to-get-redirect-url-using-python-requests
    return repo_url + "/releases/download/" + latest_version


if __name__ == '__main__':
    pass
