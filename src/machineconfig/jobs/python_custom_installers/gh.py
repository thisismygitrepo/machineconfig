"""gh-cli installer"""

import platform
from typing import Optional
from machineconfig.utils.installer_utils.installer_class import Installer
from machineconfig.utils.terminal import Terminal

r"""
https://github.com/cli/cli

# as per https://docs.github.com/en/copilot/github-copilot-in-the-cli/using-github-copilot-in-the-cli
# gh auth login
# gh extension install github/gh-copilot

# & 'C:\Program Files\GitHub CLI\gh.exe' extension install github/gh-copilot
# & 'C:\Program Files\GitHub CLI\gh.exe' extension install auth login

"""

config_dict = {"repo_url": "https://github.com/cli/cli", "doc": "GitHub CLI", "filename_template_windows_amd_64": "gh_{}_windows_amd64.zip", "filename_template_linux_amd_64": "gh_{}_linux_amd64.tar.gz", "strip_v": True, "exe_name": "gh"}


def main(version: Optional[str]):
    print(f"""
{"═" * 150}
🔱 GITHUB CLI INSTALLER | Command line tool for GitHub
💻 Platform: {platform.system()}
🔄 Version: {"latest" if version is None else version}
{"═" * 150}
""")

    _ = version
    inst = Installer.from_dict(d=config_dict, name="gh")
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

    Terminal().run(program, shell="default").print(desc="Installing GitHub Copilot extension", capture=True)

    print(f"""
{"═" * 150}
✅ SUCCESS | GitHub CLI installation completed
🚀 GitHub Copilot CLI extension installed
🔑 Authentication configured with token
{"═" * 150}
""")

    return program


if __name__ == "__main__":
    pass
