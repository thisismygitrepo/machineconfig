
import crocodile.toolbox as tb
from platform import system
import machineconfig

# https://github.com/LunarVim/LunarVim
__doc__ = "Terminal text editor based on neovim"


def main(version=None):
    _ = version
    if system() == "Windows":
        tb.P.home().joinpath(r"AppData/Local/lvim").delete(sure=True)
        # tb.P.home().joinpath("AppData/Roaming/lunarvim").delete(sure=True)
        install_script = "$LV_BRANCH='release-1.2/neovim-0.8'; Invoke-WebRequest https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/install.ps1 -UseBasicParsing | Invoke-Expression"
        # install_script = "Invoke-WebRequest    https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/install.ps1 -UseBasicParsing | Invoke-Expression"
        uninstall_script = "Invoke-WebRequest https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/uninstall.ps1 -UseBasicParsing | Invoke-Expression"
        script = f"""
# uninstall then install latest stable release as per https://www.lunarvim.org/docs/installation
{uninstall_script}
{install_script}        
cd ~/AppData/Local
rm lvim -Force  # kill bad symlinks there
git clone https://github.com/ChristianChiarulli/lvim
pip install pynvim
pip install flake8
pip install black
"""
        # tb.P(r"AppData/Local/lvim").joinpath("config.lua").append_text(tb.P(machineconfig.__file__).joinpath("src/machineconfig/settings/lvim_windows/config_additional.lua").read_text())
        return script
    else:
        tb.P.home().joinpath(".config/lvim").delete(sure=True)
        install_script = f"""

# uninstall then install latest stable release:
# from https://www.lunarvim.org/docs/installation
bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/uninstall.sh)
sudo rm -rdf ~/.config/lvim || true  # kill bad symlinks there
LV_BRANCH='release-1.2/neovim-0.8' bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)
export lvim="$HOME/.local/bin/lvim"

# config from Chris
sudo rm -rdf ~/.config/lvim || true # kill bad symlinks there
cd ~/.config
git clone https://github.com/ChristianChiarulli/lvim
sudo apt install xsel

pip install pynvim
pip install flake8

#lvim --headless + 'autocmd User PackerComplete quitall' +PackerSync
# :PackerSync
# :Copilot setup

"""
        return install_script


if __name__ == '__main__':
    main()
