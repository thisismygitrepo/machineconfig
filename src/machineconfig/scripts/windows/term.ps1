# Equivalent PowerShell script for term.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Generate random name using timestamp and SHA256 hash
$timestampNs = [DateTimeOffset]::Now.ToUnixTimeMilliseconds() * 1000000
$hashInput = [System.Text.Encoding]::UTF8.GetBytes($timestampNs.ToString())
$sha256 = [System.Security.Cryptography.SHA256]::Create()
$hashBytes = $sha256.ComputeHash($hashInput)
$hashString = -join ($hashBytes | ForEach-Object { $_.ToString('x2') })
$randomName = $hashString.Substring(0, 16)

$opDir = "$env:USERPROFILE\tmp_results\tmp_scripts\machineconfig"
$opProgramPath = "$opDir\$randomName.ps1"
$global:OP_PROGRAM_PATH = $opProgramPath

# ANSI color/style codes (using Write-Host colors)
$bold = [char]27 + '[1m'
$reset = [char]27 + '[0m'
$green = [char]27 + '[32m'
$yellow = [char]27 + '[33m'
$blue = [char]27 + '[34m'
$red = [char]27 + '[31m'

$timestamp = Get-Date -Format 'u'

Write-Host "${bold}${blue}🛠️  terminal — running term${reset}"
Write-Host "${blue}Timestamp:${reset} ${timestamp}"
Write-Host "${blue}Op program path:${reset} ${opProgramPath}"

terminal $args

if (Test-Path $opProgramPath) {
    Write-Host "${green}✅ Found op program:${reset} ${opProgramPath}"
    # Assuming bat is available; otherwise, use Get-Content
    & bat --style=plain --paging=never $opProgramPath
    Write-Host "${green}▶ Running...${reset}"
    . $opProgramPath
    $status = $LASTEXITCODE
    if ($status -eq 0) {
        Write-Host "${green}✅ Completed successfully (exit ${status})${reset}"
    } else {
        Write-Host "${yellow}⚠️  Program exited with status ${status}${reset}"
    }
} else {
    Write-Host "${yellow}⚠️  No op program found at: ${opProgramPath}${reset}"
}