

import platform
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.installer_utils.installer_abc import WINDOWS_INSTALL_PATH

from machineconfig.utils.installer_utils.installer_class import Installer
from machineconfig.utils.schemas.installer.installer_types import InstallerData

installer_data: InstallerData = {
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

    installer = Installer(installer_data=installer_data)
    downloaded, _version_to_be_installed = installer.download(version=version)
    decomp_path = downloaded.decompress()
    from pathlib import Path
    for item in decomp_path.rglob("*"):
        if "boxes.exe" in item.name:
            item.rename(Path(WINDOWS_INSTALL_PATH) / "boxes.exe")
        if "boxes.cfg" in item.name:
            item.rename(Path(WINDOWS_INSTALL_PATH) / "boxes.cfg")
    console.print("📦 Boxes downloaded and decompressed.", style="bold green")
  