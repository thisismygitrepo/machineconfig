

import platform
from typing import Optional
from rich import box
from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.schemas.installer.installer_types import InstallerData


"""
    {
      "appName": "Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle",
      "repoURL": "https://github.com/microsoft/winget-cli",
      "doc": "📦 Windows Package Manager CLI",
      "fileNamePattern": {
        "amd64": {
          "linux": null,
          "windows": "Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle",
          "macos": null
        },
        "arm64": {
          "linux": null,
          "windows": "Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle",
          "macos": null
        }
      }

"""

ps1 = r"""

# if windows is missing
# download latest from cd $HOME/Downloads; d u "https://github.com/microsoft/winget-cli/releases/download/v1.12.170-preview/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
# this must be run in windows powershell, not in pwsh
# Add-AppxPackage .\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle

winget install --no-upgrade --name "Powershell"                   --Id "Microsoft.PowerShell"       --source winget --scope user --accept-package-agreements --accept-source-agreements  # powershell require admin
winget install --no-upgrade --name "Windows Terminal"             --Id "Microsoft.WindowsTerminal"  --source winget --scope user --accept-package-agreements --accept-source-agreements  # Terminal is is installed by default on W 11
winget install --no-upgrade --name "GNU Nano"                     --Id "GNU.Nano"                   --source winget --scope user --accept-package-agreements --accept-source-agreements
# --GROUP:gui:Brave+VSCode+Git+WezTerm
# --GROUP:dev2:VSRedistrib+VSBuildTools+Codeblocks+GnuWin32: Make+GnuPG+graphviz+WinFsp+SSHFS-win+xming+Node.js+Rustup+Cloudflare+Cloudflare WARP+Microsoft Garage Mouse without Borders
# --GROUP:user:nu+Chrome+ChromeRemoteDesktop+Zoom+7zip+Firefox+Thunderbird+StreamlabsOBS+OBSStudio+MiKTeX+TexMaker+notepad+++Lapce+TesseractOCR+perl+DB Browser for SQLite+sql server management studio+Adobe Acrobat Reader DC+julia+Chafa+bottom+onefetch+Just+hyperfine+AWS CLI
# Install-Module -Name Terminal-Icons -Repository PSGallery -Force -AcceptLicense -PassThru -Confirm  # -RequiredVersion 2.5.10

"""

zsh = r"""
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo "🔄 Updating Homebrew..."
brew update || true
# Note: git and nano are pre-installed on macOS, but we install via Homebrew to ensure latest versions
# brew install git || true
# brew install nano || true
# brew install curl || true
# Install NVM
if [ ! -s "$HOME/.nvm/nvm.sh" ]; then
    echo "📥 Installing NVM (Node Version Manager)..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
fi
echo "🔧 Configuring NVM environment..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
echo "📥 Installing latest Node.js..."
nvm install node || true
# brew install make
# brew install ffmpeg
# brew install openssl
echo "✅ Essential tools installation complete."
"""

bash = r"""
sudo apt update -y || true
sudo apt install nala -y || true
sudo nala install curl wget gpg lsb-release apt-transport-https -y || true
sudo nala install git net-tools htop nano -y || true
sudo nala install build-essential python3-dev -y || true  # C build toolchain: Where build-essential brings gcc, make, etc., and python3-dev ensures headers for your Python version.
# sudo nala install libssl-dev -y
# sudo nala install libaa-bin -y

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
echo "🔧 Configuring NVM environment..."
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
echo "📥 Installing latest Node.js..."
nvm install node || true

sudo nala install samba
sudo nala install fuse3 -y || true
sudo nala install nfs-common -y || true

# echo 'keyboard-configuration keyboard-configuration/layout select US English' | sudo debconf-set-selections
# echo 'keyboard-configuration keyboard-configuration/layoutcode string us' | sudo debconf-set-selections
# sudo DEBIAN_FRONTEND=noninteractive nala install -y cmatrix
# sudo nala install hollywood -y || true

# sudo nala install ffmpeg -y || true  # Required by some dev tools
# sudo nala install make -y || true  # Required by LunarVim and SpaceVim
# (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh) || true

"""


def main(installer_data: InstallerData, version: Optional[str]) -> None:
    console = Console()
    _ = installer_data
    console.print(
        Panel.fit(
            "\n".join([f"💻 Platform: {platform.system()}", f"🔄 Version: {'latest' if version is None else version}"]),
            title="🔧 ABC Installer",
            border_style="blue",
            box=box.ROUNDED,
        )
    )

    _ = version
    if platform.system() == "Windows":
        console.print("🪟 Installing ABC on Windows using winget...", style="bold")
        program = ps1
    elif platform.system() == "Linux":
        console.print("🐧 Installing ABC on Linux...", style="bold")
        program = bash
    elif platform.system() == "Darwin":
        console.print("🍎 Installing ABC on macOS...", style="bold")
        program = zsh
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        console.print(
            Panel.fit(
                "\n".join([error_msg]),
                title="❌ Error",
                subtitle="⚠️ Unsupported platform",
                border_style="red",
                box=box.ROUNDED,
            )
        )
        raise NotImplementedError(error_msg)
    from machineconfig.utils.code import print_code, run_shell_script
    print_code(code=program, lexer="shell", desc="Installation Script Preview")
    run_shell_script(program)
