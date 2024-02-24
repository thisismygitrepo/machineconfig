
# to get exact version of an app in winget, head to: https://winget.run
# on older windows, use this to get winget for first time: Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe as per https://learn.microsoft.com/en-us/windows/package-manager/winget/
$ErrorActionPreference = "Stop"

# ================================= APPS ================================================
# winget install --no-upgrade --name "Google Chrome" --Id "Google.Chrome" --source winget --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Brave" --Id Brave.Brave --source winget
#winget install --no-upgrade --name "Chrome Remote Desktop Host" --Id "Google.ChromeRemoteDesktop" --source winget
#winget install --no-upgrade --name Zoom --Id Zoom.Zoom --source winget

# productivity
winget install --no-upgrade --name "7-zip" --Id "7zip.7zip" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "Adobe Acrobat Reader DC" --Id "dobe.Acrobat.Reader.64-bit" --source winget
#winget install --no-upgrade --name "Mozilla Firefox" --Id "Mozilla.Firefox" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "Mozilla Thunderbird" --Id "Mozilla.Thunderbird" --source winget --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Microsoft Garage Mouse without Borders" --Id "Microsoft.MouseWithoutBorders" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "StreamlabsOBS" --Id "Streamlabs.StreamlabsOBS" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "OBSStudio" --Id "OBSProject.OBSStudio" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "MiKTeX --Id "MiKTeX.MiKTeX"  --source winget  # library / lanugage
#winget install --no-upgrade --name "TexMaker" --Id "Texmaker.Texmaker" --source winget  # IDE better than simple TexWorks shipped with MikTex. IDE is basically GUI for cmd interface of Tex

#winget install --no-upgrade --name "anaconda3" --source winget
#winget install --no-upgrade --name miniconda3 --source winget
winget install --no-upgrade --name "notepad++" --Id "Notepad++.Notepad++" --source winget --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "PyCharm Professional Edition" --Id "JetBrains.PyCharm.Professional" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "PyCharm Community Edition" --Id "JetBrains.PyCharm.Community" --source winget --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "DB Browser for SQLite" --Id "DBBrowserForSQLite.DBBrowserForSQLite" --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "sql server management studio" --Id "Microsoft.SQLServerManagementStudi" --source winget --accept-package-agreements --accept-source-agreements
#winget install --no-upgrade --name "TesseractOCR" --Id UB-Mannheim.TesseractOCR

# ================================================== Shells ===========================================
# Install icons
Install-Module -Name Terminal-Icons -Repository PSGallery
winget install --no-upgrade --name "Chafa" --Id hpjansson.Chafa --source winget --accept-package-agreements --accept-source-agreements

$ErrorActionPreference = "Stop"  # if there is any error in any command, stop there instead of proceeding to the next.
winget install --no-upgrade --name "Python" --Id Python.Python.3.11 --source winget  # from https:\\winget.run  Python.Python.3.9

# the two above require Restart-Computer -Force before they are available in PATH, OR:
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
winget install --no-upgrade --name "Powershell" --Id "Microsoft.PowerShell" --source winget  # powershell require admin

# ======================= Terminal-based editors =================================
# winget install --no-upgrade --name "Lapce" --Id Lapce.Lapce  # window app variant of helix
winget install --no-upgrade --name "Neovim" --Id Neovim.Neovim --source winget --accept-package-agreements --accept-source-agreements
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
Invoke-WebRequest "https://spacevim.org/install.cmd" -OutFile "~/Downloads/spacevim_installer.cmd"
~/Downloads/spacevim_installer.cmd
# https://nvchad.com/quickstart/install

Install-Module -Name PSFzf  -SkipPublisherCheck  # -AcceptLicense -PassThru -Confirm  #  -RequiredVersion 2.5.10
winget install --no-upgrade --name "Ubuntu" --Id "Canonical.Ubuntu.2204" --source winget --accept-package-agreements --accept-source-agreements
# iex ((New-Object System.Net.WebClient).DownloadString('https://git.io/JJ8R4'))  # tune machine to minimal


