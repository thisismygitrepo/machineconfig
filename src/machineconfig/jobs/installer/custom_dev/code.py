"""vs code installer as per https://code.visualstudio.com/docs/setup/linux"""

from typing import Optional
import platform
import subprocess
from machineconfig.utils.schemas.installer.installer_types import InstallerData


def main(installer_data: InstallerData, version: Optional[str] = None):
    _ = installer_data
    print(f"""
{"=" * 150}
💻 VS CODE INSTALLER | Setting up Visual Studio Code
🖥️  Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    if platform.system() == "Linux":
        print("🐧 Installing VS Code on Linux using official script...")
        import machineconfig.jobs.installer as module
        from pathlib import Path

        install_script = Path(module.__file__).parent.joinpath("linux_scripts/vscode.sh").read_text(encoding="utf-8")
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
    
    print("🔄 EXECUTING | Running VS Code installation...")
    try:
        subprocess.run(install_script, shell=True, text=True, check=True)
        print("✅ VS Code installation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        raise


if __name__ == "__main__":
    pass
