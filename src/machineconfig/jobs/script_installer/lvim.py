
"""lvim
"""

from crocodile.meta import Terminal
import subprocess
import platform
from typing import Optional


_ = Terminal, subprocess
# as per https://www.lunarvim.org/docs/installation


def main(version: Optional[str]):
    _ = version
    if platform.system() == "Windows":
        program = """
pwsh -c "`$LV_BRANCH='release-1.3/neovim-0.9'; iwr https://raw.githubusercontent.com/LunarVim/LunarVim/release-1.3/neovim-0.9/utils/installer/install.ps1 -UseBasicParsing | iex"

"""
    elif platform.system() == "Linux":
        program = """

LV_BRANCH='release-1.3/neovim-0.9' bash <(curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/release-1.3/neovim-0.9/utils/installer/install.sh)

"""
    else:
        raise NotImplementedError("unsupported platform")
    # _res = Terminal(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).run_script(script=program, shell="default").print(desc="Running custom installer", capture=True)
    # run script here as it requires user input
    _ = program
    return ""


if __name__ == "__main__":
    pass
