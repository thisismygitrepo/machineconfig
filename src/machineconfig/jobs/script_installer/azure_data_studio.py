
from typing import Optional
import platform


def main(version: Optional[str] = None):
    _ = version
    if platform.system() == "Linux": return f"""

curl https://azuredatastudio-update.azurewebsites.net/latest/linux-x64/stable -o ~/azuredatastudio-linux-x64.tar.gz
tar -xvf ~/azuredatastudio-linux-<version string>.tar.gz
echo 'export PATH="$PATH:~/azuredatastudio-linux-x64"' >> ~/.bashrc
source ~/.bashrc

"""
    elif platform.system() == "Windows": return "winget install -e --id Microsoft.AzureDataStudio"
    else:
        raise NotImplementedError(f"Your platform {platform.system()} is not supported!")


if __name__ == '__main__':
    pass
