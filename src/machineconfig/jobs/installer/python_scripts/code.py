"""vs code installer as per https://code.visualstudio.com/docs/setup/linux"""

from typing import Optional
import platform
import subprocess
from rich import box
from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.schemas.installer.installer_types import InstallerData


def main(installer_data: InstallerData, version: Optional[str] = None) -> None:
    console = Console()
    _ = installer_data
    console.print(
        Panel.fit(
            "\n".join([f"🖥️  Platform: {platform.system()}", f"🔄 Version: {'latest' if version is None else version}"]),
            title="💻 VS Code Installer",
            border_style="blue",
            box=box.ROUNDED,
        )
    )

    if platform.system() == "Linux":
        console.print("🐧 Installing VS Code on Linux using official script...", style="bold")
        import machineconfig.jobs.installer as module
        from pathlib import Path

        install_script = Path(module.__file__).parent.joinpath("linux_scripts/vscode.sh").read_text(encoding="utf-8")
    elif platform.system() == "Darwin":
        console.print("🍎 Installing VS Code on macOS using Homebrew...", style="bold")
        install_script = """brew install --cask visual-studio-code"""
    elif platform.system() == "Windows":
        console.print("🪟 Installing VS Code on Windows using winget...", style="bold")
        install_script = """
winget install --no-upgrade --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --scope user --accept-package-agreements --accept-source-agreements

"""
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
    _ = version

    console.print("🔄 EXECUTING | Running VS Code installation...", style="bold yellow")
    try:
        subprocess.run(install_script, shell=True, text=True, check=True)
        console.print("✅ VS Code installation completed successfully", style="bold green")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Installation failed with exit code {e.returncode}", style="bold red")
        raise


if __name__ == "__main__":
    pass
