# import matplotlib.pyplot as plt

# from platform import system
from typing import Optional
from rich import box
from rich.console import Console
from rich.panel import Panel
from machineconfig.utils.schemas.installer.installer_types import InstallerData
from machineconfig.utils.path_extended import PathExtended


# config_dict: InstallerData = {
#     "appName": "bypass-paywalls-chrome",
#     "repoURL": "https://github.com/iamadamdev/bypass-paywalls-chrome",
#     "doc": """Plugin for chrome to bypass paywalls""",
# }


def main(installer_data: InstallerData, version: Optional[str] = None) -> str:
    console = Console()
    _ = installer_data
    console.print(
        Panel.fit(
            "\n".join([f"🔄 Version: {'latest' if version is None else version}"]),
            title="🔓 Bypass Paywall Installer",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    _ = version
    folder = r"C:\\"

    console.print("📥 Downloading extension from GitHub repository...", style="bold")
    PathExtended("https://github.com/iamadamdev/bypass-paywalls-chrome/archive/master.zip").download().unzip(folder=folder, content=True)
    extension_folder = PathExtended(folder).joinpath("bypass-paywalls-chrome-master")

    console.print(
        Panel.fit(
            "\n".join(
                [
                    f"📂 Location: {extension_folder}",
                    "ℹ️  Next steps:",
                    "1️⃣  Open Chrome and navigate to chrome://extensions",
                    "2️⃣  Enable Developer Mode (toggle in top right)",
                    "3️⃣  Click 'Load unpacked' and select the extension folder",
                ]
            ),
            title="✅ Extension Ready",
            border_style="green",
            box=box.ROUNDED,
        )
    )

    return ""


if __name__ == "__main__":
    pass
