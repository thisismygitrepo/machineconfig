
import crocodile.toolbox as tb
# import crocodile.environment as env


def symlink(this: tb.P, to_this: tb.P, overwrite=True):
    """helper function. creates a symlink from `this` to `to_this`.
    What can go wrong?
    depending on this and to_this existence, one will be prioretized depending on overwrite value.
    True means this will potentially be overwritten (depending on whether to_this exists or not)
    False means to_this will potentially be overwittten."""
    this = tb.P(this).expanduser().absolute()
    to_this = tb.P(to_this).expanduser().absolute()
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


def get_latest_release(repo_url, download_n_extract=False, suffix="x86_64-pc-windows-msvc", name=None, tool_name=None):
    import requests  # https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases
    latest_version = requests.get(repo_url + "/releases/latest").url.split("/")[-1]  # this is to resolve the redirection that occures: https://stackoverflow.com/questions/36070821/how-to-get-redirect-url-using-python-requests
    download_link = tb.P(repo_url + "/releases/download/" + latest_version)
    if download_n_extract:
        if name is None:
            tool = tool_name or tb.P(repo_url)[-1]
            version = download_link[-1]
            name = f'{tool}-{version}-{suffix}.zip'
            print("Downloading", download_link.joinpath(name))
        exe = download_link.joinpath(name).download().unzip(inplace=True, overwrite=True)
        if exe.is_file(): pass
        else: exe = exe.search("*.exe", r=True)[0] if tool_name is None else exe.search(f"{tool_name}.exe", r=True)[0]
        exe.move(folder=tb.P.get_env().WindowsApps, overwrite=True)  # latest version overwrites older installation.
        return exe
    return download_link


if __name__ == '__main__':
    pass
