
"""package manager
"""
from rich.console import Console

from crocodile.file_management import P, List as L, Read, Struct
from crocodile.meta import Terminal
from machineconfig.utils.utils import INSTALL_VERSION_ROOT, INSTALL_TMP_DIR, LIBRARY_ROOT

# from dataclasses import dataclass
from typing import Optional, Any
import platform


def find_move_delete_windows(downloaded_file_path: P, exe_name: Optional[str] = None, delete: bool = True, rename_to: Optional[str] = None):
    if exe_name is not None and ".exe" in exe_name: exe_name = exe_name.replace(".exe", "")
    if downloaded_file_path.is_file():
        exe = downloaded_file_path
    else:
        if exe_name is None: exe = downloaded_file_path.search("*.exe", r=True).list[0]
        else:
            tmp = downloaded_file_path.search(f"{exe_name}.exe", r=True)
            if len(tmp) == 1: exe = tmp.list[0]
            else: exe = downloaded_file_path.search("*.exe", r=True).list[0]
        if rename_to and exe.name != rename_to:
            exe = exe.with_name(name=rename_to, inplace=True)
    exe.move(folder=P.get_env().WindowsApps, overwrite=True)  # latest version overwrites older installation.
    if delete: downloaded_file_path.delete(sure=True)
    return exe


def find_move_delete_linux(downloaded: P, tool_name: str, delete: Optional[bool] = True, rename_to: Optional[str] = None):
    if downloaded.is_file():
        exe = downloaded
    else:
        res = downloaded.search(f"*{tool_name}*", folders=False, r=True)
        if len(res) == 1: exe = res.list[0]
        else: exe = downloaded.search(tool_name, folders=False, r=True).list[0]
    if rename_to and exe.name != rename_to:
        exe = exe.with_name(name=rename_to, inplace=True)
    print(f"MOVING file `{repr(exe)}` to '/usr/local/bin'")
    exe.chmod(0o777)
    # exe.move(folder=r"/usr/local/bin", overwrite=False)
    Terminal().run(f"sudo mv {exe} /usr/local/bin/").print_if_unsuccessful(desc="MOVING executable to /usr/local/bin", strict_err=True, strict_returncode=True)
    if delete: downloaded.delete(sure=True)
    return exe


