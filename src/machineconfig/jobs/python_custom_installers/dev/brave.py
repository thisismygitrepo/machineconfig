"""brave installer"""

import platform
from typing import Optional

from machineconfig.utils.schemas.installer.installer_types import InstallerData


config_dict: InstallerData = {
    "appName": "Brave",
    "repoURL": "CUSTOM",
    "doc": "Privacy-focused web browser with built-in ad blocking",
    "filenameTemplate": {"amd64": {"windows": "", "linux": "", "macos": ""}},
    "stripVersion": False,
    "exeName": "brave",
}


def main(version: Optional[str]):
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
        import machineconfig.jobs.python_custom_installers as module
        from pathlib import Path

        if platform.system() == "Linux":
            program = Path(module.__file__).parent.joinpath("scripts/linux/brave.sh").read_text(encoding="utf-8")
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

    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    return program


if __name__ == "__main__":
    pass
