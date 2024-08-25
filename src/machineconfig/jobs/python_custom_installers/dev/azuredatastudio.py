
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
    if platform.system() == "Linux": return f"""

cd ~/Downloads
curl https://azuredatastudio-update.azurewebsites.net/latest/linux-x64/stable -o ./azuredatastudio-linux-x64.tar.gz
tar -xvf ./azuredatastudio-linux-x64.tar.gz
echo 'export PATH="$PATH:~/azuredatastudio-linux-x64"' >> ~/.bashrc
source ~/.bashrc

"""
    elif platform.system() == "Windows": return "winget install -e --id Microsoft.AzureDataStudio"
    else:
        raise NotImplementedError(f"Your platform {platform.system()} is not supported!")


if __name__ == '__main__':
    pass
