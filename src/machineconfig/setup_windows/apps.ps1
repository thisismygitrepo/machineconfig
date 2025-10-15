
# to get exact version of an app in winget, head to: https://winget.run

# --GROUP:ESSENTIAL_SYSTEM:WT+Brave+VSCode+WezTerm+OhMyPosh+Powershell+Starship+Git+Neovim+GNU Nano+Terminal-Icons+PSFzf
winget install --no-upgrade --name "Windows Terminal"             --Id "Microsoft.WindowsTerminal"  --source winget --scope user --accept-package-agreements --accept-source-agreements  # Terminal is is installed by default on W 11
winget install --no-upgrade --name "Brave"                        --Id "Brave.Brave"                --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Microsoft Visual Studio Code" --Id "Microsoft.VisualStudioCode" --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "WezTerm"                      --Id "wez.wezterm"                --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Oh My Posh"                   --Id "JanDeDobbeleer.OhMyPosh"    --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Powershell"                   --Id "Microsoft.PowerShell"       --source winget --scope user --accept-package-agreements --accept-source-agreements  # powershell require admin
winget install --no-upgrade --name "Git"                          --Id "Git.Git"                    --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Neovim"                       --Id "Neovim.Neovim"              --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "GNU Nano"                     --Id "GNU.Nano"                   --source winget --scope user --accept-package-agreements --accept-source-agreements
# winget install --no-upgrade                                       --Id "CoreyButler.NVMforWindows"  --source winget --scope user --accept-package-agreements --accept-source-agreements
# winget install --no-upgrade --name "Starship"                     --Id "Starship.Starship"          --source winget --scope user --accept-package-agreements --accept-source-agreements
Install-Module -Name Terminal-Icons -Repository PSGallery -Force -AcceptLicense -PassThru -Confirm  # -RequiredVersion 2.5.10
Install-Module -Name PSFzf  -SkipPublisherCheck  # -AcceptLicense -PassThru -Confirm  #  -RequiredVersion 2.5.10


# --GROUP:DEV_SYSTEM:VSRedistrib+VSBuildTools+Codeblocks+GnuWin32: Make+GnuPG+graphviz+WinFsp+SSHFS-win+xming+Node.js+Rustup+Cloudflare+Cloudflare WARP+Microsoft Garage Mouse without Borders
winget install --no-upgrade --name "VSRedistrib"                   --Id "Microsoft.VC++2015-2022Redist-x64"      --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "VSBuildTools"                  --Id "Microsoft.VisualStudio.2022.BuildTools" --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Codeblocks"                    --Id "Codeblocks.Codeblocks"                  --source winget --scope user --accept-package-agreements --accept-source-agreements  # IDE for C/C++
winget install --no-upgrade --name "GnuWin32: Make"                --Id "GnuWin32.Make"                          --source winget --scope user --accept-package-agreements --accept-source-agreements  # required for building some python packages with native extensions, like dlib
winget install --no-upgrade --name "GnuPG"                         --Id "GnuPG.GnuPG"                            --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "graphviz"                      --Id "Graphviz.Graphviz"                      --source winget --scope user --accept-package-agreements --accept-source-agreements  # required by pygraphviz. Used in Base.viz_object_hirarchy and Model.plot_model()
winget install --no-upgrade --name "WinFsp"                        --Id "WinFsp.WinFsp"                          --source winget --scope user --accept-package-agreements --accept-source-agreements  # mount remote filesystems and required by rclone
winget install --no-upgrade --name "SSHFS-win"                     --Id "SSHFS-Win.SSHFS-Win"                    --source winget --scope user --accept-package-agreements --accept-source-agreements  # mount remote filesystems  # as per https://github.com/winfsp/sshfs-win
winget install --no-upgrade --name "xming"                         --Id "xming.xming"                            --source winget --scope user --accept-package-agreements --accept-source-agreements  # X11 server. you need this while using wsl with gui, otherwise plt.show() returns: ImportError: Cannot load backend 'TkAgg' which requires the 'tk' interactive framework, as 'headless' is currently running
winget install --no-upgrade --name "Node.js"                       --Id "OpenJS.NodeJS"                          --source winget --scope user --accept-package-agreements --accept-source-agreements  # ncessary for nvim plugins.
winget install --no-upgrade --name "Rustup"                        --Id "Rustlang.Rustup"                        --source winget --scope user --accept-package-agreements --accept-source-agreements  # rust compiler, necessary for some nvim plugins
winget install --no-upgrade --name "Cloudflare"                    --Id "Cloudflare.cloudflared"                 --source winget --scope user --accept-package-agreements --accept-source-agreements  # cloudflare tunnel client, alternative to ngrok
winget install --no-upgrade --name "Cloudflare WARP"               --Id "Cloudflare.Warp"                        --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Microsoft Garage Mouse without Borders" --Id "Microsoft.MouseWithoutBorders" --source winget --scope user --accept-package-agreements --accept-source-agreements


