
from machineconfig.utils.path_reduced import P as PathExtended
from machineconfig.utils.installer_utils.installer_abc import find_move_delete_linux, find_move_delete_windows
from machineconfig.utils.utils import INSTALL_TMP_DIR, INSTALL_VERSION_ROOT, LIBRARY_ROOT, check_tool_exists
from machineconfig.utils.utils2 import pprint, read_json

import platform
import subprocess
from typing import Any, Optional
from pathlib import Path


class Installer:
    def __init__(self, repo_url: str, name: str, doc: str,
                strip_v: bool, exe_name: str,
                filename_template_windows_amd_64: str,
                filename_template_linux_amd_64: str,
                filename_template_windows_arm_64: Optional[str] = None,
                filename_template_linux_arm_64: Optional[str] = None,
                filename_template_macos_amd_64: Optional[str] = None,
                filename_template_macos_arm_64: Optional[str] = None,
                ):
        self.repo_url: str=repo_url
        self.name: str=name
        self.doc: str=doc
        self.filename_template_windows_amd_64: str=filename_template_windows_amd_64
        self.filename_template_linux_amd_64: str=filename_template_linux_amd_64
        self.filename_template_windows_arm_64: Optional[str]=filename_template_windows_arm_64
        self.filename_template_linux_arm_64: Optional[str]=filename_template_linux_arm_64
        self.filename_template_macos_amd_64: Optional[str]=filename_template_macos_amd_64
        self.filename_template_macos_arm_64: Optional[str]=filename_template_macos_arm_64
        self.strip_v: bool=strip_v
        self.exe_name: str=exe_name
    def __repr__(self) -> str: return f"Installer of {self.repo_url}"
    def get_description(self):
        # old_version_cli = Terminal().run(f"{self.exe_name} --version").op.replace("\n", "")
        # old_version_cli = os.system(f"{self.exe_name} --version").replace("\n", "")
        old_version_cli: bool=check_tool_exists(tool_name=self.exe_name)
        old_version_cli_str = "✅" if old_version_cli else "❌"
        # name_version = f"{self.exe_name} {old_version_cli_str}"
        return f"{self.exe_name:<12} {old_version_cli_str} {self.doc}"
    def to_dict(self): return self.__dict__
    @staticmethod
    def from_dict(d: dict[str, Any], name: str):
        try: return Installer(name=name, **d)
        except Exception as ex:
            pprint(d, "Installer Creation Error")
            raise ex
    @staticmethod
    def choose_app_and_install():
        print(f"\n{'='*80}\n🔍 SELECT APPLICATION TO INSTALL 🔍\n{'='*80}")
        from machineconfig.utils.utils import choose_one_option
        print("📂 Searching for configuration files...")
        jobs_dir = Path(LIBRARY_ROOT.joinpath("jobs"))
        config_paths = [Path(p) for p in jobs_dir.rglob("config.json")]
        path = choose_one_option(options=config_paths)
        print(f"📄 Loading configuration from: {path}")
        config: dict[str, Any] = read_json(path)  # /python_generic_installers/config.json"))
        print("🔍 Select an application to install:")
        app_name = choose_one_option(options=list(config.keys()), fzf=True)
        # for keys, dict_ in config.items():
        installer = Installer.from_dict(d=config[app_name], name=app_name)
        print(f"📦 Selected application: {installer.exe_name}")
        version = input(f"📝 Enter version to install for {installer.exe_name} [latest]: ") or None
        print(f"\n{'='*80}\n🚀 INSTALLING {installer.exe_name.upper()} 🚀\n{'='*80}")
        installer.install(version=version)

    def install_robust(self, version: Optional[str]):
        try:
            print(f"\n{'='*80}\n🚀 INSTALLING {self.exe_name.upper()} 🚀\n{'='*80}")
            result_old = subprocess.run(f"{self.exe_name} --version", shell=True, capture_output=True, text=True)
            old_version_cli = result_old.stdout.strip()
            print(f"📊 Current version: {old_version_cli or 'Not installed'}")

            self.install(version=version)

            result_new = subprocess.run(f"{self.exe_name} --version", shell=True, capture_output=True, text=True)
            new_version_cli = result_new.stdout.strip()
            print(f"📊 New version: {new_version_cli}")

            if old_version_cli == new_version_cli:
                print(f"ℹ️  Same version detected: {old_version_cli}")
                return f"""echo "📦️ 😑 {self.exe_name}, same version: {old_version_cli}" """
            else:
                print(f"🚀 Update successful: {old_version_cli} ➡️ {new_version_cli}")
                return f"""echo "📦️ 🤩 {self.exe_name} updated from {old_version_cli} ➡️ TO ➡️  {new_version_cli}" """

        except Exception as ex:
            print(f"❌ ERROR: Installation failed for {self.exe_name}: {ex}")
            return f"""echo "📦️ ❌ Failed to install `{self.name}` with error: {ex}" """

    def install(self, version: Optional[str]):
        print(f"\n{'='*80}\n🔧 INSTALLATION PROCESS: {self.exe_name} 🔧\n{'='*80}")
        if self.repo_url == "CUSTOM":
            print(f"🧩 Using custom installer for {self.exe_name}")
            import machineconfig.jobs.python_custom_installers as python_custom_installers
            installer_path = Path(python_custom_installers.__file__).parent.joinpath(self.exe_name + ".py")
            if not installer_path.exists():
                installer_path = Path(python_custom_installers.__file__).parent.joinpath("dev", self.exe_name + ".py")
                print(f"🔍 Looking for installer in dev folder: {installer_path}")
            else:
                print(f"🔍 Found installer at: {installer_path}")

            import runpy
            print(f"⚙️  Executing function 'main' from '{installer_path}'...")
            program: str = runpy.run_path(str(installer_path), run_name=None)['main'](version=version)
            # print(program)
            print("🚀 Running installation script...")
            if platform.system() == "Linux": script = "#!/bin/bash" + "\n" + program
            else: script = program
            script_file = PathExtended.tmpfile(name="tmp_shell_script", suffix=".ps1" if platform.system() == "Windows" else ".sh", folder="tmp_scripts").write_text(script, newline=None if platform.system() == "Windows" else "\n")
            if platform.system() == "Windows":
                start_cmd = "powershell"
                full_command = f"{start_cmd} {script_file}"
            else:
                start_cmd = "bash"
                full_command = f"{start_cmd} {script_file}"
            subprocess.run(full_command, stdin=None, stdout=None, stderr=None, shell=True, text=True)
            version_to_be_installed = str(version)
            print(f"✅ Custom installation completed\n{'='*80}")

        elif "npm " in self.repo_url or "pip " in self.repo_url or "winget " in self.repo_url:
            package_manager = self.repo_url.split(" ", maxsplit=1)[0]
            print(f"📦 Using package manager: {package_manager}")
            desc = package_manager + " installation"
            version_to_be_installed = package_manager + "Latest"
            print(f"🚀 Running: {self.repo_url}")
            result = subprocess.run(self.repo_url, shell=True, capture_output=True, text=True)
            success = result.returncode == 0 and result.stderr == ""
            if not success:
                print(f"❌ {desc} failed")
                if result.stdout:
                    print(f"STDOUT: {result.stdout}")
                if result.stderr:
                    print(f"STDERR: {result.stderr}")
                print(f"Return code: {result.returncode}")
            print(f"✅ Package manager installation completed\n{'='*80}")

        else:
            print("📥 Downloading from repository...")
            downloaded, version_to_be_installed = self.download(version=version)
            if str(downloaded).endswith(".deb"):
                print(f"📦 Installing .deb package: {downloaded}")
                assert platform.system() == "Linux"
                result = subprocess.run(f"sudo nala install -y {downloaded}", shell=True, capture_output=True, text=True)
                success = result.returncode == 0 and result.stderr == ""
                if not success:
                    desc = "Installing .deb"
                    print(f"❌ {desc} failed")
                    if result.stdout:
                        print(f"STDOUT: {result.stdout}")
                    if result.stderr:
                        print(f"STDERR: {result.stderr}")
                    print(f"Return code: {result.returncode}")
                print("🗑️  Cleaning up .deb package...")
                downloaded.delete(sure=True)
                print(f"✅ DEB package installation completed\n{'='*80}")
            else:
                if platform.system() == "Windows":
                    print("🪟 Installing on Windows...")
                    exe = find_move_delete_windows(downloaded_file_path=downloaded, exe_name=self.exe_name, delete=True, rename_to=self.exe_name.replace(".exe", "") + ".exe")
                elif platform.system() in ["Linux", "Darwin"]:
                    system_name = "Linux" if platform.system() == "Linux" else "macOS"
                    print(f"🐧 Installing on {system_name}...")
                    exe = find_move_delete_linux(downloaded=downloaded, tool_name=self.exe_name, delete=True, rename_to=self.exe_name)
                else:
                    error_msg = f"❌ ERROR: System {platform.system()} not supported"
                    print(error_msg)
                    raise NotImplementedError(error_msg)

                _ = exe
                if exe.name.replace(".exe", "") != self.exe_name.replace(".exe", ""):
                    from rich import print as pprint
                    from rich.panel import Panel
                    print("⚠️  Warning: Executable name mismatch")
                    pprint(Panel(f"Expected exe name: [red]{self.exe_name}[/red] \nAttained name: [red]{exe.name.replace('.exe', '')}[/red]", title="exe name mismatch", subtitle=self.repo_url))
                    new_exe_name = self.exe_name + ".exe" if platform.system() == "Windows" else self.exe_name
                    print(f"🔄 Renaming to correct name: {new_exe_name}")
                    exe.with_name(name=new_exe_name, inplace=True, overwrite=True)

        print(f"💾 Saving version information to: {INSTALL_VERSION_ROOT.joinpath(self.exe_name)}")
        INSTALL_VERSION_ROOT.joinpath(self.exe_name).parent.mkdir(parents=True, exist_ok=True)
        INSTALL_VERSION_ROOT.joinpath(self.exe_name).write_text(version_to_be_installed, encoding="utf-8")
        print(f"✅ Installation completed successfully!\n{'='*80}")

    def download(self, version: Optional[str]):
        print(f"\n{'='*80}\n📥 DOWNLOADING: {self.exe_name} 📥\n{'='*80}")
        if "github" not in self.repo_url or ".zip" in self.repo_url or ".tar.gz" in self.repo_url:
            download_link = Path(self.repo_url)
            version_to_be_installed = "predefined_url"
            print(f"🔗 Using direct download URL: {download_link}")
            print(f"📦 Version to be installed: {version_to_be_installed}")

        elif "http" in self.filename_template_linux_amd_64 or "http" in self.filename_template_windows_amd_64:
            if platform.system() == "Windows":
                download_link = Path(self.filename_template_windows_amd_64)
                print(f"🪟 Using Windows-specific download URL: {download_link}")
            elif platform.system() in ["Linux", "Darwin"]:
                download_link = Path(self.filename_template_linux_amd_64)
                system_name = "Linux" if platform.system() == "Linux" else "macOS"
                print(f"🐧 Using {system_name}-specific download URL: {download_link}")
            else:
                error_msg = f"❌ ERROR: System {platform.system()} not supported"
                print(error_msg)
                raise NotImplementedError(error_msg)

            version_to_be_installed = "predefined_url"

        else:
            print("🌐 Retrieving release information from GitHub...")
            release_url, version_to_be_installed = Installer.get_github_release(repo_url=self.repo_url, version=version)
            print(f"📦 Version to be installed: {version_to_be_installed}")
            print(f"📦 Release URL: {release_url}")

            version_to_be_installed_stripped = version_to_be_installed.replace("v", "") if self.strip_v else version_to_be_installed
            version_to_be_installed_stripped = version_to_be_installed_stripped.replace("ipinfo-", "")

            if platform.system() == "Windows":
                file_name = self.filename_template_windows_amd_64.format(version_to_be_installed_stripped)
                print(f"🪟 Windows file name: {file_name}")
            elif platform.system() in ["Linux", "Darwin"]:
                file_name = self.filename_template_linux_amd_64.format(version_to_be_installed_stripped)
                system_name = "Linux" if platform.system() == "Linux" else "macOS"
                print(f"🐧 {system_name} file name: {file_name}")
            else:
                error_msg = f"❌ ERROR: System {platform.system()} not supported"
                print(error_msg)
                raise NotImplementedError(error_msg)

            print(f"📄 File name: {file_name}")
            download_link = release_url.joinpath(file_name)

        print(f"📥 Downloading {self.name} from: {download_link}")
        downloaded = PathExtended(download_link).download(folder=INSTALL_TMP_DIR).decompress()
        print(f"✅ Download and extraction completed to: {downloaded}\n{'='*80}")
        return downloaded, version_to_be_installed

    @staticmethod
    def get_github_release(repo_url: str, version: Optional[str] = None):
        print(f"\n{'='*80}\n🔍 GITHUB RELEASE DETECTION 🔍\n{'='*80}")
        print(f"🌐 Inspecting releases at: {repo_url}")
        # with console.status("Installing..."):  # makes troubles on linux when prompt asks for password to move file to /usr/bin
        if version is None:
            # see this: https://api.github.com/repos/cointop-sh/cointop/releases/latest
            print("🔍 Finding latest version...")
            import requests  # https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases
            _latest_version = requests.get(str(repo_url) + "/releases/latest", timeout=10).url.split("/")[-1]  # this is to resolve the redirection that occures: https://stackoverflow.com/questions/36070821/how-to-get-redirect-url-using-python-requests
            version_to_be_installed = _latest_version
            print(f"✅ Latest version detected: {version_to_be_installed}")
            # print(version_to_be_installed)
        else:
            version_to_be_installed = version
            print(f"📝 Using specified version: {version_to_be_installed}")

        release_url = Path(repo_url + "/releases/download/" + version_to_be_installed)
        print(f"🔗 Release download URL: {release_url}\n{'='*80}")
        return release_url, version_to_be_installed

    @staticmethod
    def check_if_installed_already(exe_name: str, version: str, use_cache: bool):
        print(f"\n{'='*80}\n🔍 CHECKING INSTALLATION STATUS: {exe_name} 🔍\n{'='*80}")
        version_to_be_installed = version
        INSTALL_VERSION_ROOT.joinpath(exe_name).parent.mkdir(parents=True, exist_ok=True)
        tmp_path = INSTALL_VERSION_ROOT.joinpath(exe_name)

        if use_cache:
            print("🗂️  Using cached version information...")
            if tmp_path.exists():
                existing_version = tmp_path.read_text(encoding="utf-8").rstrip()
                print(f"📄 Found cached version: {existing_version}")
            else:
                existing_version = None
                print("ℹ️  No cached version information found")
        else:
            print("🔍 Checking installed version directly...")
            result = subprocess.run([exe_name, "--version"], check=False, capture_output=True, text=True)
            if result.stdout.strip() == '':
                existing_version = None
                print("ℹ️  Could not detect installed version")
            else:
                existing_version = result.stdout.strip()
                print(f"📄 Detected installed version: {existing_version}")

        if existing_version is not None:
            if existing_version == version_to_be_installed:
                print(f"✅ {exe_name} is up to date (version {version_to_be_installed})")
                print(f"📂 Version information stored at: {INSTALL_VERSION_ROOT}")
                return ("✅ Uptodate", version.strip(), version_to_be_installed.strip())
            else:
                print(f"🔄 {exe_name} needs update: {existing_version.rstrip()} → {version_to_be_installed}")
                tmp_path.write_text(version_to_be_installed, encoding="utf-8")
                return ("❌ Outdated", existing_version.strip(), version_to_be_installed.strip())
        else:
            print(f"📦 {exe_name} is not installed. Will install version: {version_to_be_installed}")
            tmp_path.write_text(version_to_be_installed, encoding="utf-8")

        print(f"{'='*80}")
        return ("⚠️ NotInstalled", "None", version_to_be_installed.strip())
