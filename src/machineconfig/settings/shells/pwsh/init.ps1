

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

try {
    Set-Alias -Name gcs -Value {gh copilot suggest -t shell}
    Set-Alias -Name gcg -Value {gh copilot suggest -t git}
    Set-Alias -Name gce -Value {gh copilot explain}
    # Check for conflicts
    # Get-Command gcs -ErrorAction SilentlyContinue
    # Get-Command gcg -ErrorAction SilentlyContinue
    # Get-Command gce -ErrorAction SilentlyContinue
}
catch {
    # Do nothing
}


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

# try {
#     Invoke-Expression -Command $(mcfly init powershell | out-string)
# }
# catch {
#     # Do nothing
# }


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