# --GROUP:OTHER_WINDOWS:nu+Chrome+ChromeRemoteDesktop+Zoom+7zip+Firefox+Thunderbird+StreamlabsOBS+OBSStudio+MiKTeX+TexMaker+notepad+++Lapce+TesseractOCR+perl+DB Browser for SQLite+sql server management studio+Adobe Acrobat Reader DC+julia+Chafa+bottom+onefetch+Just+hyperfine+AWS CLI
winget install --no-upgrade --name "nu"                                 --Id "Nushell.Nushell"                   --source winget --scope user --accept-package-agreements --accept-source-agreements  # add to userpath C:\Program Files\nu\bin, done in symlinks
winget install --no-upgrade --name "Google Chrome"                      --Id "Google.Chrome"                     --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Chrome Remote Desktop Host"         --Id "Google.ChromeRemoteDesktop"        --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Zoom"                               --Id "Zoom.Zoom"                         --source winget    --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "7-zip"                              --Id "7zip.7zip"                         --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Mozilla Firefox"                    --Id "Mozilla.Firefox" --source winget   --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Mozilla Thunderbird (en-US)"        --Id "Mozilla.Thunderbird"               --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "StreamlabsOBS"                      --Id "Streamlabs.StreamlabsOBS"          --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "OBSStudio"                          --Id "OBSProject.OBSStudio"              --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "MiKTeX"                             --Id "MiKTeX.MiKTeX"                     --source winget   --scope user  # library / lanugage
winget install --no-upgrade --name "TexMaker"                           --Id "Texmaker.Texmaker"                 --source winget --scope user  # IDE better than simple TexWorks shipped with MikTex. IDE is basically GUI for cmd interface of Tex
winget install --no-upgrade --name "notepad++"                          --Id "Notepad++.Notepad++"               --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Lapce"                              --Id "Lapce.Lapce"                       --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "TesseractOCR"                       --Id "UB-Mannheim.TesseractOCR"          --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "perl"                               --Id "StrawbgnogerryPerl.StrawberryPerl"     --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "DB Browser for SQLite"              --Id "DBBrowserForSQLite.DBBrowserForSQLite" --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "sql server management studio"       --Id "Microsoft.SQLServerManagementStudio"   --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Adobe Acrobat Reader DC"            --Id "Adobe.Acrobat.Reader.64-bit"       --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "julia"                               --Id "Julialang.Julia" --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "Chafa"                               --Id "hpjansson.Chafa" --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "bottom"                              --Id "Clement.bottom" --source winget --scope user --accept-package-agreements --accept-source-agreements
winget install --no-upgrade --name "onefetch"                            --Id "o2sh.onefetch" --source winget --scope user  # repo-version of system fastfetch, see also tokei
winget install --no-upgrade --name "Just"                               --Id "Casey.Just" --source winget --scope user  # commandline runner
winget install --no-upgrade --name "hyperfine"                          --Id "sharkdp.hyperfine" --source winget --scope user  # benchmarking tool
winget install --no-upgrade --name "AWS Command Line Interface"         --Id "Amazon.AWSCLI" --source winget --scope user --accept-package-agreements --accept-source-agreements
