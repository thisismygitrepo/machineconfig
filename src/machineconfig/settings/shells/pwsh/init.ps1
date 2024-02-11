


# try {
#     Import-Module -Name Terminal-Icons

#     # Shows navigable menu of all options when hitting Tab
#     Set-PSReadlineKeyHandler -Key Tab -Function MenuComplete
#     Set-PSReadlineKeyHandler -Key UpArrow -Function HistorySearchBackward
#     Set-PSReadlineKeyHandler -Key DownArrow -Function HistorySearchForward
#     # Set-PSReadlineOption -PredictionSource History
#     # Set-PSReadlineOption -PredictionViewStyle History
#     # see how to get dynamic help with prerelease
# }
# catch [System.Management.Automation.CommandNotFoundException] {
#     # Suppresses the "module not found" error
# }
# catch {
#     # Handles other types of errors
#     Write-Output $_.Exception.Message
# }

# PATH extension =====================================================
# $env:Path += ";$HOME\code\machineconfig\src\machineconfig\scripts\windows;$HOME\dotfiles\scripts\windows;C:\Program Files (x86)\GnuWin32\bin;C:\Program Files\CodeBlocks\MinGW\bin;C:\Program Files\nu\bin;C:\Program Files\Graphviz\bin"

function Add-ToPathIfNotAlready {
    param (
        [Parameter(Mandatory=$true)]
        [string[]]$Directories
    )

    foreach ($dir in $Directories) {
        if ($env:Path -notlike "*$dir*") {
            $env:Path += ";$dir"
        }
    }
}

Add-ToPathIfNotAlready -Directories @(
    "$HOME\code\machineconfig\src\machineconfig\scripts\windows",
    "$HOME\dotfiles\scripts\windows",
    "C:\Program Files (x86)\GnuWin32\bin",
    "C:\Program Files\CodeBlocks\MinGW\bin",
    "C:\Program Files\nu\bin",
    "C:\Program Files\Graphviz\bin"
)

# $machineconfig_path = (python -c "print(__import__('machineconfig').__file__[:-12])")
#C:\Program Files\Git\bin


# sources  ================================================================
. $HOME/code/machineconfig/src/machineconfig/settings/broot/brootcd.ps1
. $HOME/code/machineconfig/src/machineconfig/settings/lf/windows/lfcd.ps1
. $HOME/code/machineconfig/src/machineconfig/settings/tere/terecd.ps1

function lsdla { lsd -la }
Set-Alias -Name l -Value lsdla -Option AllScope

# patches ===========================================================

try {
    # patched by machineconfig from https://github.com/ajeetdsouza/zoxide
    Invoke-Expression (& {
        $hook = if ($PSVersionTable.PSVersion.Major -lt 6) { 'prompt' } else { 'pwd' }
        (zoxide init --hook $hook powershell | Out-String)
    })
}
catch {
    # Do nothing
}


oh-my-posh --init --shell pwsh --config $env:USERPROFILE/AppData/Local/Programs/oh-my-posh/themes/atomicBit.omp.json | Invoke-Expression

# try {
#     Invoke-Expression (&starship init powershell)
# }
# catch {
#     # Do nothing
# # oh-my-posh --init --shell pwsh --config $env:USERPROFILE/AppData/Local/Programs/oh-my-posh/themes/atomicBit.omp.json | Invoke-Expression
# }

# Set-Alias lvim '~/.local/bin/lvim.ps1'
# function fuck {     $history = (Get-History -Count 1).CommandLine;     if (-not [string]::IsNullOrWhiteSpace($history)) {         $f>

