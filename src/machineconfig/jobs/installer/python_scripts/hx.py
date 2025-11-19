"""
Installers do not add runtime files to the machine, hence this script.
"""

from machineconfig.utils.path_extended import PathExtended
from machineconfig.utils.installer_utils.installer_locator_utils import WINDOWS_INSTALL_PATH
from typing import Optional
import platform

from machineconfig.utils.installer_utils.installer_locator_utils import LINUX_INSTALL_PATH
from machineconfig.utils.installer_utils.installer_class import Installer
from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.schemas.installer.installer_types import InstallerData


LANGUAGES_SUPPORTED_GRAMMER = ["python.so", "nu.so", "bash.so", "lua.so", "powershell.so"]
config_dict: InstallerData = {
    "appName": "hx",
    "repoURL": "CMD",
    "doc": "Helix is a post-modern modal text editor.",
    "fileNamePattern": {
        "amd64": {
            "linux": "helix-{version}-x86_64-linux.tar.xz",
            "macos": "helix-{version}-x86_64-macos.tar.xz",
            "windows": "helix-{version}-x86_64-windows.zip",
        },
        "arm64": {
            "linux": "helix-{version}-arm64-linux.tar.xz",
            "macos": "helix-{version}-arm64-macos.tar.xz",
            "windows": "helix-{version}-arm64-windows.zip",
        },
    },
}


