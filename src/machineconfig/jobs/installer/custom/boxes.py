

import platform
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.installer_utils.installer_locator_utils import WINDOWS_INSTALL_PATH

from machineconfig.utils.installer_utils.installer_class import Installer
from machineconfig.utils.schemas.installer.installer_types import InstallerData

installer_data_modified: InstallerData = {
      "appName": "boxes",
      "repoURL": "https://github.com/ascii-boxes/boxes",
      "doc": "📦 ASCI draws boxes around text.",
      "fileNamePattern": {
        "amd64": {
          "windows": "boxes-{version}-intel-win32.zip",
          "linux": None,
          "macos": None
        },
        "arm64": {
          "linux": None,
          "macos": None,
          "windows": None
        }
      }
    }

def main(installer_data: InstallerData, version: Optional[str] = None) -> None:
    console = Console()
    _ = installer_data
    console.print(
        Panel.fit(
            "\n".join([f"🖥️  Platform: {platform.system()}", f"🔄 Version: {'latest' if version is None else version}"]),
            title="📦 Boxes Installer",
            border_style="blue",
        )
    )

    installer = Installer(installer_data=installer_data_modified)
    downloaded, _version_to_be_installed = installer.binary_download(version=version)
    decomp_path = downloaded.decompress()
    from pathlib import Path
    for item in decomp_path.rglob("*"):
        if "boxes.exe" in item.name:
            dest_exe = Path(WINDOWS_INSTALL_PATH) / "boxes.exe"
            if dest_exe.exists():
                dest_exe.unlink()
            item.rename(dest_exe)
        if "boxes.cfg" in item.name:
            dest_cfg = Path(WINDOWS_INSTALL_PATH) / "boxes.cfg"
            if dest_cfg.exists():
                dest_cfg.unlink()
            item.rename(dest_cfg)
    console.print("📦 Boxes downloaded and decompressed.", style="bold green")


if __name__ == "__main__":
    pass
