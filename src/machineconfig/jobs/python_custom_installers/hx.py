"""
Installers do not add runtime files to the machine, hence this script.
"""

from machineconfig.utils.path_reduced import PathExtended as PathExtended
from machineconfig.utils.installer_utils.installer_abc import WINDOWS_INSTALL_PATH
from typing import Optional
import platform

from machineconfig.utils.installer_utils.installer_abc import LINUX_INSTALL_PATH
from machineconfig.utils.installer_utils.installer_class import Installer
from rich.console import Console
from rich.panel import Panel


config_dict = {
    "repo_url": "CUSTOM",
    "doc": "Helix is a post-modern modal text editor.",
    "filename_template_windows_amd_64": "helix-{}-x86_64-windows.zip",
    "filename_template_linux_amd_64": "helix-{}-x86_64-linux.tar.xz",
    "strip_v": False,
    "exe_name": "hx",
}


def main(version: Optional[str], install_lib: bool = False):
    console = Console()

    console.print(Panel(f"HELIX EDITOR INSTALLER 🧬\nPlatform: {platform.system()}\nVersion:  {'latest' if version is None else version}", title="Installer", expand=False))

    config_dict_copy = config_dict.copy()
    config_dict_copy["repo_url"] = "https://github.com/helix-editor/helix"
    inst = Installer.from_dict(d=config_dict_copy, name="hx")

    print("\n📥 [Step 1/5] Downloading Helix editor...")
    downloaded, _version_to_be_installed = inst.download(version=version)
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
    runtime_path.delete(sure=True, verbose=False)
    contrib_path.delete(sure=True, verbose=False)
    print(f"   ✨ Cleaned '{runtime_path}' and '{contrib_path}'.")

    print("\n📦 [Step 4/5] Installing Helix components...")
    target_config_dir = PathExtended("~/.config/helix").expanduser()
    target_config_dir.mkdir(parents=True, exist_ok=True)

    if platform.system() in ["Linux", "Darwin"]:
        target_bin_path = PathExtended(LINUX_INSTALL_PATH) if platform.system() == "Linux" else PathExtended("/usr/local/bin")
        exe_name = "hx"
        hx_file.move(folder=target_bin_path, overwrite=True)
        if install_lib:
            contrib.move(folder=target_config_dir, overwrite=True)
            runtime.move(folder=target_config_dir, overwrite=True)
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
        if install_lib:
            contrib.move(folder=target_config_dir, overwrite=True)
            runtime.move(folder=target_config_dir, overwrite=True)
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
    main(version=None)
