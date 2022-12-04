
# https://www.lunarvim.org/docs/installation
Invoke-WebRequest https://raw.githubusercontent.com/lunarvim/lunarvim/master/utils/installer/uninstall.ps1 -UseBasicParsing | Invoke-Expression
$LV_BRANCH='release-1.2/neovim-0.8'; Invoke-WebRequest https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/install.ps1 -UseBasicParsing | Invoke-Expression
