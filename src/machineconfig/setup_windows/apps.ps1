
# to get exact version of an app in winget, head to: https://winget.run
$ErrorActionPreference = "Stop"

# ================================= APPS ================================================
winget install --no-upgrade --name "Google Chrome" --Id "Google.Chrome" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "Chrome Remote Desktop Host" --Id "Google.ChromeRemoteDesktop" --source winget
#winget search "Microsoft Teams" --Id "Microsoft.Teams" --Source winget
#winget install --no-upgrade --name Zoom --Id Zoom.Zoom --source winget

# productivity
winget install --no-upgrade --name "7-zip" --Id "7zip.7zip" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "Adobe Acrobat Reader DC" --source winget
#winget install --no-upgrade --name "Mozilla Firefox" --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "Mozilla Thunderbird" --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "Microsoft Garage Mouse without Borders" --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --Id "Streamlabs.StreamlabsOBS" --source "winget" --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --Id "OBSProject.OBSStudio" --source "winget" --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "MiKTeX --Id "MiKTeX.MiKTeX"  --source winget  # library / lanugage
#winget install --no-upgrade --name "TexMaker" --Id "Texmaker.Texmaker" --source winget  # IDE better than simple TexWorks shipped with MikTex. IDE is basically GUI for cmd interface of Tex

#winget install --no-upgrade --name "anaconda3"
#winget install --no-upgrade --name miniconda3
winget install --no-upgrade --name "notepad++" --source winget --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --accept-package-agreements --accept-source-agreements
# winget install --no-upgrade --name "PyCharm Professional Edition" --accept-package-agreements --accept-source-agreements
# winget install --no-upgrade --name "PyCharm Community Edition" --Id "JetBrains.PyCharm.Community" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade spyder
winget install --no-upgrade --name "DB Browser for SQLite" --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "sql server management studio" --Id "Microsoft.SQLServerManagementStudi" --source winget --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --Id UB-Mannheim.TesseractOCR
# sudo apt install tesseract-ocr


# ================================================== Shells ===========================================
# Install icons
Install-Module -Name Terminal-Icons -Repository PSGallery
# Install oh-my-posh
winget install --no-upgrade --name "Oh My Posh" --Id "JanDeDobbeleer.OhMyPosh" --source winget

$ErrorActionPreference = "Stop"  # if there is any error in any command, stop there instead of proceeding to the next.
winget install --no-upgrade --id Python.Python.3.9 --source winget  # from https:\\winget.run  Python.Python.3.9
winget install --no-upgrade --id Python.Python.3.10 --source winget
winget install --no-upgrade --name "Git" --Id "Git.Git" --source winget --accept-package-agreements --accept-source-agreements
# the two above require Restart-Computer -Force before they are available in PATH, OR:
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
winget install --no-upgrade gitui
winget install sharkdp.hyperfine  # benchmarking tool

# github.com/ajeetdsouza/zoxide#installation
echo "Installing zoxide must be done with non-admin privliage"
curl.exe -A "MS" https://webinstall.dev/zoxide | powershell

# winget install --no-upgrade --name "AWS Command Line Interface"
# winget install --no-upgrade --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --Source winget  # Terminal is is installed by default on W11
winget install --no-upgrade nushell  # add to userpath C:\Program Files\nu\bin, done in symlinks
winget install --no-upgrade --name "Powershell" --Id "Microsoft.PowerShell" --source winget  # powershell require admin


# ======================== DEV TOOLS =================================
winget install --no-upgrade xming.xming  # X11 server. you need this while using wsl with gui, otherwise plt.show() returns: ImportError: Cannot load backend 'TkAgg' which requires the 'tk' interactive framework, as 'headless' is currently running
winget isntall WinFsp.WinFsp  # required by rclone
winget install --no-upgrade --name "Node.js" --Id "OpenJS.NodeJS" --accept-package-agreements --accept-source-agreements  # ncessary for nvim plugins.
npm install sharewifi -g
npm install -g easy-sharing
npm install -g lolcatjs
npm install -g figlet-cli
winget install --no-upgrade Graphviz.Graphviz  # required by pygraphviz. Used in Base.viz_object_hirarchy and Model.plot_model()
winget install --no-upgrade WinFsp.WinFsp  # mount remote filesystems
winget install --no-upgrade SSHFS-Win.SSHFS-Win  # mount remote filesystems  # as per https://github.com/winfsp/sshfs-win   

# https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe
# installing via winget as opposoed to the installer above, causes ignoring the requirements, and not adding ~/.carog/bin to PATH.
# installing requirements first (as per the installer instructions)
winget install --no-upgrade -e --id "Microsoft.VC++2015-2022Redist-x64"
winget install --no-upgrade -e --id "Microsoft.VisualStudio.2022.BuildTools"
winget install --no-upgrade --Id Rustlang.Rustup --source winget
winget install --no-upgrade --name "julia" --Id "Julialang.Julia" --source winget --accept-package-agreements --accept-source-agreements

winget install --no-upgrade --Id Codeblocks.Codeblocks --source winget  # gives gcc compiler  # could also be provided by MSCV Build Tools
winget install --no-upgrade --Id GnuWin32.Make --source winget  # make command  # can be provided by mscv build tools.
winget install --no-upgrade GnuPG.GnuPG

winget install --no-upgrade --Id Clement.bottom --source winget --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --Name onefetch --Id o2sh.onefech --source winget  # repo-version of system neofetch, see also tokei

# ======================= Terminal-based editors =================================
winget install --no-upgrade --Id Lapce.Lapce  # app variant of helix
winget install --no-upgrade --Id Neovim.Neovim --source winget --accept-package-agreements --accept-source-agreements
Invoke-WebRequest "https://spacevim.org/install.cmd" -OutFile "~/Downloads/spacevim_installer.cmd"
~/Downloads/spacevim_installer.cmd
# https://nvchad.com/quickstart/install

winget install --no-upgrade --Id "Canonical.Ubuntu.2204" --accept-package-agreements --accept-source-agreements
# iex ((New-Object System.Net.WebClient).DownloadString('https://git.io/JJ8R4'))  # tune machine to minimal
Install-Module -Name PSFzf  -SkipPublisherCheck -AcceptLicense -PassThru -Confirm  #  -RequiredVersion 2.5.10
Write-Output "Finished installing apps"

