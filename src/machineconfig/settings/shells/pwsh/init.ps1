

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
    "$HOME\.local\bin",
    "$CONFIG_ROOT\scripts",
    "$HOME\dotfiles\scripts\windows",
    "C:\Program Files (x86)\GnuWin32\bin",
    "C:\Program Files\CodeBlocks\MinGW\bin",
    "C:\Program Files\nu\bin",
    "C:\Program Files\Graphviz\bin"
)

# sources  ================================================================
if (Test-Path "$CONFIG_ROOT\scripts\wrap_mcfg.ps1") {
    . $CONFIG_ROOT\settings\broot\brootcd.ps1
    . $CONFIG_ROOT\settings\lf\windows\lfcd.ps1
    . $CONFIG_ROOT\settings\tere\terecd.ps1
    . $CONFIG_ROOT\settings\yazi\shell\yazi_cd.ps1
    . $CONFIG_ROOT\scripts\wrap_mcfg.ps1

    function lsdla { lsd -la }
    Set-Alias -Name l -Value lsdla -Option AllScope
    function d { wrap_in_shell_script devops $args }
    function c { wrap_in_shell_script cloud $args }
    function a { wrap_in_shell_script agents $args }
    function sx { wrap_in_shell_script sessions $args }
    function fx { wrap_in_shell_script ftpx $args }
    function f { wrap_in_shell_script fire $args }
    function rr { wrap_in_shell_script croshell $args }
    function u { wrap_in_shell_script utils $args }
    function t { wrap_in_shell_script terminal $args }
    function ms { wrap_in_shell_script msearch $args }

}
else {
    Write-Host "Missing config files: $CONFIG_ROOT"
    function lsdla { lsd -la }
    Set-Alias -Name l -Value lsdla -Option AllScope
    function d { devops $args }
    function c { cloud $args }
    function a { agents $args }
    function sx { sessions $args }
    function fx { ftpx $args }
    function f { fire $args }
    function rr { croshell $args }
    function u { utils $args }
    function t { terminal $args }
    function ms { msearch $args }
}



# sources end

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
