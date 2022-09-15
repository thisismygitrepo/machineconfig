
# to get exact version of an app in winget, head to: https://winget.run
$ErrorActionPreference = "Stop"

# ================================= APPS ================================================
winget install --name "Google Chrome" --Id "Google.Chrome" --source winget --accept-package-agreements --accept-source-agreements
#winget install --name "Chrome Remote Desktop Host" --Id "Google.ChromeRemoteDesktop" --source winget
#winget search "Microsoft Teams" --Id "Microsoft.Teams" --Source winget
#winget install --name Zoom --Id Zoom.Zoom --source winget

# productivity
#winget install --name "Adobe Acrobat Reader DC" --source winget
winget install --name "7-zip" --Id "7zip.7zip" --source winget --accept-package-agreements --accept-source-agreements
#winget install --name "Mozilla Firefox" --accept-package-agreements --accept-source-agreements
#winget install --name "Mozilla Thunderbird" --accept-package-agreements --accept-source-agreements
winget install --name "Microsoft Garage Mouse without Borders" --accept-package-agreements --accept-source-agreements
#winget install --name "StreamlabsOBS" --Id "Streamlabs.StreamlabsOBS" --source "winget" --accept-package-agreements --accept-source-agreements
#winget install --name "MiKTeX" --Id "ChristianSchenk.MiKTeX"  --source winget  # library / lanugage
#winget install --name "TexMaker" --Id "Texmaker.Texmaker" --source winget  # IDE better than simple TexWorks shipped with MikTex. IDE is basically GUI for cmd interface of Tex

#winget install --name "anaconda3"
#winget install --name miniconda3
winget install --name "notepad++" --source winget --accept-package-agreements --accept-source-agreements
winget install --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --accept-package-agreements --accept-source-agreements
# winget install --name "PyCharm Professional Edition" --accept-package-agreements --accept-source-agreements
# winget install --name "PyCharm Community Edition" --Id "JetBrains.PyCharm.Community" --source winget --accept-package-agreements --accept-source-agreements
#winget install spyder
winget install --name "DB Browser for SQLite" --accept-package-agreements --accept-source-agreements
#winget install --name "sql server management studio" --Id "Microsoft.SQLServerManagementStudi" --source winget --accept-package-agreements --accept-source-agreements

# ================================================== Shells ===========================================
$ErrorActionPreference = "Stop"  # if there is any error in any command, stop there instead of proceeding to the next.
winget install --id "Python.Python.3.9" --source winget  # from https:\\winget.run  Python.Python.3.9
winget install Python.Python.3.10 --source winget
# OR: winget install --name "Python 3" --source winget  # gives the latest python

# the two above require Restart-Computer -Force before they are available in PATH.
# iwr -useb https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim | ni "$(@($env:XDG_DATA_HOME, $env:LOCALAPPDATA)[$null -eq $env:XDG_DATA_HOME])/nvim-data/site/autoload/plug.vim" -Force

winget install --name "Git" --Id "Git.Git" --source winget --accept-package-agreements --accept-source-agreements
# a terminal restart of terminal is required to for git to work, or the one can update the path

# DONT use this line in combination with activated virtual enviroment.
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

#git config credential.helper store  # makes git remember credentials, or just link to pre-configured git config file.

# winget install --name "AWS Command Line Interface"
# winget install --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --Source winget  # Terminal is is installed by default on W 11
winget install --name "Powershell" --Id "Microsoft.PowerShell" --source winget  # powershell require admin
winget install --name "Node.js" --Id "OpenJS.NodeJS" --accept-package-agreements --accept-source-agreements  # ncessary for nvim plugins.

# https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe
# installing via winget as opposoed to the installer above, causes ignoring the requirements, and not adding ~/.carog/bin to PATH.
# installing requirements first (as per the installer instructions)
winget install -e --id "Microsoft.VC++2015-2022Redist-x64"
winget install -e --id "Microsoft.VisualStudio.2022.BuildTools"
winget install --Id Rustlang.Rust.MSVC --source winget

#winget install --name "julia" --Id "Julialang.Julia" --source winget --accept-package-agreements --accept-source-agreements
winget install --Id Codeblocks.Codeblocks --source winget  # gives gcc compiler  # could also be provided by MSCV Build Tools
winget install --Id GnuWin32.Make --source winget  # make command  # can be provided by mscv build tools.
cargo install tokei  # counts lines of code in every language.
# use release download with croshell for each of the following rust programs since compiling is very slow.
#cargo install ripgrep  # rg command
#cargo install fd-find  # fd command
#cargo install bat  # colored version of cat.
winget install --Id Clement.bottom --source winget --accept-package-agreements --accept-source-agreements
# cargo install bottom  # terminal-based htop,
winget install onefetch
# cargo install onefetch  # repo-version of system neofetch

# ======================= Terminal-based editors =================================
winget install --Id Neovim.Neovim --source winget --accept-package-agreements --accept-source-agreements
# https://github.com/LunarVim/LunarVim
Invoke-WebRequest https://raw.githubusercontent.com/LunarVim/LunarVim/master/utils/installer/install.ps1 -UseBasicParsing | Invoke-Expression
Invoke-WebRequest "https://spacevim.org/install.cmd" -OutFile "~/Downloads/spacevim_installer.cmd"
~/Downloads/spacevim_installer.cmd

wsl --install -d Ubuntu  #--accept-package-agreements --accept-source-agreements
# iex ((New-Object System.Net.WebClient).DownloadString('https://git.io/JJ8R4'))  # tune machine to minimal
echo "Finished installing apps"
