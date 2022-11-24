
import crocodile.toolbox as tb
from platform import system
import machineconfig

# https://github.com/LunarVim/LunarVim


def main():
    if system() == "Windows":
        tb.P(r"AppData/Local/lvim").delete(sure=True)
        install_script = "$LV_BRANCH='release-1.2/neovim-0.8'; Invoke-WebRequest https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/install.ps1 -UseBasicParsing | Invoke-Expression"
        # install_script = "Invoke-WebRequest    https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/install.ps1 -UseBasicParsing | Invoke-Expression"
        uninstall_script = "Invoke-WebRequest https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/uninstall.ps1 -UseBasicParsing | Invoke-Expression"
        script = f"{uninstall_script} ; {install_script}"
        # tb.T().run(script, shell="pwsh")
        # tb.P(r"AppData/Local/lvim").joinpath("config.lua").append_text(tb.P(machineconfig.__file__).joinpath("src/machineconfig/settings/lvim_windows/config_additional.lua").read_text())
        return script
    else:
        tb.P("~/.config/lvim").delete(sure=True)
        install_script = "LV_BRANCH='release-1.2/neovim-0.8' bash <(curl -s https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/install.sh)"
        # install_script = r"bash <(curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/rolling/utils/installer/install-neovim-from-release)"
        # script = install_script
        # tb.T().run(script, shell="pwsh")
        return install_script


if __name__ == '__main__':
    main()
