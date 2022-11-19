
import crocodile.toolbox as tb
from platform import system
import machineconfig

# https://github.com/LunarVim/LunarVim


def main():
    if system() == "Windows":
        tb.P(r"AppData/Local/lvim").delete(sure=True)
        install_script = "Invoke-WebRequest    https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/install.ps1 -UseBasicParsing | Invoke-Expression"
        uninstall_script = "Invoke-WebResquest https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/uninstall.ps1 -UseBasicParsing | Invoke-Expression"
        script = f"{uninstall_script} ; {install_script}"
        tb.T().run(script, shell="pwsh")
        tb.P(r"AppData/Local/lvim").joinpath("config.lua").append_text(tb.P(machineconfig.__file__).joinpath("src/machineconfig/settings/lvim_windows/config_additional.lua").read_text())
    else:
        tb.P("~/.config/lvim").delete(sure=True)
        install_script = r"bash <(curl -s https://raw.githubusercontent.com/LunarVim/LunarVim/rolling/utils/installer/install-neovim-from-release)"
        # script = install_script
        # tb.T().run(script, shell="pwsh")
        return install_script


if __name__ == '__main__':
    main()
