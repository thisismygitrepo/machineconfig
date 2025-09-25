# import matplotlib.pyplot as plt

# from platform import system
from typing import Optional
from machineconfig.utils.schemas.installer.installer_types import InstallerData
from machineconfig.utils.path_reduced import PathExtended as PathExtended


config_dict: InstallerData = {
    "appName": "bypass-paywalls-chrome",
    "repoURL": "https://github.com/iamadamdev/bypass-paywalls-chrome",
    "doc": """Plugin for chrome to bypass paywalls""",
    "filenameTemplate": {"amd64": {"windows": "", "linux": "", "macos": ""}, "arm64": {"windows": "", "linux": "", "macos": ""}},
    "stripVersion": True,
    "exeName": "",
}


def main(version: Optional[str] = None):
    print(f"""
{"=" * 150}
🔓 BYPASS PAYWALL | Installing paywall bypass extension for Chrome
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    _ = version
    # see remove paywalls and enhance YT experience by Chris Titus
    folder = r"C:\\"

    print("📥 Downloading extension from GitHub repository...")
    PathExtended("https://github.com/iamadamdev/bypass-paywalls-chrome/archive/master.zip").download().unzip(folder=folder, content=True)
    extension_folder = PathExtended(folder).joinpath("bypass-paywalls-chrome-master")

    print(f"""
{"=" * 150}
✅ SUCCESS | Extension downloaded successfully
📂 Location: {extension_folder}
ℹ️  Next steps:
1️⃣  Open Chrome and navigate to chrome://extensions
2️⃣  Enable Developer Mode (toggle in top right)
3️⃣  Click "Load unpacked" and select the extension folder
{"=" * 150}
""")

    return ""


if __name__ == "__main__":
    pass
