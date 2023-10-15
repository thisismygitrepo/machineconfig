
from dataclasses import dataclass
from typing import Optional

from crocodile.file_management import P
from crocodile.meta import Terminal
from rich.console import Console

from machineconfig.utils.utils import APP_VERSION_ROOT, TMP_INSTALL_DIR


def find_move_delete_windows(downloaded: P, tool_name: Optional[str] = None, delete: bool = True, rename_to: Optional[str] = None):
    if tool_name is not None and ".exe" in tool_name: tool_name = tool_name.replace(".exe", "")
    if downloaded.is_file():
        exe = downloaded
    else:
        if tool_name is None: exe = downloaded.search("*.exe", r=True).list[0]
        else:
            tmp = downloaded.search(f"{tool_name}.exe", r=True)
            if len(tmp) == 1: exe = tmp.list[0]
            else: exe = downloaded.search("*.exe", r=True).list[0]
    if rename_to: exe = exe.with_name(name=rename_to, inplace=True)
    exe.move(folder=P.get_env().WindowsApps, overwrite=True)  # latest version overwrites older installation.
    if delete: downloaded.delete(sure=True)
    return exe


def find_move_delete_linux(downloaded: P, tool_name: str, delete: Optional[bool] = True, rename_to: Optional[str] = None) -> None:
    if downloaded.is_file():
        exe = downloaded
    else:
        res = downloaded.search(f"*{tool_name}*", folders=False, r=True)
        if len(res) == 1: exe = res.list[0]
        else: exe = downloaded.search(tool_name, folders=False, r=True).list[0]
    if rename_to: exe = exe.with_name(name=rename_to, inplace=True)
    print(f"MOVING file `{repr(exe)}` to '/usr/local/bin'")
    exe.chmod(0o777)
    # exe.move(folder=r"/usr/local/bin", overwrite=False)
    Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)
    if delete: downloaded.delete(sure=True)
    return None


@dataclass
class Release:
    version: Optional[str]
    release_url: P
    download_url: P


def get_latest_release(repo_url: str, exe_name: str,
                       download_n_extract: bool = False, suffix: Optional[str] = "x86_64-pc-windows-msvc",
                       file_name: Optional[str] = None,  # e.g. windows_x86_64.zip
                       tool_name: Optional[str] = None,
                       delete: bool = True, strip_v: bool = False, linux: bool = False, compression: Optional[str] = None,
                       sep: Optional[str] = "-", version: Optional[str] = None):
    """Arguments help form last part of URL  `filename = f'{tool_name}{sep}{version}{sep}{suffix}.{compression}'`
     Unless `file_name` is passed directly,  in which case it is used as is and parameters above are ignored.
    """
    console = Console()
    print("\n\n\n")
    print(f"Inspecting latest release @ {repo_url}   ...")
    # with console.status("Installing..."):  # makes troubles on linux when prompt asks for password to move file to /usr/bin

    if version is None:
        import requests  # https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases
        _latest_version = requests.get(str(repo_url) + "/releases/latest", timeout=10).url.split("/")[-1]  # this is to resolve the redirection that occures: https://stackoverflow.com/questions/36070821/how-to-get-redirect-url-using-python-requests
        version_to_be_installed = _latest_version
    else:
        version_to_be_installed = version

    release_url = P(repo_url + "/releases/download/" + version_to_be_installed)

    # existing_version_cli = Terminal().run(f"{exe_name or tool_name} --version", shell="powershell").op_if_successfull_or_default(strict_err=True, strict_returcode=True)
    tmp_path = APP_VERSION_ROOT.joinpath(exe_name).create(parents_only=True)
    if tmp_path.exists(): existing_version = tmp_path.read_text().rstrip()
    else: existing_version = None

    if existing_version is not None:
        if existing_version == version_to_be_installed:
            print(f"⚠️ {exe_name} already installed at version {version_to_be_installed}")
            return
        else:
            # print(f"Latest version is {version}, logged at {tmp_path}")
            print(f"⬆️ {exe_name} installed at version {existing_version.rstrip()} --> Installing version {version_to_be_installed} ")
            tmp_path.write_text(version_to_be_installed)
    else:
        print(f"{exe_name} has no known version. Installing version `{version_to_be_installed}` ")
        tmp_path.write_text(version_to_be_installed)

    if not download_n_extract: return release_url

    console.rule(f"Installing {exe_name} version {version_to_be_installed}")

    if file_name is None:  # it is not constant, so we compile it from parts as follows:
        version_in_filename = version_to_be_installed.replace("v", "") if strip_v else version_to_be_installed
        compression = compression or ("zip" if not linux else "tar.gz")
        tool_name = tool_name or str(P(repo_url)[-1])
        file_name = f'{tool_name}{sep}{version_in_filename}{sep}{suffix}.{compression}'
    download_link = release_url.joinpath(file_name)

    print("Downloading", download_link.as_url_str())
    downloaded = download_link.download(folder=TMP_INSTALL_DIR)
    if "tar.gz" in download_link: downloaded = downloaded.ungz_untar(inplace=True)
    elif "zip" in download_link: downloaded = downloaded.unzip(inplace=True, overwrite=True)
    elif "tar.xz" in download_link: downloaded = downloaded.unxz_untar(inplace=True)
    else: pass  # no compression.

    if not linux: return find_move_delete_windows(downloaded=downloaded, tool_name=exe_name, delete=delete)
    return find_move_delete_linux(downloaded=downloaded, tool_name=exe_name, delete=delete)
    # console.rule(f"Completed Installation")
    # return res
