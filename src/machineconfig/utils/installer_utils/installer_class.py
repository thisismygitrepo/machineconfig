from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.installer_utils.installer_abc import find_move_delete_linux, find_move_delete_windows
from machineconfig.utils.source_of_truth import INSTALL_TMP_DIR, INSTALL_VERSION_ROOT, LIBRARY_ROOT
from machineconfig.utils.options import check_tool_exists
from machineconfig.utils.utils2 import read_json
from machineconfig.utils.schemas.installer.installer_types import InstallerData, InstallerDataFiles

import platform
import subprocess
from typing import Optional
from pathlib import Path


class Installer:
    def __init__(self, installer_data: InstallerData):
        self.installer_data: InstallerData = installer_data

    def __repr__(self) -> str:
        exe_name = self.installer_data.get("exeName", "unknown")
        app_name = self.installer_data.get("appName", "unknown")
        repo_url = self.installer_data.get("repoURL", "unknown")
        return f"Installer of {exe_name} {app_name} @ {repo_url}"

    def get_description(self):
        # old_version_cli = Terminal().run(f"{self.exe_name} --version").op.replace("\n", "")
        # old_version_cli = os.system(f"{self.exe_name} --version").replace("\n", "")
        exe_name = self.installer_data.get("exeName", "")
        if not exe_name:
            return "Invalid installer: missing exeName"

        old_version_cli: bool = check_tool_exists(tool_name=exe_name)
        old_version_cli_str = "✅" if old_version_cli else "❌"
        # name_version = f"{self.exe_name} {old_version_cli_str}"
        doc = self.installer_data.get("doc", "No description")
        return f"{exe_name:<12} {old_version_cli_str} {doc}"

    @staticmethod
    def choose_app_and_install():
        print(f"\n{'=' * 80}\n🔍 SELECT APPLICATION TO INSTALL 🔍\n{'=' * 80}")
        from machineconfig.utils.options import choose_one_option

        print("📂 Searching for configuration files...")
        jobs_dir = Path(LIBRARY_ROOT.joinpath("jobs"))
        config_paths = [Path(p) for p in jobs_dir.rglob("config.json")]
        path = choose_one_option(options=config_paths)
        print(f"📄 Loading configuration from: {path}")
        config_data = read_json(path)
        installer_data_files = InstallerDataFiles(config_data)

        # Extract app names from the installers
        app_names = [installer["appName"] for installer in installer_data_files["installers"]]
        print("🔍 Select an application to install:")
        app_name = choose_one_option(options=app_names, fzf=True)

        # Find the selected installer data
        selected_installer_data = None
        for installer_data in installer_data_files["installers"]:
            if installer_data["appName"] == app_name:
                selected_installer_data = installer_data
                break

        if selected_installer_data is None:
            raise ValueError(f"Could not find installer data for {app_name}")

        installer = Installer(installer_data=selected_installer_data)
        print(f"📦 Selected application: {selected_installer_data.get('exeName', 'unknown')}")
        version = input(f"📝 Enter version to install for {selected_installer_data.get('exeName', 'unknown')} [latest]: ") or None
        print(f"\n{'=' * 80}\n🚀 INSTALLING {selected_installer_data.get('exeName', 'UNKNOWN').upper()} 🚀\n{'=' * 80}")
        installer.install(version=version)

    def install_robust(self, version: Optional[str]):
        try:
            exe_name = self.installer_data.get("exeName", "unknown")
            print(f"\n{'=' * 80}\n🚀 INSTALLING {exe_name.upper()} 🚀\n{'=' * 80}")
            result_old = subprocess.run(f"{exe_name} --version", shell=True, capture_output=True, text=True)
            old_version_cli = result_old.stdout.strip()
            print(f"📊 Current version: {old_version_cli or 'Not installed'}")

            self.install(version=version)

            result_new = subprocess.run(f"{exe_name} --version", shell=True, capture_output=True, text=True)
            new_version_cli = result_new.stdout.strip()
            print(f"📊 New version: {new_version_cli}")

            if old_version_cli == new_version_cli:
                print(f"ℹ️  Same version detected: {old_version_cli}")
                return f"""📦️ 😑 {exe_name}, same version: {old_version_cli}"""
            else:
                print(f"🚀 Update successful: {old_version_cli} ➡️ {new_version_cli}")
                return f"""📦️ 🤩 {exe_name} updated from {old_version_cli} ➡️ TO ➡️  {new_version_cli}"""

        except Exception as ex:
            exe_name = self.installer_data.get("exeName", "unknown")
            app_name = self.installer_data.get("appName", "unknown")
            print(f"❌ ERROR: Installation failed for {exe_name}: {ex}")
            return f"""📦️ ❌ Failed to install `{app_name}` with error: {ex}"""

    def install(self, version: Optional[str]):
        exe_name = self.installer_data.get("exeName", "unknown")
        repo_url = self.installer_data.get("repoURL", "")

        print(f"\n{'=' * 80}\n🔧 INSTALLATION PROCESS: {exe_name} 🔧\n{'=' * 80}")
        if repo_url == "CUSTOM":
            print(f"🧩 Using custom installer for {exe_name}")
            import machineconfig.jobs.python_custom_installers as python_custom_installers

            installer_path = Path(python_custom_installers.__file__).parent.joinpath(exe_name + ".py")
            if not installer_path.exists():
                installer_path = Path(python_custom_installers.__file__).parent.joinpath("dev", exe_name + ".py")
                print(f"🔍 Looking for installer in dev folder: {installer_path}")
            else:
                print(f"🔍 Found installer at: {installer_path}")

            import runpy

            print(f"⚙️  Executing function 'main' from '{installer_path}'...")
            program: str = runpy.run_path(str(installer_path), run_name=None)["main"](version=version)
            # print(program)
            print("🚀 Running installation script...")
            if platform.system() == "Linux":
                script = "#!/bin/bash" + "\n" + program
            else:
                script = program
            script_file = PathExtended.tmpfile(name="tmp_shell_script", suffix=".ps1" if platform.system() == "Windows" else ".sh", folder="tmp_scripts")
            script_file.write_text(script, newline=None if platform.system() == "Windows" else "\n")
            if platform.system() == "Windows":
                start_cmd = "powershell"
                full_command = f"{start_cmd} {script_file}"
            else:
                start_cmd = "bash"
                full_command = f"{start_cmd} {script_file}"
            subprocess.run(full_command, stdin=None, stdout=None, stderr=None, shell=True, text=True)
            version_to_be_installed = str(version)
            print(f"✅ Custom installation completed\n{'=' * 80}")

        elif "npm " in repo_url or "pip " in repo_url or "winget " in repo_url:
            package_manager = repo_url.split(" ", maxsplit=1)[0]
            print(f"📦 Using package manager: {package_manager}")
            desc = package_manager + " installation"
            version_to_be_installed = package_manager + "Latest"
            print(f"🚀 Running: {repo_url}")
            result = subprocess.run(repo_url, shell=True, capture_output=True, text=True)
            success = result.returncode == 0 and result.stderr == ""
            if not success:
                print(f"❌ {desc} failed")
                if result.stdout:
                    print(f"STDOUT: {result.stdout}")
                if result.stderr:
                    print(f"STDERR: {result.stderr}")
                print(f"Return code: {result.returncode}")
            print(f"✅ Package manager installation completed\n{'=' * 80}")

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
                print(f"✅ DEB package installation completed\n{'=' * 80}")
            else:
                if platform.system() == "Windows":
                    print("🪟 Installing on Windows...")
                    exe = find_move_delete_windows(downloaded_file_path=downloaded, exe_name=exe_name, delete=True, rename_to=exe_name.replace(".exe", "") + ".exe")
                elif platform.system() in ["Linux", "Darwin"]:
                    system_name = "Linux" if platform.system() == "Linux" else "macOS"
                    print(f"🐧 Installing on {system_name}...")
                    exe = find_move_delete_linux(downloaded=downloaded, tool_name=exe_name, delete=True, rename_to=exe_name)
                else:
                    error_msg = f"❌ ERROR: System {platform.system()} not supported"
                    print(error_msg)
                    raise NotImplementedError(error_msg)

                _ = exe
                if exe.name.replace(".exe", "") != exe_name.replace(".exe", ""):
                    from rich import print as pprint
                    from rich.panel import Panel

                    print("⚠️  Warning: Executable name mismatch")
                    pprint(Panel(f"Expected exe name: [red]{exe_name}[/red] \nAttained name: [red]{exe.name.replace('.exe', '')}[/red]", title="exe name mismatch", subtitle=repo_url))
                    new_exe_name = exe_name + ".exe" if platform.system() == "Windows" else exe_name
                    print(f"🔄 Renaming to correct name: {new_exe_name}")
                    exe.with_name(name=new_exe_name, inplace=True, overwrite=True)

        print(f"💾 Saving version information to: {INSTALL_VERSION_ROOT.joinpath(exe_name)}")
        INSTALL_VERSION_ROOT.joinpath(exe_name).parent.mkdir(parents=True, exist_ok=True)
        INSTALL_VERSION_ROOT.joinpath(exe_name).write_text(version_to_be_installed, encoding="utf-8")
        print(f"✅ Installation completed successfully!\n{'=' * 80}")

    def download(self, version: Optional[str]):
        exe_name = self.installer_data.get("exeName", "unknown")
        repo_url = self.installer_data.get("repoURL", "")
        app_name = self.installer_data.get("appName", "unknown")
        strip_v = self.installer_data.get("stripVersion", False)

        print(f"\n{'=' * 80}\n📥 DOWNLOADING: {exe_name} 📥\n{'=' * 80}")
        download_link: Optional[Path] = None
        version_to_be_installed: Optional[str] = None
        if "github" not in repo_url or ".zip" in repo_url or ".tar.gz" in repo_url:
            download_link = Path(repo_url)
            version_to_be_installed = "predefined_url"
            print(f"🔗 Using direct download URL: {download_link}")
            print(f"📦 Version to be installed: {version_to_be_installed}")
        elif self._any_direct_http_template():
            template, arch = self._select_template()
            if not template.startswith("http"):
                # Fall back to github-style handling below
                pass
            else:
                download_link = Path(template)
                version_to_be_installed = "predefined_url"
                system_name = self._system_name()
                print(f"🧭 Detected system={system_name} arch={arch}")
                print(f"🔗 Using architecture-specific direct URL: {download_link}")
                print(f"📦 Version to be installed: {version_to_be_installed}")
                # continue to unified download logic below

        else:
            print("🌐 Retrieving release information from GitHub...")
            release_url, version_to_be_installed = Installer.get_github_release(repo_url=repo_url, version=version)
            print(f"📦 Version to be installed: {version_to_be_installed}")
            print(f"📦 Release URL: {release_url}")

            version_to_be_installed_stripped = version_to_be_installed.replace("v", "") if strip_v else version_to_be_installed
            version_to_be_installed_stripped = version_to_be_installed_stripped.replace("ipinfo-", "")

            template, arch = self._select_template()
            system_name = self._system_name()
            file_name = template.format(version_to_be_installed_stripped)
            print(f"🧭 Detected system={system_name} arch={arch}")
            print(f"📄 Using template: {template}")
            print(f"🗂️  Resolved file name: {file_name}")

            print(f"📄 File name: {file_name}")
            download_link = release_url.joinpath(file_name)

        assert download_link is not None, "download_link must be set"
        assert version_to_be_installed is not None, "version_to_be_installed must be set"
        print(f"📥 Downloading {app_name} from: {download_link}")
        downloaded = PathExtended(download_link).download(folder=INSTALL_TMP_DIR).decompress()
        print(f"✅ Download and extraction completed to: {downloaded}\n{'=' * 80}")
        return downloaded, version_to_be_installed

    # --------------------------- Arch / template helpers ---------------------------
    def _normalized_arch(self) -> str:
        arch_raw = platform.machine().lower()
        if arch_raw in ("x86_64", "amd64"):
            return "amd64"
        if arch_raw in ("aarch64", "arm64", "armv8", "armv8l"):
            return "arm64"
        return arch_raw

    def _system_name(self) -> str:
        sys_ = platform.system()
        if sys_ == "Darwin":
            return "macOS"
        return sys_

    def _any_direct_http_template(self) -> bool:
        filename_templates = self.installer_data.get("filenameTemplate", {})
        templates: list[str] = []

        for arch_templates in filename_templates.values():
            templates.extend([t for t in arch_templates.values() if t])

        return any(t for t in templates if t.startswith("http"))

    def _select_template(self) -> tuple[str, str]:
        sys_name = platform.system()
        arch = self._normalized_arch()

        filename_templates = self.installer_data.get("filenameTemplate", {})

        # Get templates for each architecture
        amd64_templates = filename_templates.get("amd64", {})
        arm64_templates = filename_templates.get("arm64", {})

        # mapping logic
        candidates: list[str] = []
        template: Optional[str] = None

        if sys_name == "Windows":
            if arch == "arm64" and arm64_templates.get("windows"):
                template = arm64_templates["windows"]
            else:
                template = amd64_templates.get("windows", "")
            candidates = ["arm64.windows", "amd64.windows"]
        elif sys_name == "Linux":
            if arch == "arm64" and arm64_templates.get("linux"):
                template = arm64_templates["linux"]
            else:
                template = amd64_templates.get("linux", "")
            candidates = ["arm64.linux", "amd64.linux"]
        elif sys_name == "Darwin":
            if arch == "arm64" and arm64_templates.get("macos"):
                template = arm64_templates["macos"]
            elif arch == "amd64" and amd64_templates.get("macos"):
                template = amd64_templates["macos"]
            else:
                # fallback between available mac templates
                template = arm64_templates.get("macos") or amd64_templates.get("macos") or ""
            candidates = ["arm64.macos", "amd64.macos"]
        else:
            raise NotImplementedError(f"System {sys_name} not supported")

        if not template:
            raise ValueError(f"No filename template available for system={sys_name} arch={arch}. Checked {candidates}")

        return template, arch

    @staticmethod
    def get_github_release(repo_url: str, version: Optional[str] = None):
        print(f"\n{'=' * 80}\n🔍 GITHUB RELEASE DETECTION 🔍\n{'=' * 80}")
        print(f"🌐 Inspecting releases at: {repo_url}")
        # with console.status("Installing..."):  # makes troubles on linux when prompt asks for password to move file to /usr/bin
        if version is None:
            # see this: https://api.github.com/repos/cointop-sh/cointop/releases/latest
            print("🔍 Finding latest version...")
            import requests  # https://docs.github.com/en/repositories/releasing-projects-on-github/linking-to-releases

            _latest_version = requests.get(str(repo_url) + "/releases/latest", timeout=10).url.split("/")[
                -1
            ]  # this is to resolve the redirection that occures: https://stackoverflow.com/questions/36070821/how-to-get-redirect-url-using-python-requests
            version_to_be_installed = _latest_version
            print(f"✅ Latest version detected: {version_to_be_installed}")
            # print(version_to_be_installed)
        else:
            version_to_be_installed = version
            print(f"📝 Using specified version: {version_to_be_installed}")

        release_url = Path(repo_url + "/releases/download/" + version_to_be_installed)
        print(f"🔗 Release download URL: {release_url}\n{'=' * 80}")
        return release_url, version_to_be_installed

    @staticmethod
    def check_if_installed_already(exe_name: str, version: str, use_cache: bool):
        print(f"\n{'=' * 80}\n🔍 CHECKING INSTALLATION STATUS: {exe_name} 🔍\n{'=' * 80}")
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
            if result.stdout.strip() == "":
                existing_version = None
                print("ℹ️  Could not detect installed version")
            else:
                existing_version = result.stdout.strip()
                print(f"📄 Detected installed version: {existing_version}")

        if existing_version is not None:
            if existing_version == version_to_be_installed:
                print(f"✅ {exe_name} is up to date (version {version_to_be_installed})")
                print(f"📂 Version information stored at: {INSTALL_VERSION_ROOT}")
                return ("✅ Up to date", version.strip(), version_to_be_installed.strip())
            else:
                print(f"🔄 {exe_name} needs update: {existing_version.rstrip()} → {version_to_be_installed}")
                tmp_path.write_text(version_to_be_installed, encoding="utf-8")
                return ("❌ Outdated", existing_version.strip(), version_to_be_installed.strip())
        else:
            print(f"📦 {exe_name} is not installed. Will install version: {version_to_be_installed}")
            tmp_path.write_text(version_to_be_installed, encoding="utf-8")

        print(f"{'=' * 80}")
        return ("⚠️ NotInstalled", "None", version_to_be_installed.strip())
