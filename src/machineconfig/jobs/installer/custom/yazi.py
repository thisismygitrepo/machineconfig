
from typing import Optional
import platform
from machineconfig.utils.installer_utils.installer_class import Installer
from machineconfig.utils.schemas.installer.installer_types import InstallerData


installer_standard: InstallerData =    {
      "appName": "yazi",
      "repoURL": "https://github.com/sxyazi/yazi",
      "doc": "⚡ Blazing Fast Terminal File Manager.",
      "fileNamePattern": {
        "amd64": {
          "linux": "yazi-x86_64-unknown-linux-musl.zip",
          "macos": "yazi-x86_64-apple-darwin.zip",
          "windows": "yazi-x86_64-pc-windows-msvc.zip"
        },
        "arm64": {
          "linux": "yazi-aarch64-unknown-linux-musl.zip",
          "macos": "yazi-aarch64-apple-darwin.zip",
          "windows": "yazi-aarch64-pc-windows-msvc.zip"
        }
      }
    }

def main(installer_data: InstallerData, version: Optional[str]):
    _ = installer_data
    inst = Installer(installer_data=installer_standard)
    inst.install(version=version)

    from pathlib import Path
    system_name = platform.system().lower()
    home_dir = Path.home()
    if system_name == "windows":
        yazi_plugins_dir = home_dir.joinpath("AppData", "Roaming", "yazi", "config")
    else:
        yazi_plugins_dir = home_dir.joinpath(".config", "yazi")
    
    yazi_plugins_path = yazi_plugins_dir.joinpath("plugins")
    yazi_flavours_path = yazi_plugins_dir.joinpath("flavors")
    if not yazi_plugins_path.exists():
        yazi_plugins_dir.mkdir(parents=True, exist_ok=True)
        import git
        git.Repo.clone_from("https://github.com/yazi-rs/plugins", yazi_plugins_path)
    if not yazi_flavours_path.exists():
        yazi_plugins_dir.mkdir(parents=True, exist_ok=True)
        import git
        git.Repo.clone_from("https://github.com/yazi-rs/flavors", yazi_flavours_path)

    # previewers:
    if platform.system() == "Linux":
        script = r"""
sudo nala install poppler-utils -y || true  # For PDF preview, needed by yazi.
"""
        from machineconfig.utils.code import run_shell_script
        run_shell_script(script)
    elif platform.system() == "Darwin":
        script = r"""
brew install --upgrade poppler || true  # For PDF preview, needed by yazi.
"""
        from machineconfig.utils.code import run_shell_script
        run_shell_script(script)
    elif platform.system() == "Windows":
        popler_installer: InstallerData = {
            "appName": "poppler",
            "repoURL": "https://github.com/oschwartz10612/poppler-windows",
            "doc": "PDF rendering library - Windows builds.",
            "fileNamePattern": {
                "amd64": {
                    "windows": "Release-{version}.zip",
                    "linux": None,
                    "macos": None,
                },
                "arm64": {
                    "windows": None,
                    "linux": None,
                    "macos": None,
                }
            }
        }
        inst_poppler = Installer(installer_data=popler_installer)
        inst_poppler.install(version=None)

if __name__ == "__main__":
    pass
