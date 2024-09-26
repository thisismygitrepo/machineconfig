
"""
custom installer for azuredatastudio
"""

from typing import Optional
import platform

config_dict = {
        "repo_url": "CUSTOM",
        "doc": "Azure Data Studio is a data management tool that enables working with SQL Server, Azure SQL DB and SQL DW from Windows, macOS and Linux.",
        "filename_template_windows_amd_64": "AzureDataStudio-{}.exe",
        "filename_template_linux_amd_64": "azuredatastudio-{}.deb",
        "strip_v": True,
        "exe_name": "azuredatastudio"
    }


def main(version: Optional[str] = None):
    _ = version
    if platform.system() == "Linux": return """

rm -rfd $HOME/.azuredatastudio
cd $HOME/Downloads
curl -L https://azuredatastudio-update.azurewebsites.net/latest/linux-deb-x64/stable -o ./azuredatastudio-linux-x64.deb
sudo dpkg -i ./azuredatastudio-linux-x64.deb

"""
    elif platform.system() == "Windows": return "winget install -e --id Microsoft.AzureDataStudio"
    else:
        raise NotImplementedError(f"Your platform {platform.system()} is not supported!")


if __name__ == '__main__':
    pass
