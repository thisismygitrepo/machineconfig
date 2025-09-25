"""vs code installer as per https://code.visualstudio.com/docs/setup/linux"""

from typing import Optional
import platform
from machineconfig.utils.schemas.installer.installer_types import InstallerData

config_dict: InstallerData = {
    "appName": "Visual Studio Code",
    "repoURL": "CUSTOM",
    "doc": "Visual Studio Code",
    "filenameTemplate": {"amd64": {"windows": "VSCodeSetup-{}.exe", "linux": "code_{}.deb", "macos": ""}},
    "stripVersion": True,
    "exeName": "code",
}


def main(version: Optional[str] = None):
    print(f"""
{"=" * 150}
💻 VS CODE INSTALLER | Setting up Visual Studio Code
🖥️  Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    if platform.system() == "Linux":
        print("🐧 Installing VS Code on Linux using official script...")
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path

        install_script = Path(module.__file__).parent.joinpath("scripts/linux/vscode.sh").read_text(encoding="utf-8")
    elif platform.system() == "Darwin":
        print("🍎 Installing VS Code on macOS using Homebrew...")
        install_script = """brew install --cask visual-studio-code"""
    elif platform.system() == "Windows":
        print("🪟 Installing VS Code on Windows using winget...")
        install_script = """winget install --no-upgrade --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --scope user --accept-package-agreements --accept-source-agreements"""
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)
    _ = version
    return install_script


if __name__ == "__main__":
    pass
