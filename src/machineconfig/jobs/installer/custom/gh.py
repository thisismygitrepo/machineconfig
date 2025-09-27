"""gh-cli installer"""

import platform
import subprocess
from typing import Optional
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
    "fileNamePattern": {
        "amd64": {
            "windows": "gh_{version}_windows_amd64.msi",
            "linux": "gh_{version}_linux_amd64.deb",
            "macos": "gh_{version}_macOS_amd64.pkg",
        },
        "arm64": {
            "windows": "gh_{version}_windows_arm64.msi",
            "linux": "gh_{version}_linux_arm64.deb",
            "macos": "gh_{version}_macOS_arm64.pkg",
        },
    },
}


def main(version: Optional[str]):
    print(f"""
{"═" * 150}
🔱 GITHUB CLI INSTALLER | Command line tool for GitHub
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"═" * 150}
""")

    _ = version
    inst = Installer(installer_data=config_dict)
    print("""
📦 INSTALLATION | Installing GitHub CLI base package...
""")
    inst.install(version=version)

    print(f"""
{"─" * 150}
🤖 GITHUB COPILOT | Setting up GitHub Copilot CLI extension
{"─" * 150}
""")

    if platform.system() == "Windows":
        print("""
🪟 WINDOWS SETUP | Configuring GitHub CLI for Windows...
""")
        program = "gh extension install github/gh-copilot"
    elif platform.system() in ["Linux", "Darwin"]:
        system_name = "LINUX" if platform.system() == "Linux" else "MACOS"
        print(f"""
🐧 {system_name} SETUP | Configuring GitHub CLI for {platform.system()}...
""")
        program = """
gh extension install github/gh-copilot
"""
    else:
        error_msg = f"Unsupported platform: {platform.system()}"
        print(f"""
{"⚠️" * 20}
❌ ERROR | {error_msg}
{"⚠️" * 20}
""")
        raise NotImplementedError(error_msg)

    program += """
gh auth login --with-token $HOME/dotfiles/creds/git/gh_token.txt
"""
    print("""
🔐 AUTHENTICATION | Setting up GitHub authentication with token...
""")

    print("""
🔄 EXECUTING | Running GitHub Copilot extension installation and authentication...
""")
    try:
        subprocess.run(program, shell=True, text=True, check=True)
        print("✅ Command executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        raise

    print(f"""
{"═" * 150}
✅ SUCCESS | GitHub CLI installation completed
🚀 GitHub Copilot CLI extension installed
🔑 Authentication configured with token
{"═" * 150}
""")


if __name__ == "__main__":
    pass
