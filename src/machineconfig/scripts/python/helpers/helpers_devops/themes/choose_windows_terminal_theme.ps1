$ErrorActionPreference = "Stop"

$settingsCandidates = @(
    Join-Path $env:LOCALAPPDATA "Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json",
    Join-Path $env:LOCALAPPDATA "Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json",
    Join-Path $env:LOCALAPPDATA "Microsoft\Windows Terminal\settings.json"
)

$settingsPath = $settingsCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $settingsPath) {
    Write-Host "Could not find Windows Terminal settings.json in documented install locations." -ForegroundColor Red
    exit 1
}

function Read-Settings([string]$Path) {
    return Get-Content -Path $Path -Raw | ConvertFrom-Json
}

function Write-Settings([string]$Path, [object]$Settings) {
    $Settings | ConvertTo-Json -Depth 100 | Set-Content -Path $Path -Encoding utf8
}

function Ensure-Defaults([object]$Settings) {
    if (-not $Settings.profiles) {
        throw "settings.json does not contain a profiles object."
    }
    if (-not $Settings.profiles.defaults) {
        $Settings.profiles | Add-Member -MemberType NoteProperty -Name defaults -Value ([PSCustomObject]@{}) -Force
    }
}

function Set-PreviewScheme([string]$Path, [string]$Scheme) {
    $settings = Read-Settings -Path $Path
    Ensure-Defaults -Settings $settings
    $settings.profiles.defaults.colorScheme = $Scheme
    Write-Settings -Path $Path -Settings $settings
}

function Restore-Scheme([string]$Path, [bool]$HadOriginalScheme, [object]$OriginalSchemeValue) {
    $settings = Read-Settings -Path $Path
    Ensure-Defaults -Settings $settings
    if ($HadOriginalScheme) {
        $settings.profiles.defaults.colorScheme = $OriginalSchemeValue
    } else {
        $null = $settings.profiles.defaults.PSObject.Properties.Remove("colorScheme")
    }
    Write-Settings -Path $Path -Settings $settings
}

function Render-ThemeMenu([string[]]$Schemes, [int]$Index, [string]$SettingsPath) {
    Clear-Host
    Write-Host "Windows Terminal Theme Selector" -ForegroundColor Cyan
    Write-Host "Settings: $SettingsPath" -ForegroundColor DarkGray
    Write-Host "Use Up/Down to preview quickly, Enter to keep, Esc to cancel." -ForegroundColor Yellow
    Write-Host ""

    $windowSize = [Math]::Min(18, $Schemes.Count)
    $startIndex = [Math]::Max(0, [Math]::Min($Index - [int]($windowSize / 2), $Schemes.Count - $windowSize))
    $endIndex = $startIndex + $windowSize - 1

    for ($i = $startIndex; $i -le $endIndex; $i++) {
        if ($i -eq $Index) {
            Write-Host ("-> " + $Schemes[$i]) -ForegroundColor Green
        } else {
            Write-Host ("   " + $Schemes[$i])
        }
    }

    Write-Host ""
    Write-Host ("Previewing: " + $Schemes[$Index]) -ForegroundColor Magenta
}

$settings = Read-Settings -Path $settingsPath
Ensure-Defaults -Settings $settings

$schemeNames = @()
if ($settings.schemes) {
    $schemeNames = @(
        $settings.schemes |
            ForEach-Object { $_.name } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
            Sort-Object -Unique
    )
}

if ($schemeNames.Count -eq 0) {
    Write-Host "No color schemes were found in settings.json under the schemes array." -ForegroundColor Red
    exit 1
}

$hadOriginalScheme = $settings.profiles.defaults.PSObject.Properties.Name -contains "colorScheme"
$originalSchemeValue = if ($hadOriginalScheme) { $settings.profiles.defaults.colorScheme } else { $null }

$currentIndex = 0
if ($hadOriginalScheme -and $originalSchemeValue -is [string] -and -not [string]::IsNullOrWhiteSpace($originalSchemeValue)) {
    $existingIndex = [array]::IndexOf($schemeNames, $originalSchemeValue)
    if ($existingIndex -ge 0) {
        $currentIndex = $existingIndex
    }
}

$confirmed = $false
Set-PreviewScheme -Path $settingsPath -Scheme $schemeNames[$currentIndex]

try {
    while ($true) {
        Render-ThemeMenu -Schemes $schemeNames -Index $currentIndex -SettingsPath $settingsPath
        $key = [System.Console]::ReadKey($true)
        switch ($key.Key) {
            "UpArrow" {
                if ($currentIndex -gt 0) {
                    $currentIndex--
                    Set-PreviewScheme -Path $settingsPath -Scheme $schemeNames[$currentIndex]
                }
                continue
            }
            "DownArrow" {
                if ($currentIndex -lt ($schemeNames.Count - 1)) {
                    $currentIndex++
                    Set-PreviewScheme -Path $settingsPath -Scheme $schemeNames[$currentIndex]
                }
                continue
            }
            "PageUp" {
                if ($currentIndex -gt 0) {
                    $currentIndex = [Math]::Max(0, $currentIndex - 10)
                    Set-PreviewScheme -Path $settingsPath -Scheme $schemeNames[$currentIndex]
                }
                continue
            }
            "PageDown" {
                if ($currentIndex -lt ($schemeNames.Count - 1)) {
                    $currentIndex = [Math]::Min($schemeNames.Count - 1, $currentIndex + 10)
                    Set-PreviewScheme -Path $settingsPath -Scheme $schemeNames[$currentIndex]
                }
                continue
            }
            "Enter" {
                $confirmed = $true
                break
            }
            "Escape" {
                break
            }
            Default {
                continue
            }
        }
    }
}
finally {
    if (-not $confirmed) {
        Restore-Scheme -Path $settingsPath -HadOriginalScheme $hadOriginalScheme -OriginalSchemeValue $originalSchemeValue
        Clear-Host
        Write-Host "Theme selection canceled. Restored previous scheme." -ForegroundColor Yellow
    } else {
        Clear-Host
        Write-Host ("Applied Windows Terminal color scheme: " + $schemeNames[$currentIndex]) -ForegroundColor Green
    }
}
