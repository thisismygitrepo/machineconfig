


from machineconfig.utils.schemas.installer.installer_types import InstallerData
from typing import Optional

installer_data: InstallerData = {
      "appName": "libduckdb.so",
      "repoURL": "https://github.com/duckdb/duckdb",
      "doc": "🗃️ An in-process SQL OLAP database management system",
      "fileNamePattern": {
        "amd64": {
          "linux": "libduckdb-linux-amd64.zip",
          "macos": None,
          "windows": None
        },
        "arm64": {
          "linux": "libduckdb-linux-arm64.zip",
          "macos": None,
          "windows": None
        }
      }
    }


def main(installer_data: InstallerData, version: Optional[str]) -> None:
    _ = version
    from machineconfig.utils.installer_utils.installer_runner import Installer
    installer = Installer(installer_data)
    installer.install(version=None)
