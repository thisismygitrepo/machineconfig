from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.installer_utils.installer_abc import find_move_delete_linux, find_move_delete_windows
from machineconfig.utils.source_of_truth import INSTALL_TMP_DIR, INSTALL_VERSION_ROOT
from machineconfig.utils.installer_utils.installer_abc import check_tool_exists
from machineconfig.utils.schemas.installer.installer_types import InstallerData, get_os_name, get_normalized_arch

import platform
import subprocess
import json
from typing import Optional, Any
from urllib.parse import urlparse


class Installer:
    def __init__(self, installer_data: InstallerData):
        self.installer_data: InstallerData = installer_data

    def __repr__(self) -> str:
        app_name = self.installer_data["appName"]
        repo_url = self.installer_data["repoURL"]
        return f"Installer of {app_name} @ {repo_url}"

    def get_description(self) -> str:
        exe_name = self._get_exe_name()
        
        old_version_cli: bool = check_tool_exists(tool_name=exe_name)
        old_version_cli_str = "✅" if old_version_cli else "❌"
        doc = self.installer_data["doc"]
        return f"{exe_name:<12} {old_version_cli_str} {doc}"
    
    def _get_exe_name(self) -> str:
        """Derive executable name from app name by converting to lowercase and removing spaces."""
        return self.installer_data["appName"].lower().replace(" ", "")  # .replace("-", "")

    def install_robust(self, version: Optional[str]) -> str:
        try:
            exe_name = self._get_exe_name()
            result_old = subprocess.run(f"{exe_name} --version", shell=True, capture_output=True, text=True)
            old_version_cli = result_old.stdout.strip()
            print(f"🚀 INSTALLING {exe_name.upper()} 🚀. 📊 Current version: {old_version_cli or 'Not installed'}")
            self.install(version=version)
            result_new = subprocess.run(f"{exe_name} --version", shell=True, capture_output=True, text=True)
            new_version_cli = result_new.stdout.strip()
            if old_version_cli == new_version_cli:
                # print(f"ℹ️  Same version detected: {old_version_cli}")
                return f"""📦️ 😑 {exe_name}, same version: {old_version_cli}"""
            else:
                # print(f"🚀 Update successful: {old_version_cli} ➡️ {new_version_cli}")
                return f"""📦️ 🤩 {exe_name} updated from {old_version_cli} ➡️ TO ➡️  {new_version_cli}"""
        except Exception as ex:
            exe_name = self._get_exe_name()
            app_name = self.installer_data["appName"]
            print(f"❌ ERROR: Installation failed for {exe_name}: {ex}")
            return f"""📦️ ❌ Failed to install `{app_name}` with error: {ex}"""

    def install(self, version: Optional[str]) -> None:
        exe_name = self._get_exe_name()
        repo_url = self.installer_data["repoURL"]
        os_name = get_os_name()
        arch = get_normalized_arch()
        installer_arch_os = self.installer_data["fileNamePattern"][arch][os_name]
        if installer_arch_os is None:
            raise ValueError(f"No installation pattern for {exe_name} on {os_name} {arch}")
        version_to_be_installed: str = "unknown"  # Initialize to ensure it's always bound
        if repo_url == "CMD":
            if any(pm in installer_arch_os for pm in ["npm ", "pip ", "winget ", "brew ", "curl "]):
                package_manager = installer_arch_os.split(" ", maxsplit=1)[0]
                print(f"📦 Using package manager: {package_manager}")
                desc = package_manager + " installation"
                version_to_be_installed = package_manager + "Latest"
                result = subprocess.run(installer_arch_os, shell=True, capture_output=True, text=False)
                # from machineconfig.utils.code import run_shell_script
                # result = run_shell_script(installer_arch_os)
                success = result.returncode == 0 and result.stderr == "".encode()
                if not success:
                    print(f"❌ {desc} failed")
                    if result.stdout:
                        print(f"STDOUT: {result.stdout}")
                    if result.stderr:
                        print(f"STDERR: {result.stderr}")
                    print(f"Return code: {result.returncode}")
            elif installer_arch_os.endswith((".sh", ".py", ".ps1")):
                # search for the script, see which path ends with the script name
                import machineconfig.jobs.installer as module
                from pathlib import Path
                search_root = Path(module.__file__).parent
                search_results = list(search_root.rglob(installer_arch_os))
                if len(search_results) == 0:
                    raise FileNotFoundError(f"Could not find installation script: {installer_arch_os}")
                elif len(search_results) > 1:
                    raise ValueError(f"Multiple installation scripts found for {installer_arch_os}: {search_results}")
                installer_path = search_results[0]
                print(f"📄 Found installation script: {installer_path}")
                if installer_arch_os.endswith(".sh"):
                    if platform.system() not in ["Linux", "Darwin"]:
                        raise NotImplementedError(f"Shell script installation not supported on {platform.system()}")
                    subprocess.run(f"bash {installer_path}", shell=True, check=True)
                    version_to_be_installed = "scripted_installation"
                elif installer_arch_os.endswith(".ps1"):
                    if platform.system() != "Windows":
                        raise NotImplementedError(f"PowerShell script installation not supported on {platform.system()}")
                    subprocess.run(f"powershell -ExecutionPolicy Bypass -File {installer_path}", shell=True, check=True)
                    version_to_be_installed = "scripted_installation"
                elif installer_arch_os.endswith(".py"):
                    import runpy
                    runpy.run_path(str(installer_path), run_name=None)["main"](self.installer_data, version=version)
                    version_to_be_installed = str(version)
            elif installer_arch_os.startswith("https://"):  # its a url to be downloaded
                downloaded_object = PathExtended(installer_arch_os).download(folder=INSTALL_TMP_DIR)
                # object is either a zip containing a binary or a straight out binary.
                if downloaded_object.suffix in [".zip", ".tar.gz"]:
                    downloaded_object = downloaded_object.decompress()
                if downloaded_object.suffix in [".exe", ""]:  # likely an executable
                    if platform.system() == "Windows":
                        exe = find_move_delete_windows(downloaded_file_path=downloaded_object, exe_name=exe_name, delete=True, rename_to=exe_name.replace(".exe", "") + ".exe")
                    elif platform.system() in ["Linux", "Darwin"]:
                        system_name = "Linux" if platform.system() == "Linux" else "macOS"
                        print(f"🐧 Installing on {system_name}...")
                        exe = find_move_delete_linux(downloaded=downloaded_object, tool_name=exe_name, delete=True, rename_to=exe_name)
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
                    version_to_be_installed = "downloaded_binary"
            else:
                raise NotImplementedError(f"CMD installation method not implemented for: {installer_arch_os}")
        else:
            assert repo_url.startswith("https://github.com/"), f"repoURL must be a GitHub URL, got {repo_url}"
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
            else:
                if platform.system() == "Windows":
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
        INSTALL_VERSION_ROOT.joinpath(exe_name).parent.mkdir(parents=True, exist_ok=True)
        INSTALL_VERSION_ROOT.joinpath(exe_name).write_text(version_to_be_installed or "unknown", encoding="utf-8")
    def download(self, version: Optional[str]) -> tuple[PathExtended, str]:
        exe_name = self._get_exe_name()
        repo_url = self.installer_data["repoURL"]
        # app_name = self.installer_data["appName"]
        download_link: Optional[str] = None
        version_to_be_installed: Optional[str] = None
        if "github" not in repo_url or ".zip" in repo_url or ".tar.gz" in repo_url:
            # Direct download URL
            download_link = repo_url
            version_to_be_installed = "predefined_url"
            print(f"🔗 Using direct download URL: {download_link}")
            print(f"📦 Version to be installed: {version_to_be_installed}")
        else:
            # GitHub repository
            print("🌐 Retrieving release information from GitHub...")
            arch = get_normalized_arch()
            os_name = get_os_name()
            print(f"🧭 Detected system={os_name} arch={arch}")
            # Use existing get_github_release method to get download link and version
            download_link, version_to_be_installed = self.get_github_release(repo_url, version)
            if download_link is None:
                raise ValueError(f"Could not retrieve download link for {exe_name} version {version or 'latest'}")
            print(f"📦 Version to be installed: {version_to_be_installed}")
            print(f"🔗 Download URL: {download_link}")
        assert download_link is not None, "download_link must be set"
        assert version_to_be_installed is not None, "version_to_be_installed must be set"
        downloaded = PathExtended(download_link).download(folder=INSTALL_TMP_DIR).decompress()
        return downloaded, version_to_be_installed

    # --------------------------- Arch / template helpers ---------------------------

    @staticmethod
    def _get_repo_name_from_url(repo_url: str) -> str:
        """Extract owner/repo from GitHub URL."""
        try:
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip("/").split("/")
            return f"{path_parts[0]}/{path_parts[1]}"
        except (IndexError, AttributeError):
            return ""

    @staticmethod
    def _fetch_github_release_data(repo_name: str, version: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Fetch release data from GitHub API using requests."""
        import requests
        
        try:
            if version and version.lower() != "latest":
                # Fetch specific version
                url = f"https://api.github.com/repos/{repo_name}/releases/tags/{version}"
            else:
                # Fetch latest release
                url = f"https://api.github.com/repos/{repo_name}/releases/latest"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch data for {repo_name}: HTTP {response.status_code}")
                return None
                
            response_data = response.json()
            
            # Check if API returned an error
            if "message" in response_data:
                if "API rate limit exceeded" in response_data.get("message", ""):
                    print(f"🚫 Rate limit exceeded for {repo_name}")
                    return None
                elif "Not Found" in response_data.get("message", ""):
                    print(f"🔍 No releases found for {repo_name}")
                    return None
                    
            return response_data
            
        except (requests.RequestException, requests.Timeout, json.JSONDecodeError) as e:
            print(f"❌ Error fetching {repo_name}: {e}")
            return None

    def get_github_release(self, repo_url: str, version: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """
        Get download link and version from GitHub release based on fileNamePattern.
        Returns (download_url, actual_version)
        """
        arch = get_normalized_arch()
        os_name = get_os_name()
        filename_pattern = self.installer_data["fileNamePattern"][arch][os_name]
        if filename_pattern is None:
            raise ValueError(f"No fileNamePattern for {self._get_exe_name()} on {os_name} {arch}")
        repo_name = self._get_repo_name_from_url(repo_url)
        if not repo_name:
            print(f"❌ Invalid repository URL: {repo_url}")
            return None, None
        release_data = self._fetch_github_release_data(repo_name, version)
        if not release_data:
            return None, None        
        # print(release_data)
        actual_version = release_data.get("tag_name", "unknown")
        filename = filename_pattern.format(version=actual_version)

        available_filenames: list[str] = []
        for asset in release_data.get("assets", []):
            an_dl = asset.get("browser_download_url", "NA")
            available_filenames.append(an_dl.split("/")[-1])
        if filename not in available_filenames:
            candidates = [
                filename,
                filename_pattern.format(version=actual_version),
                filename_pattern.format(version=actual_version.replace("v", "")),
            ]

            # Include hyphen/underscore variants
            variants = []
            for f in candidates:
                variants += [f, f.replace("-", "_"), f.replace("_", "-")]

            for f in variants:
                if f in available_filenames:
                    filename = f
                    break
            else:
                print(f"❌ Filename not found in assets. Tried: {variants}\nAvailable: {available_filenames}")
                return None, None
        browser_download_url = f"{repo_url}/releases/download/{actual_version}/{filename}"
        return browser_download_url, actual_version