class Installer:
    def __init__(self, repo_url: str, doc: str, filename_template_windows_amd_64: str, filename_template_linux_amd_64: str, strip_v: bool, exe_name: str):
        self.repo_url = repo_url
        self.doc = doc
        self.filename_template_windows_amd_64 = filename_template_windows_amd_64
        self.filename_template_linux_amd_64 = filename_template_linux_amd_64
        self.strip_v = strip_v
        self.exe_name = exe_name
    def __repr__(self) -> str: return f"Installer of {self.repo_url}"
    def get_description(self): return f"{self.exe_name} -- {self.doc}"
    def to_dict(self): return self.__dict__
    @staticmethod
    def from_dict(d: dict[str, Any]):
        try: return Installer(**d)
        except Exception as ex:
            Struct(d).print(as_config=True)
            raise ex
    @staticmethod
    def choose_and_install():
        from machineconfig.utils.utils import choose_one_option
        path = choose_one_option(options=LIBRARY_ROOT.joinpath("jobs").search("config.json", r=True).list)
        config: dict[str, Any] = Read.json(path)  # /python_generic_installers/config.json"))
        # binary = choose_one_option(options=list(config.keys()), fzf=True)
        for binary in list(config.keys()):
            installer = Installer.from_dict(config[binary])
            installer.install(version=None)

    def install_robust(self, version: Optional[str]):
        try:
            old_version_cli = Terminal().run(f"{self.exe_name} --version", shell="powershell").op.replace("\n", "")
            self.install(version=version)
            new_version_cli = Terminal().run(f"{self.exe_name} --version", shell="powershell").op.replace("\n", "")
            if old_version_cli == new_version_cli: return f"😑 {self.exe_name}, same version: {old_version_cli}"
            else: return f"🤩 {self.exe_name} updated from {old_version_cli} === to ===> {new_version_cli}"
        except Exception as ex:
            print(ex)
            return f"Failed at {self.exe_name} with {ex}"

    def install(self, version: Optional[str]):
        if "github" not in self.repo_url or ".zip" in self.repo_url or ".tar.gz" in self.repo_url:
            download_link = P(self.repo_url)
            version_to_be_installed = "predefined_url"
        else:
            release_url, version_to_be_installed = self.get_github_release(repo_url=self.repo_url, version=version)
            version_to_be_installed_stripped = version_to_be_installed.replace("v", "") if self.strip_v else version_to_be_installed
            if platform.system() == "Windows":
                file_name = self.filename_template_windows_amd_64.format(version_to_be_installed_stripped)
            elif platform.system() == "Linux":
                file_name = self.filename_template_linux_amd_64.format(version_to_be_installed_stripped)
            else: raise NotImplementedError(f"System {platform.system()} not implemented")
            download_link = release_url.joinpath(file_name)
        print("Downloading", download_link.as_url_str())
        downloaded = download_link.download(folder=INSTALL_TMP_DIR).decompress()
        if platform.system() == "Windows": exe = find_move_delete_windows(downloaded_file_path=downloaded, exe_name=self.exe_name, delete=True, rename_to=self.exe_name + ".exe")
        elif platform.system() == "Linux": exe = find_move_delete_linux(downloaded=downloaded, tool_name=self.exe_name, delete=True, rename_to=self.exe_name)
        else: raise NotImplementedError(f"System {platform.system()} not implemented")
        if exe.name.replace(".exe", "") != self.exe_name:
            from rich import print as pprint
            from rich.panel import Panel
            pprint(Panel(f"Expected exe name, [red]{self.exe_name}! Attained name: {exe.name}", title="exe mismatch", subtitle=self.repo_url))
        INSTALL_VERSION_ROOT.joinpath(self.exe_name).create(parents_only=True).write_text(version_to_be_installed)

    @staticmethod
    def get_github_release(repo_url: str, version: Optional[str] = None):
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
        return release_url, version_to_be_installed

    @staticmethod
    def check_if_installed_already(exe_name: str, version: str):
        version_to_be_installed = version
        # existing_version_cli = Terminal().run(f"{exe_name or tool_name} --version", shell="powershell").op_if_successfull_or_default(strict_err=True, strict_returcode=True)
        tmp_path = INSTALL_VERSION_ROOT.joinpath(exe_name).create(parents_only=True)
        if tmp_path.exists(): existing_version = tmp_path.read_text().rstrip()
        else: existing_version = None

        if existing_version is not None:
            if existing_version == version_to_be_installed:
                print(f"⚠️ {exe_name} already installed at version {version_to_be_installed}. See {INSTALL_VERSION_ROOT}")
                return True
            else:
                # print(f"Latest version is {version}, logged at {tmp_path}")
                print(f"⬆️ {exe_name} installed at version {existing_version.rstrip()} --> Installing version {version_to_be_installed} ")
                tmp_path.write_text(version_to_be_installed)
        else:
            print(f"{exe_name} has no known version. Installing version `{version_to_be_installed}` ")
            tmp_path.write_text(version_to_be_installed)
        return False


def get_installed_cli_apps():
    if platform.system() == "Windows": apps = P.home().joinpath("AppData/Local/Microsoft/WindowsApps").search("*.exe", not_in=["notepad"])
    elif platform.system() == "Linux": apps = P(r"/usr/local/bin").search("*")
    else: raise NotImplementedError("Not implemented for this OS")
    apps = L([app for app in apps if app.size("kb") > 0.1 and not app.is_symlink()])  # no symlinks like paint and wsl and bash
    return apps


def get_cli_py_installers(system: str, dev: bool) -> list[Installer]:
    if system == "Windows": import machineconfig.jobs.python_windows_installers as inst
    else: import machineconfig.jobs.python_linux_installers as inst
    import machineconfig.jobs.python_generic_installers as gens
    path = P(inst.__file__).parent
    gens_path = P(gens.__file__).parent
    if dev:
        path = path.joinpath("dev")
        gens_path = gens_path.joinpath("dev")
    res1: dict[str, Any] = Read.json(path=path.joinpath("config.json"))
    res2: dict[str, Any] = Read.json(path=gens_path.joinpath("config.json"))
    res2.update(res1)
    return [Installer.from_dict(d) for d in res2.values()]


def install_all(installers: L[Installer], safe: bool = False, jobs: int = 10, fresh: bool = False):
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
    installers.list[0].install(version=None)
    res = installers.slice(start=1).apply(lambda x: x.install_robust(version=None), jobs=jobs)  # try out the first installer alone cause it will ask for password, so the rest will inherit the sudo session.
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
