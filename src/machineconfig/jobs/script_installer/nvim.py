


"""nvim
"""


import platform
from typing import Optional


def main(version: Optional[str]):
    _ = version
    if platform.system() == "Windows":
        program = """
winget install --no-upgrade --name "Neovim" --Id Neovim.Neovim --source winget --accept-package-agreements --accept-source-agreements
"""
    elif platform.system() == "Linux":
        # as per https://ngrok.com/docs/getting-started/?os=linux
        program = """
mkdir $HOME/tmp_install -p || true
mkdir $HOME/.local/share -p || true
cd $HOME/tmp_install || true
wget https://github.com/neovim/neovim/releases/download/stable/nvim-linux64.tar.gz || true
tar -xvf nvim-linux64.tar.gz  -C $HOME/.local/share/ || true
sudo cp ~/.local/share/nvim-linux64/bin/nvim /usr/local/bin/nvim || true
"""
        _ = program
        program = ""
    else:
        raise NotImplementedError("unsupported platform")
    return program


if __name__ == "__main__":
    pass
