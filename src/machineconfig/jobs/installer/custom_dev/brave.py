"""brave installer"""

import platform
import subprocess
from typing import Optional

from machineconfig.utils.schemas.installer.installer_types import InstallerData


# config_dict: InstallerData = {
#     "appName": "Brave",
#     "repoURL": "CMD",
#     "doc": "Privacy-focused web browser with built-in ad blocking",
# }


def main(installer_data: InstallerData, version: Optional[str]):
    _ = installer_data
    print(f"""
{"=" * 150}
🦁 BRAVE BROWSER | Installing privacy-focused web browser
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"=" * 150}
""")

    _ = version
    if platform.system() == "Windows":
        print("🪟 Installing Brave Browser on Windows using winget...")
        program = """

winget install --Name "Brave Browser" --Id Brave.Brave --source winget --accept-package-agreements --accept-source-agreements

"""
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "Linux" if platform.system() == "Linux" else "macOS"
        print(f"🐧 Installing Brave Browser on {system_name}...")
        import machineconfig.jobs.installer as module
        from pathlib import Path

        if platform.system() == "Linux":
            program = Path(module.__file__).parent.joinpath("linux_scripts/brave.sh").read_text(encoding="utf-8")
        else:  # Darwin/macOS
            program = "brew install --cask brave-browser"
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    print(f"""
{"=" * 150}
ℹ️  INFO | Brave Browser features:
🔒 Built-in ad blocking
🛡️ Privacy-focused browsing
💨 Faster page loading
🪙 Optional crypto rewards
{"=" * 150}
""")

    print("🔄 EXECUTING | Running Brave Browser installation...")
    try:
        subprocess.run(program, shell=True, text=True, check=True)
        print("✅ Brave Browser installation completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        raise


if __name__ == "__main__":
    pass
