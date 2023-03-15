
Import-Module -Name Terminal-Icons

# Shows navigable menu of all options when hitting Tab
Set-PSReadlineKeyHandler -Key Tab -Function MenuComplete
Set-PSReadlineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadlineKeyHandler -Key DownArrow -Function HistorySearchForward
# Set-PSReadlineOption -PredictionSource History
# Set-PSReadlineOption -PredictionViewStyle History
# see how to get dynamic help with prerelease


# PATH extension =====================================================
$env:Path += ";~\code\machineconfig\src\machineconfig\scripts\windows;~\dotfiles\scripts\windows;C:\Program Files (x86)\GnuWin32\bin;C:\Program Files\CodeBlocks\MinGW\bin;C:\Program Files\nu\bin;C:\Program Files\Graphviz\bin"

# sources  ================================================================
. ~/code/machineconfig/src/machineconfig/settings/broot/brootcd.ps1
. ~/code/machineconfig/src/machineconfig/settings/lf/windows/lfcd.ps1
. ~/code/machineconfig/src/machineconfig/settings/tere/terecd.ps1


# patches ===========================================================
# patched by machineconfig from https://github.com/ajeetdsouza/zoxide
Invoke-Expression (& {
    $hook = if ($PSVersionTable.PSVersion.Major -lt 6) { 'prompt' } else { 'pwd' }
    (zoxide init --hook $hook powershell | Out-String)
})

Set-Alias lvim 'C:\Users\alex\.local\bin\lvim.ps1'
# function fuck {     $history = (Get-History -Count 1).CommandLine;     if (-not [string]::IsNullOrWhiteSpace($history)) {         $f>
