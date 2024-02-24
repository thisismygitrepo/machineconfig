
"""lvim
"""

import platform
from typing import Optional


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
    return program


if __name__ == "__main__":
    pass
