
import crocodile.toolbox as tb
# import crocodile.environment as env
import machineconfig


LIBRARY_ROOT = tb.P(machineconfig.__file__).parent
REPO_ROOT = LIBRARY_ROOT.parent.parent


def display_options(msg, options: list, header="", default=None):
    print("\n")
    print(header.center(50, "-"))
    print(msg)

    if default is not None:
        assert default in options, f"Default `{default}` option not in options."
        default_msg = f"<<<<-------- DEFAULT"
    else: default_msg = ""

    for idx, key in enumerate(options):
        print(f"{idx:2d}", key, default_msg if default is not None and default == key else "")

    choice_idx = input(f"Enter option *number* (or option name starting with space): ")
    if choice_idx.startswith(" "):
        choice_key = choice_idx.strip()
        assert choice_key in options, f"Choice `{choice_key}` not in options."
        choice_idx = options.index(choice_key)
    else:
        if choice_idx == "":
            assert default is not None, f"Default option not available!"
            choice_idx = options.index(default)
        try:
            choice_key = options[int(choice_idx)]
        except IndexError:
            raise ValueError(f"Unknown choice. {choice_idx}")

    print(f"{choice_idx}: {choice_key}", f"<<<<-------- CHOICE MADE")
    return choice_key


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
            if to_this.exists():
                # this.delete(sure=True)  # this exists, to_this as well. to_this is prioritized.
                this.append(f".orig_{tb.randstr()}", inplace=True)  # rename is better than deletion
            else: this.move(path=to_this)  # this exists, to_this doesn't. to_this is prioritized.
        elif overwrite is False:  # don't sacrefice this, sacrefice to_this.
            if to_this.exists(): this.move(path=to_this, overwrite=True)  # this exists, to_this as well, this is prioritized.   # now we are readly to make the link
            else: this.move(path=to_this)  # this exists, to_this doesn't, this is prioritized.
    else:  # this doesn't exist.
        if not to_this.exists(): to_this.touch()  # we have to touch it (file) or create it (folder)
    try: tb.P(this).symlink_to(to_this, verbose=True, overwrite=True)
    except Exception as ex: print(f"Failed at linking {this} ==> {to_this}.\nReason: {ex}")


def find_move_delete_windows(downloaded, tool_name=None, delete=True):
    if downloaded.is_file():
        exe = downloaded
    else:
        exe = downloaded.search("*.exe", r=True)[0] if tool_name is None else downloaded.search(f"{tool_name}.exe", r=True)[0]
    exe.move(folder=tb.P.get_env().WindowsApps, overwrite=True)  # latest version overwrites older installation.
    if delete: downloaded.delete(sure=True)
    return exe


def find_move_delete_linux(downloaded, tool_name, delete=True):
    if downloaded.is_file():
        exe = downloaded
    else:
        res = downloaded.search()
        if len(res) == 1:
            if res[0].is_file():
                exe = res[0]
            else:
                res = res[0].search()
                exe = res[0] if len(res) == 1 else res[0].parent.joinpath(tool_name)
        else:
            exe = downloaded.joinpath(tool_name)
    print(f"MOVING file `{repr(exe)}` to '/usr/local/bin'")
    exe.chmod(0o777)
    # exe.move(folder=r"/usr/local/bin", overwrite=False)
    tb.Terminal().run(f"sudo mv {exe} /usr/local/bin/").print()
    if delete: downloaded.delete(sure=True)


def get_latest_release(repo_url, download_n_extract=False, suffix="x86_64-pc-windows-msvc", file_name=None, tool_name=None, exe_name=None, delete=True, strip_v=False, linux=False, compression=None):
    import requests  # https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases
    latest_version = requests.get(str(repo_url) + "/releases/latest").url.split("/")[-1]  # this is to resolve the redirection that occures: https://stackoverflow.com/questions/36070821/how-to-get-redirect-url-using-python-requests
    download_link = tb.P(repo_url + "/releases/download/" + latest_version)

    version = download_link[-1]
    version = str(version).replace("v", "") if strip_v else version
    tool_name = tool_name or tb.P(repo_url)[-1]

    if not download_n_extract: return download_link
    print("\n\n\n")
    print(f"Installing {tool_name} version {version}".center(100, "-"))
    if download_n_extract and not linux:
        if file_name is None:  # it is not constant, so we compile it from parts as follows:
            file_name = f'{tool_name}-{version}-{suffix}.{compression or "zip"}'
        print("Downloading", download_link.joinpath(file_name))
        downloaded = download_link.joinpath(file_name).download().unzip(inplace=True, overwrite=True)
        return find_move_delete_windows(downloaded, exe_name or tool_name, delete)
    elif download_n_extract and linux:
        if file_name is None:  # it is not constant, so we compile it from parts as follows:
            file_name = f'{tool_name}-{version}-{suffix}.{compression or "tar.gz"}'
        download_link = download_link.joinpath(file_name)
        print("Downloading", download_link)
        downloaded = download_link.download()
        downloaded = download_link.ungz_untar(inplace=True) if "tar.gz" in download_link else downloaded.unzip(inplace=True)
        find_move_delete_linux(downloaded, exe_name or tool_name, delete)
    print(f"Completed Installation".center(100, "-"))


def get_shell_script_executing_pyscript(python_file, func=None, system=None, ve_name="ve"):
    return f"""
~/venvs/{ve_name}/Scripts/activate.ps1
python {python_file} {func if func is not None else ""}
""" if system == "Windows" else f"""
. ~/venvs/{ve_name}/bin/activate
python {python_file} {func if func is not None else ""}
deactivate
"""


if __name__ == '__main__':
    pass
