
# to get exact version of an app in winget, head to: https://winget.run
$ErrorActionPreference = "Stop"

# ================================= APPS ================================================
winget install --name "Google Chrome" --Id "Google.Chrome" --source winget --accept-package-agreements --accept-source-agreements
#winget install --name "Chrome Remote Desktop Host" --Id "Google.ChromeRemoteDesktop" --source winget
#winget search "Microsoft Teams" --Id "Microsoft.Teams" --Source winget

# productivity
winget install --name "7-zip" --Id "7zip.7zip" --source winget --accept-package-agreements --accept-source-agreements
winget install --name "Mozilla Firefox" --accept-package-agreements --accept-source-agreements
winget install --name "Mozilla Thunderbird" --accept-package-agreements --accept-source-agreements
winget install --name "Microsoft Garage Mouse without Borders" --accept-package-agreements --accept-source-agreements
#winget install --name "VLC media player" --source "winget" --accept-package-agreements --accept-source-agreements
#winget install --name "StreamlabsOBS" --Id "Streamlabs.StreamlabsOBS" --source "winget" --accept-package-agreements --accept-source-agreements
#winget install --name "sql server management studio" --Id "Microsoft.SQLServerManagementStudi" --source winget --accept-package-agreements --accept-source-agreements
#winget install --name "MiKTeX" --Id "ChristianSchenk.MiKTeX"  --source winget  # library / lanugage
#winget install --name "TexMaker" --Id "Texmaker.Texmaker" --source winget  # IDE better than simple TexWorks shipped with MikTex. IDE is basically GUI for cmd interface of Tex

#winget install --name "anaconda3"
#winget install --name miniconda3
winget install --name "notepad++" --source winget --accept-package-agreements --accept-source-agreements
winget install --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --accept-package-agreements --accept-source-agreements
# winget install --name "PyCharm Professional Edition" --accept-package-agreements --accept-source-agreements
winget install --name "PyCharm Community Edition" --Id "JetBrains.PyCharm.Community" --source winget --accept-package-agreements --accept-source-agreements
#winget install spyder

# ================================================== Shells ===========================================
$ErrorActionPreference = "Stop"  # if there is any error in any command, stop there instead of proceeding to the next.
winget install -e --id "Python.Python.3" -v "3.9.7150.0" --source winget  # from https:\\winget.run
winget install Python.Python.3 --source winget  # installs the latest.
# OR: winget install --name "Python 3" --source winget  # gives the latest python

winget install --name "Git" --Id "Git.Git" --source winget --accept-package-agreements --accept-source-agreements
#git config credential.helper store  # makes git remember credentials.
# a terminal restart of terminal is required to for git to work, or the one can update the path
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# winget install --name "PuTTY"
# winget install --name "AWS Command Line Interface"
# winget install --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --Source winget  # Terminal is is installed by default on W 11
winget install --name "Powershell" --Id "Microsoft.PowerShell" --source winget  # powershell require admin

# winget install --name "Node.js" --accept-package-agreements --accept-source-agreements
winget install --name "julia" --Id "Julialang.Julia" --source winget --accept-package-agreements --accept-source-agreements
# winget install --Id Rustlang.Rust.MSVC --source winget
# https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe
winget install --name "DB Browser for SQLite" --accept-package-agreements --accept-source-agreements
wsl --install -d Ubuntu --accept-package-agreements --accept-source-agreements

# iex ((New-Object System.Net.WebClient).DownloadString('https://git.io/JJ8R4'))  # tune machine to minimal
