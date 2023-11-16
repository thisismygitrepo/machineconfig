
"""package manager
"""
from rich.console import Console

from crocodile.file_management import P, List as L, Read
from crocodile.meta import Terminal
from machineconfig.utils.utils import INSTALL_VERSION_ROOT, INSTALL_TMP_DIR

from dataclasses import dataclass
from typing import Optional, Literal
import platform


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
    tmp_path = INSTALL_VERSION_ROOT.joinpath(exe_name).create(parents_only=True)
    if tmp_path.exists(): existing_version = tmp_path.read_text().rstrip()
    else: existing_version = None

    if existing_version is not None:
        if existing_version == version_to_be_installed:
            print(f"⚠️ {exe_name} already installed at version {version_to_be_installed}. See {INSTALL_VERSION_ROOT}")
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
    downloaded = download_link.download(folder=INSTALL_TMP_DIR)
    if "tar.gz" in download_link or "tgz" in download_link: downloaded = downloaded.ungz_untar(inplace=True)
    elif "zip" in download_link: downloaded = downloaded.unzip(inplace=True, overwrite=True)
    elif "tar.xz" in download_link: downloaded = downloaded.unxz_untar(inplace=True)
    else: pass  # no compression.

    if not linux: return find_move_delete_windows(downloaded=downloaded, tool_name=exe_name, delete=delete)
    return find_move_delete_linux(downloaded=downloaded, tool_name=exe_name, delete=delete)
    # console.rule(f"Completed Installation")
    # return res


def get_cli_py_installers(dev: bool = False, system: Optional[Literal['Windows', "Linux"]] = None):
    system_ = platform.system() if system is None else system
    if system_ == "Windows": import machineconfig.jobs.python_windows_installers as inst
    else: import machineconfig.jobs.python_linux_installers as inst
    import machineconfig.jobs.python_generic_installers as gens
    path = P(inst.__file__).parent
    gens_path = P(gens.__file__).parent
    if dev:
        path = path.joinpath("dev")
        gens_path = gens_path.joinpath("dev")
    return path.search("*.py", filters=[lambda x: "__init__" not in str(x)]) + gens_path.search("*.py", filters=[lambda x: "__init__" not in str(x)])


def get_installed_cli_apps():
    if platform.system() == "Windows": apps = P.home().joinpath("AppData/Local/Microsoft/WindowsApps").search("*.exe", not_in=["notepad"])
    elif platform.system() == "Linux": apps = P(r"/usr/local/bin").search("*")
    else: raise NotImplementedError("Not implemented for this OS")
    apps = L([app for app in apps if app.size("kb") > 0.1 and not app.is_symlink()])  # no symlinks like paint and wsl and bash
    return apps


def run_python_installer(py_file: P, version: Optional[str] = None):
    try:
        old_version = Terminal().run(f"{py_file.stem} --version", shell="powershell").op.replace("\n", "")
        Read.py(py_file)["main"](version=version)
        new_version = Terminal().run(f"{py_file.stem} --version", shell="powershell").op.replace("\n", "")
        if old_version == new_version: return f"😑 {py_file.stem}, same version: {old_version}"
        else: return f"🤩 {py_file.stem} updated from {old_version} === to ===> {new_version}"
    except Exception as ex:
        print(ex)
        return f"Failed at {py_file.stem} with {ex}"


def install_all(installers: Optional[list[P]] = None, safe: bool = False, dev: bool = False, jobs: int = 10, fresh: bool = False):
    if fresh: INSTALL_VERSION_ROOT.delete(sure=True)
    if safe:
        from machineconfig.jobs.python.check_installations import APP_SUMMARY_PATH
        apps_dir = APP_SUMMARY_PATH.readit()
        if platform.system().lower() == "windows":
            apps_dir.search("*").apply(lambda app: app.move(folder=P.get_env().WindowsApps))
        elif platform.system().lower() == "linux":
            Terminal().run(f"sudo mv {apps_dir.as_posix()}/* /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)
        else: raise NotImplementedError(f"I don't know this system {platform.system()}")
        apps_dir.delete(sure=True)
        return None

    if not isinstance(installers, list): installers_concrete = get_cli_py_installers(dev=dev)
    else: installers_concrete = L(installers)

    run_python_installer(installers_concrete.list[0])  # try out the first installer alone cause it will ask for password, so the rest will inherit the sudo session.

    # summarize results
    res: L[str] = installers_concrete.slice(start=1).apply(run_python_installer, jobs=jobs)
    console = Console()
    print("\n")
    console.rule("Same version apps")
    print(f"{res.filter(lambda x: 'same version' in x).print()}")
    print("\n")
    console.rule("Updated apps")
    print(f"{res.filter(lambda x: 'updated from' in x).print()}")
    print("\n")
    console.rule("Failed apps")
    print(f"{res.filter(lambda x: 'Failed at' in x).print()}")

    print("\n")
    print("Completed Installation".center(100, "-"))
    print("\n" * 2)
