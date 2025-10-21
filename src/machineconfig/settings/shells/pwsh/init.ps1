

$CONFIG_ROOT = "$HOME\.config\machineconfig"

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
    "$CONFIG_ROOT\scripts\windows",
    "$HOME\dotfiles\scripts\windows",
    "C:\Program Files (x86)\GnuWin32\bin",
    "C:\Program Files\CodeBlocks\MinGW\bin",
    "C:\Program Files\nu\bin",
    "C:\Program Files\Graphviz\bin"
)

# sources  ================================================================
. $CONFIG_ROOT\settings\broot\brootcd.ps1
. $CONFIG_ROOT\settings\lf\windows\lfcd.ps1
. $CONFIG_ROOT\settings\tere\terecd.ps1


function lsdla { lsd -la }
Set-Alias -Name l -Value lsdla -Option AllScope
function d { devops @args }
function c { cloud @args }
function a { agents @args }
function ss { sessions @args }
function ff { ftpx @args }
function f { fire @args }
function rr { croshell @args }
function u { utils @args }

# try {
#     Set-Alias -Name gcs -Value {gh copilot suggest -t shell}
#     Set-Alias -Name gcg -Value {gh copilot suggest -t git}
#     Set-Alias -Name gce -Value {gh copilot explain}
#     # Check for conflicts
#     # Get-Command gcs -ErrorAction SilentlyContinue
#     # Get-Command gcg -ErrorAction SilentlyContinue
#     # Get-Command gce -ErrorAction SilentlyContinue
# }
# catch {
#     # Do nothing
# }


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

try {
    # Initialize Starship prompt
    Invoke-Expression (&starship init powershell)
}
catch {
    # Do nothing
}
