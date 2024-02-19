
"""vs code installer as per https://code.visualstudio.com/docs/setup/linux
"""

from typing import Optional
import platform

def main(version: Optional[str] = None):

    if platform.system() == 'Linux':
        code = """

sudo apt-get install wget gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg

sudo apt install apt-transport-https -y
sudo apt update
sudo apt install code -y # or code-insiders

"""

    elif platform.system() == 'Windows':
        code = "winget install -e --id Microsoft.VisualStudioCode"
    else:
        raise NotImplementedError(f"Unsupported platform: {platform.system()}")
    _ = version
    return code


if __name__ == '__main__':
    pass