def main(installer_data: InstallerData, version: Optional[str], install_lib: bool = True):
    _ = installer_data
    console = Console()

    console.print(Panel(f"HELIX EDITOR INSTALLER 🧬\nPlatform: {platform.system()}\nVersion:  {'latest' if version is None else version}", title="Installer", expand=False))

    config_dict_copy = config_dict.copy()
    config_dict_copy["repoURL"] = "https://github.com/helix-editor/helix"
    inst = Installer(installer_data=config_dict_copy)

    print("\n📥 [Step 1/5] Downloading Helix editor...")
    downloaded, _version_to_be_installed = inst.binary_download(version=version)
    print("   ✨ Download complete.")

    print("\n🔍 [Step 2/5] Locating executable and components...")
    if platform.system() == "Windows":
        hx_file_search = downloaded.search("hx.exe", folders=False, files=True, r=True)
    else:
        hx_file_search = downloaded.search("hx", folders=False, files=True, r=True)

    if not hx_file_search:
        console.print(Panel("❌ ERROR: Could not find 'hx' executable in downloaded files.", title="Error", expand=False))
        raise FileNotFoundError(f"Could not find 'hx' executable in {downloaded.name}")

    assert len(hx_file_search) == 1, f"Expected 1 'hx' executable, found {len(hx_file_search)}"

    hx_file = hx_file_search[0]
    contrib = hx_file.parent / "contrib"
    runtime = contrib.parent / "runtime"

    if not runtime.exists():
        console.print(Panel(f"❌ ERROR: 'runtime' directory not found at expected location: {runtime}", title="Error", expand=False))
        raise FileNotFoundError(f"'runtime' directory not found at expected location: {runtime}")
    if not contrib.exists():
        console.print(Panel(f"❌ ERROR: 'contrib' directory not found at expected location: {contrib}", title="Error", expand=False))
        raise FileNotFoundError(f"'contrib' directory not found at expected location: {contrib}")
    print("   ✨ Executable and components located.")

    print("\n🗑️  [Step 3/5] Cleaning up previous installation (if any)...")
    runtime_path = PathExtended.home().joinpath(".config/helix/runtime")
    contrib_path = PathExtended.home().joinpath(".config/helix/contrib")

    print("\n📦 [Step 4/5] Installing Helix components...")
    target_config_dir = PathExtended.home().joinpath(".config/helix").expanduser()
    target_config_dir.mkdir(parents=True, exist_ok=True)

    if platform.system() in ["Linux", "Darwin"]:
        target_bin_path = PathExtended(LINUX_INSTALL_PATH) if platform.system() == "Linux" else PathExtended("/usr/local/bin")
        exe_name = "hx"
        hx_file.move(folder=target_bin_path, overwrite=True)

        # Always install contrib (regardless of install_lib flag) — treat it like the executable.
        contrib_path.delete(sure=True, verbose=False)
        contrib.move(folder=target_config_dir, overwrite=True)

        # Install runtime only if install_lib is True. When copying runtime, copy all subfolders
        # except 'grammars' (for which we only copy the specific python.so file if present).
        if install_lib:
            runtime_path.delete(sure=True, verbose=False)
            print(f"   ✨ Cleaned '{runtime_path}' and '{contrib_path}'.")
            target_runtime = target_config_dir.joinpath("runtime")
            target_runtime.mkdir(parents=True, exist_ok=True)

            # iterate runtime children and copy selectively
            for child in runtime.iterdir():
                # skip non-existent or weird entries
                if not child.exists():
                    continue
                if child.name == "grammars":
                    # copy only the specific language files from runtime/grammars if they exist
                    for a_language in LANGUAGES_SUPPORTED_GRAMMER:
                        lang_file = child.joinpath(a_language)
                        if lang_file.exists() and lang_file.is_file():
                            dest = target_runtime.joinpath("grammars")
                            lang_file.copy(folder=dest, overwrite=True)
                else:
                    # copy the whole child (file or directory) into target_runtime
                    # for directories, copy will create target_runtime/<child.name>
                    try:
                        child.copy(folder=target_runtime, overwrite=True)
                    except Exception:
                        # fallback: try copying contents if it's a directory
                        if child.is_dir():
                            for sub in child.iterdir():
                                sub.copy(folder=target_runtime.joinpath(child.name), overwrite=True)
        system_name = "Linux" if platform.system() == "Linux" else "macOS"
        console.print(
            Panel(
                f"""✅ SUCCESS | Helix editor installed successfully on {system_name}!

📂 Executable: {target_bin_path / exe_name}
🔧 Config:     {target_config_dir}""",
                title="Success",
                expand=False,
            )
        )
    elif platform.system() == "Windows":
        target_bin_path = PathExtended(WINDOWS_INSTALL_PATH)
        exe_name = "hx.exe"
        hx_file.move(folder=target_bin_path, overwrite=True)

        # Always install contrib (regardless of install_lib flag)
        contrib_path.delete(sure=True, verbose=False)
        contrib.move(folder=target_config_dir, overwrite=True)

        # Install runtime only if install_lib is True. Copy selectively as on POSIX.
        if install_lib:
            runtime_path.delete(sure=True, verbose=False)
            print(f"   ✨ Cleaned '{runtime_path}' and '{contrib_path}'.")
            target_runtime = target_config_dir.joinpath("runtime")
            target_runtime.mkdir(parents=True, exist_ok=True)

            for child in runtime.iterdir():
                if not child.exists():
                    continue
                if child.name == "grammars":
                    for a_language in LANGUAGES_SUPPORTED_GRAMMER:
                        lang_file = child.joinpath(a_language)
                        if lang_file.exists() and lang_file.is_file():
                            dest = target_runtime.joinpath("grammars")
                            lang_file.copy(folder=dest, overwrite=True)
                else:
                    try:
                        child.copy(folder=target_runtime, overwrite=True)
                    except Exception:
                        if child.is_dir():
                            for sub in child.iterdir():
                                sub.copy(folder=target_runtime.joinpath(child.name), overwrite=True)
        console.print(
            Panel(
                f"""✅ SUCCESS | Helix editor installed successfully on Windows!
📂 Executable: {target_bin_path / exe_name}
🔧 Config:     {target_config_dir}""",
                title="Success",
                expand=False,
            )
        )
    else:
        console.print(
            Panel(
                f"""⚠️ WARNING | Unsupported operating system: {platform.system()}
          | Installation aborted.""",
                title="Warning",
                expand=False,
            )
        )
        print("\n🧹 [Step 5/5] Cleaning up temporary download files...")
        downloaded.delete(sure=True)
        print("   ✨ Cleanup complete.")
        return f"Error: Unsupported OS: {platform.system()}"

    print("\n🧹 [Step 5/5] Cleaning up temporary download files...")
    downloaded.delete(sure=True)
    print("   ✨ Cleanup complete.")

    console.print(Panel("🎉 Installation Finished Successfully! 🎉", title="Finished", expand=False))
    return ""


if __name__ == "__main__":
    pass
