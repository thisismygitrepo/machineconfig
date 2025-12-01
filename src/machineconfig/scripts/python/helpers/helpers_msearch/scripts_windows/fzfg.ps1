#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$QueryTokens
)

if ($null -eq $QueryTokens) {
    $QueryTokens = @()
}

$initialQuery = if ($QueryTokens.Count -gt 0) { [string]::Join(' ', $QueryTokens) } else { '' }
$rgPrefix = 'rg --column --line-number --no-heading --color=always --smart-case '

$escapedDefault = if ($initialQuery.Length -gt 0) {
    $rgPrefix + '"' + $initialQuery.Replace('"', '""') + '" || type nul'
} else {
    'type nul'
}

$previousDefault = $env:FZF_DEFAULT_COMMAND
$env:FZF_DEFAULT_COMMAND = $escapedDefault

$reloadBinding = "change:reload:$rgPrefix{q} || type nul"
$ctrlFBinding = 'ctrl-f:unbind(change,ctrl-f)+change-prompt(2. fzf> )+enable-search+clear-query+rebind(ctrl-r)'
$ctrlRBinding = "ctrl-r:unbind(ctrl-r)+change-prompt(1. ripgrep> )+disable-search+reload($rgPrefix{q} || type nul)+rebind(change,ctrl-f)"

try {
    $selectionRaw = & fzf --ansi `
        --color 'hl:-1:underline,hl+:-1:underline:reverse' `
        --disabled `
        --query $initialQuery `
        --bind $reloadBinding `
        --bind $ctrlFBinding `
        --bind $ctrlRBinding `
        --prompt '1. ripgrep> ' `
        --delimiter ':' `
        --header 'CTRL-R (ripgrep mode) | CTRL-F (fzf mode)' `
        --preview 'bat --color=always {1} --highlight-line {2}' `
        --preview-window 'up,60%,border-bottom,+{2}+3/3,~3'
}
finally {
    if ($null -ne $previousDefault) {
        $env:FZF_DEFAULT_COMMAND = $previousDefault
    } else {
        Remove-Item Env:FZF_DEFAULT_COMMAND -ErrorAction SilentlyContinue
    }
}

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($selectionRaw)) {
    exit
}

if ($selectionRaw -match '^(?<path>.+?):(?<line>\d+):(?<column>\d+):') {
    $path = $Matches['path']
    $line = [int]$Matches['line']
    $column = [int]$Matches['column']
    & hx ("{0}:{1}:{2}" -f $path,$line,$column)
}