"""wezterm installer"""

import platform
import subprocess
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from machineconfig.utils.schemas.installer.installer_types import InstallerData

console = Console()


def main(installer_data: InstallerData, version: Optional[str]):
    _ = installer_data
    console.print(
        Panel.fit(
            "\n".join(
                [
                    "🖥️  WEZTERM INSTALLER | Modern, GPU-accelerated terminal emulator",
                    f"💻 Platform: {platform.system()}",
                    f"🔄 Version: {version or 'latest'}",
                ]
            ),
            title="WezTerm Setup",
            border_style="magenta",
            padding=(1, 2),
        )
    )

    _ = version
    if platform.system() == "Windows":
        program = """winget install --no-upgrade --name "WezTerm"                      --Id "wez.wezterm"                --source winget --accept-package-agreements --accept-source-agreements
"""
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "LINUX" if platform.system() == "Linux" else "MACOS"
        console.print(
            Panel.fit(
                f"🐧 {system_name} SETUP | Installing WezTerm terminal emulator...",
                title="Platform Setup",
                border_style="cyan",
            )
        )
        import machineconfig.jobs.installer as module
        from pathlib import Path

        if platform.system() == "Linux":
            program = Path(module.__file__).parent.joinpath("linux_scripts/wezterm.sh").read_text(encoding="utf-8")
        else:  # Darwin/macOS
            program = "brew install --cask wezterm"
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        console.print(
            Panel.fit(
                f"❌ ERROR | {error_msg}",
                title="Unsupported Platform",
                border_style="red",
            )
        )
        raise NotImplementedError(error_msg)

    console.print(
        Panel(
            "\n".join(
                [
                    "ℹ️  INFO | WezTerm Features:",
                    "⚡ GPU-accelerated rendering",
                    "🎨 Full color emoji support",
                    "🧩 Multiplexing with panes and tabs",
                    "⚙️  Lua configuration",
                    "📦 Cross-platform support",
                    "🔌 Plugin system",
                ]
            ),
            title="Why WezTerm?",
            border_style="magenta",
            padding=(1, 2),
        )
    )

    console.print("[bold]🔄 EXECUTING | Running WezTerm installation...[/bold]")
    try:
        subprocess.run(program, shell=True, text=True, check=True)
        console.print("[green]✅ WezTerm installation completed successfully[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Installation failed with exit code {e.returncode}[/red]")
        raise


if __name__ == "__main__":
    pass
