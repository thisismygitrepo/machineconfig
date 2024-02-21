
import platform
from typing import Optional
from machineconfig.utils.installer import Installer
from crocodile.meta import Terminal

r"""
https://github.com/cli/cli

# as per https://docs.github.com/en/copilot/github-copilot-in-the-cli/using-github-copilot-in-the-cli
# gh auth login
# gh extension install github/gh-copilot

# & 'C:\Program Files\GitHub CLI\gh.exe' extension install github/gh-copilot
# & 'C:\Program Files\GitHub CLI\gh.exe' extension install auth login

"""

gh = {
    "repo_url": "https://github.com/cli/cli",
    "doc": "GitHub CLI",
    "filename_template_windows_amd_64": "gh_{}_windows_amd64.zip",
    "filename_template_linux_amd_64": "gh_{}_linux_amd64.tar.gz",
    "strip_v": True,
    "exe_name": "gh"
}


def main(version: Optional[str]):
    _ = version
    inst = Installer.from_dict(d=gh, name="gh")
    inst.install(version=version)
    if platform.system() == "Windows":
        program = "gh extension install github/gh-copilot"
    elif platform.system() == "Linux":
        program = """
gh extension install github/gh-copilot
"""
    else:
        raise NotImplementedError("unsupported platform")

    Terminal().run(program, shell="default")

    print("Use: gh auth login")
    print("Use: gh extension install github/gh-copilot")
    return program


if __name__ == "__main__":
    pass
