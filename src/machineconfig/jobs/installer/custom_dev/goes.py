"""natural language to API
https://github.com/ShishirPatil/gorilla
"""

import subprocess
from rich import box
from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.schemas.installer.installer_types import InstallerData

# config_dict: InstallerData = {
#     "appName": "Gorilla",
#     "repoURL": "https://github.com/ShishirPatil/gorilla",
#     "doc": "natural language to API",
# }

ve_name = "goex"


def main(installer_data: InstallerData) -> None:
    console = Console()
    _ = installer_data
    console.print(
        Panel.fit(
            "\n".join(
                [
                    "Natural language to API converter",
                    "🌐 Source: https://github.com/ShishirPatil/gorilla",
                    f"📦 Virtual Environment: {ve_name}",
                ]
            ),
            title="🦍 Gorilla Installer",
            border_style="blue",
            box=box.ROUNDED,
        )
    )

    console.print("🔄 Preparing installation script...", style="bold")
    install_script = """
cd ~/code/foreign
git clone https://github.com/ShishirPatil/gorilla --depth 1
cd gorilla/goex
uv sync
"""

    console.print(
        Panel.fit(
            "\n".join(
                [
                    f"1️⃣  Create Python 3.13 virtual environment: {ve_name}",
                    "2️⃣  Clone Gorilla repository to ~/code/foreign",
                    "3️⃣  Install Gorilla in development mode",
                ]
            ),
            title="📋 Installation Steps",
            subtitle="✅ Installation script prepared successfully!",
            border_style="magenta",
            box=box.ROUNDED,
        )
    )

    console.print("🔄 EXECUTING | Running Gorilla installation...", style="bold yellow")
    try:
        subprocess.run(install_script, shell=True, text=True, check=True)
        console.print("✅ Gorilla installation completed successfully", style="bold green")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Installation failed with exit code {e.returncode}", style="bold red")
        raise
