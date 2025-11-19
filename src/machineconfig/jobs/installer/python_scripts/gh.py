"""gh-cli installer"""

import platform
import subprocess
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from machineconfig.utils.installer_utils.installer_class import Installer
from machineconfig.utils.schemas.installer.installer_types import InstallerData

r"""
https://github.com/cli/cli


# as per https://docs.github.com/en/copilot/github-copilot-in-the-cli/using-github-copilot-in-the-cli
# gh auth login
# gh extension install github/gh-copilot

# & 'C:\Program Files\GitHub CLI\gh.exe' extension install github/gh-copilot
# & 'C:\Program Files\GitHub CLI\gh.exe' extension install auth login

"""

config_dict: InstallerData = {
    "appName": "gh",
    "repoURL": "https://github.com/cli/cli",
    "doc": "GitHub CLI",
    "fileNamePattern": {"amd64": {"windows": "gh_{version}_windows_amd64.msi", "linux": "gh_{version}_linux_amd64.deb", "macos": "gh_{version}_macOS_amd64.pkg"}, "arm64": {"windows": "gh_{version}_windows_arm64.msi", "linux": "gh_{version}_linux_arm64.deb", "macos": "gh_{version}_macOS_arm64.pkg"}},
}


console = Console()


def main(version: Optional[str]):
    console.print(
        Panel.fit(
            "\n".join(
                [
                    "[bold magenta]GitHub CLI Installer[/bold magenta]",
                    f"💻 Platform: {platform.system()}",
                    f"🔄 Version: {version or 'latest'}",
                ]
            ),
            title="🔱 GitHub CLI",
            border_style="magenta",
            padding=(1, 2),
        )
    )

    _ = version
    inst = Installer(installer_data=config_dict)
    console.print("[bold cyan]📦 INSTALLATION | Installing GitHub CLI base package...[/bold cyan]")
    inst.install(version=version)

    console.print(
        Panel.fit(
            "🤖 GITHUB COPILOT | Setting up GitHub Copilot CLI extension",
            title="Extension Setup",
            border_style="cyan",
        )
    )

    if platform.system() == "Windows":
        console.print(
            Panel.fit(
                "🪟 WINDOWS SETUP | Configuring GitHub CLI for Windows...",
                border_style="blue",
                title="Platform Setup",
            )
        )
        program = "gh extension install github/gh-copilot"
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "LINUX" if platform.system() == "Linux" else "MACOS"
        console.print(
            Panel.fit(
                f"🐧 {system_name} SETUP | Configuring GitHub CLI for {platform.system()}...",
                border_style="blue",
                title="Platform Setup",
            )
        )
        program = """
gh extension install github/gh-copilot
"""
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

    program += """
gh auth login --with-token $HOME/dotfiles/creds/git/gh_token.txt
"""
    console.print("[bold]🔐 AUTHENTICATION | Setting up GitHub authentication with token...[/bold]")

    console.print("[bold]🔄 EXECUTING | Running GitHub Copilot extension installation and authentication...[/bold]")
    try:
        subprocess.run(program, shell=True, text=True, check=True)
        console.print("[green]✅ Command executed successfully[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Command failed with exit code {e.returncode}[/red]")
        raise

    console.print(
        Panel.fit(
            "\n".join(
                [
                    "✅ SUCCESS | GitHub CLI installation completed",
                    "🚀 GitHub Copilot CLI extension installed",
                    "🔑 Authentication configured with token",
                ]
            ),
            title="Installation Complete",
            border_style="green",
            padding=(1, 2),
        )
    )


if __name__ == "__main__":
    pass
