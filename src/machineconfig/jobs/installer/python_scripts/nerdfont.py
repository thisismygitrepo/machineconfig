"""Nerd Fonts installer - Cross-platform font installation"""

import platform
import subprocess
from typing import Optional
from rich import box
from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.schemas.installer.installer_types import InstallerData


def main(installer_data: InstallerData, version: Optional[str]) -> None:
    """Main entry point for Nerd Fonts installation.

    Args:
        installer_data: Installation configuration data
        version: Specific version to install (None for latest)
    """
    console = Console()
    _ = installer_data
    console.print(
        Panel.fit(
            "\n".join([f"💻 Platform: {platform.system()}", f"🔄 Version: {'latest' if version is None else version}"]),
            title="🔤 Nerd Fonts Installer",
            border_style="blue",
            box=box.ROUNDED,
        )
    )

    _ = version
    current_platform = platform.system()

    if current_platform == "Windows":
        console.print("🪟 Installing Nerd Fonts on Windows...", style="bold")
        from machineconfig.jobs.installer.python_scripts.nerfont_windows_helper import install_nerd_fonts

        try:
            install_nerd_fonts()
            console.print(
                Panel.fit(
                    "\n".join(["💡 Restart terminal applications to see the new fonts."]),
                    title="✅ Nerd Fonts Installed",
                    border_style="green",
                    box=box.ROUNDED,
                )
            )
        except Exception as e:  # noqa: BLE001
            error_msg = f"Windows Nerd Fonts installation failed: {e}"
            console.print(
                Panel.fit(
                    "\n".join(
                        [
                            error_msg,
                            "💡 Try running as administrator or install manually from https://www.nerdfonts.com",
                        ]
                    ),
                    title="❌ Error",
                    subtitle="⚠️ Installation issue",
                    border_style="red",
                    box=box.ROUNDED,
                )
            )
            raise RuntimeError(error_msg) from e

    elif current_platform in ["Linux", "Darwin"]:
        console.print(f"🐧 Installing Nerd Fonts on {current_platform} using installation script...", style="bold")
        import machineconfig.jobs.installer as module
        from pathlib import Path

        program = Path(module.__file__).parent.joinpath("linux_scripts/nerdfont.sh").read_text(encoding="utf-8")

        console.print(
            Panel.fit(
                "\n".join(
                    [
                        "🎨 Programming fonts patched with icons",
                        "🔣 Includes icons from popular sets (FontAwesome, Devicons, etc.)",
                        "🖥️  Perfect for terminals and coding environments",
                        "🧰 Works with many terminal applications and editors",
                    ]
                ),
                title="ℹ️  Nerd Fonts Features",
                border_style="magenta",
                box=box.ROUNDED,
            )
        )

        console.print("🔄 EXECUTING | Running Nerd Fonts installation...", style="bold yellow")
        try:
            subprocess.run(program, shell=True, text=True, check=True)
            console.print("✅ Nerd Fonts installation completed successfully", style="bold green")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Installation failed with exit code {e.returncode}", style="bold red")
            raise

    else:
        error_msg = f"Unsupported platform: {current_platform}"
        console.print(
            Panel.fit(
                "\n".join([error_msg, "💡 Supported platforms are Windows, Linux, and macOS (Darwin)"]),
                title="❌ Error",
                subtitle="⚠️ Unsupported platform",
                border_style="red",
                box=box.ROUNDED,
            )
        )
        raise NotImplementedError(error_msg)


if __name__ == "__main__":
    main(1, None)  # type: ignore