# ======================== DEV TOOLS =================================
# https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe
# installing via winget as opposoed to the installer above, causes ignoring the requirements, and not adding ~/.carog/bin to PATH.
# installing requirements first (as per the installer instructions)
winget install --no-upgrade --name "VSRedistrib" --Id "Microsoft.VC++2015-2022Redist-x64" --source winget -e
winget install --no-upgrade --name "VSBuildTools" --Id "Microsoft.VisualStudio.2022.BuildTools" --source winget -e
winget install --no-upgrade --name "Rustup" --Id Rustlang.Rustup --source winget
# winget install --no-upgrade --name "julia" --Id "Julialang.Julia" --source winget --accept-package-agreements --accept-source-agreements

winget install --no-upgrade --name "Codeblocks" --Id Codeblocks.Codeblocks --source winget  # gives gcc compiler  # could also be provided by MSCV Build Tools
winget install --no-upgrade --name "GnuWin32: Make" --Id GnuWin32.Make --source winget  # make command  # can be provided by mscv build tools.
winget install --no-upgrade --name "GnuPG" GnuPG.GnuPG

# winget install --no-upgrade --name "bottom" --Id Clement.bottom --source winget --accept-package-agreements --accept-source-agreements
# Move-Item 'C:\Program Files\bottom\bin\btm.exe' $HOME\AppData\Local\Microsoft\WindowsApps\btm.exe  # move to userpath
# winget install --no-upgrade --name "onefetch" --Id o2sh.onefetch --source winget  # repo-version of system neofetch, see also tokei
# winget install --no-upgrade --name "Just" --Id Casey.Just --source winget  # commandline runner
# winget install --no-upgrade --name Cloudflare --Id Cloudflare.cloudflared --source winget
# winget install --no-upgrade --name "Cloudflare WARP" --Id "Cloudflare.Warp" --accept-package-agreements --accept-source-agreements --source winget
# winget install --no-upgrade --name "gitui" --Id gitui --source winget
# winget install --no-upgrade --name "hyperfine" --Id sharkdp.hyperfine --source winget  # benchmarking tool
# winget install --no-upgrade --name "AWS Command Line Interface"
# winget install --no-upgrade --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --Source winget  # Terminal is is installed by default on W11
# winget install --no-upgrade --name "wezterm" --Id "wez.wezterm" --source winget
# winget install --no-upgrade --name "nu" --Id "Nushell.Nushell" --source winget  # add to userpath C:\Program Files\nu\bin, done in symlinks
# winget install --no-upgrade --name "Oh My Posh" --Id "JanDeDobbeleer.OhMyPosh" --source winget
# winget install --no-upgrade --name "Starship" --Id Starship.Starship --source winget
# winget install --no-upgrade --name "Git" --Id Git.Git --source winget --accept-package-agreements --accept-source-agreements
# winget install --no-upgrade --name "GitHub CLI" --Id GitHub.cli --source winget --accept-package-agreements --accept-source-agreements
# as per https://docs.github.com/en/copilot/github-copilot-in-the-cli/using-github-copilot-in-the-cli
# & 'C:\Program Files\GitHub CLI\gh.exe' extension install github/gh-copilot auth login
# & 'C:\Program Files\GitHub CLI\gh.exe' extension install github/gh-copilot

winget install --no-upgrade --name "graphviz" --Id Graphviz.Graphviz --source winget  # required by pygraphviz. Used in Base.viz_object_hirarchy and Model.plot_model()
winget install --no-upgrade --name "WinFsp" --Id WinFsp.WinFsp --source winget  # mount remote filesystems and required by rclone
winget install --no-upgrade --name "SSHFS-win" --Id SSHFS-Win.SSHFS-Win --source winget  # mount remote filesystems  # as per https://github.com/winfsp/sshfs-win

winget install --no-upgrade --name "xming" --Id xming.xming --source winget  # X11 server. you need this while using wsl with gui, otherwise plt.show() returns: ImportError: Cannot load backend 'TkAgg' which requires the 'tk' interactive framework, as 'headless' is currently running
winget install --no-upgrade --name "Node.js" --Id "OpenJS.NodeJS" --accept-package-agreements --accept-source-agreements --source winget  # ncessary for nvim plugins.
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

npm install sharewifi -g
npm install -g easy-sharing
npm install -g lolcatjs
npm install -g figlet-cli
# npm install -g @pnp/cli-microsoft365


Write-Output "Finished installing apps"
