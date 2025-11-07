# to run: powershell.exe -executionpolicy Bypass -nologo -noninteractive -file .\Install_Fonts.ps1

$FONTS = 0x14
$Path = ".\fonts-to-be-installed"
$objShell = New-Object -ComObject Shell.Application
$objFolder = $objShell.Namespace($FONTS)
$Fontdir = Get-ChildItem -Path $Path -File

$invalidCharPattern = "[{0}]" -f ([Regex]::Escape(([string]::Join('', [System.IO.Path]::GetInvalidFileNameChars()))))

function Get-FontBaseNameSafe {
    param([string]$Input)
    if ([string]::IsNullOrWhiteSpace($Input)) { return "" }
    $candidate = ($Input -split ',')[0].Trim()
    try { return [System.IO.Path]::GetFileNameWithoutExtension($candidate) }
    catch {
        $sanitized = [Regex]::Replace($candidate, $invalidCharPattern, '')
        return ($sanitized -replace '\\.[^.]+$')
    }
}

# Normalization helper: remove spaces, underscores, hyphens, 'nerd', 'font', and collapse 'nf' for broad matching
function Normalize-FontName {
    param([string]$Name)
    $n = $Name.ToLower()
    $n = $n -replace '[ _-]', ''
    $n = $n -replace 'nerd', ''
    $n = $n -replace 'font', ''
    $n = $n -replace 'nf', ''
    return $n
}

function Get-FontIdentityForms {
    param([string]$Name)
    if ([string]::IsNullOrWhiteSpace($Name)) { return @() }
    $normalized = Normalize-FontName $Name
    if ([string]::IsNullOrWhiteSpace($normalized)) { return @() }

    $forms = @()
    $forms += $normalized

    $stylePattern = '(regular|italic|oblique|bold|bolditalic|semibold|semilight|light|extrabold|extralight|medium|thin|black|book|ultra|heavy|demi|retina|condensed|narrow|windowscompatible|complete|windowscomp|compatibility)+$'
    $stem = $normalized
    while ($stem -match $stylePattern) {
        $stem = [Regex]::Replace($stem, $stylePattern, '')
        if ([string]::IsNullOrWhiteSpace($stem)) { break }
        $forms += $stem
    }

    $stemForVariants = $stem
    foreach ($tail in @('mono', 'propo')) {
        $tmp = $stemForVariants
        while (-not [string]::IsNullOrWhiteSpace($tmp) -and $tmp.EndsWith($tail)) {
            $tmp = $tmp.Substring(0, $tmp.Length - $tail.Length)
            if ([string]::IsNullOrWhiteSpace($tmp)) { break }
            $forms += $tmp
        }
    }

    return ($forms | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)
}

function Test-FontFormsOverlapFuzzy {
    param(
        [string[]]$CandidateForms,
        [string[]]$ExistingForms
    )
    foreach ($candidate in $CandidateForms) {
        if ([string]::IsNullOrWhiteSpace($candidate)) { continue }
        foreach ($existing in $ExistingForms) {
            if ([string]::IsNullOrWhiteSpace($existing)) { continue }
            if ($existing.Contains($candidate) -or $candidate.Contains($existing)) { return $true }
        }
    }
    return $false
}

function Merge-UniqueForms {
    param(
        [string[]]$Existing,
        [string[]]$Additional
    )
    return (($Existing + $Additional) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique)
}

# Cache installed font basenames once (raw + normalized map)
$installedFontFiles = Get-ChildItem C:\Windows\Fonts -File
$installedFonts = @()
foreach ($f in $installedFontFiles) {
    $installedFonts = Merge-UniqueForms $installedFonts (Get-FontIdentityForms $f.BaseName)
}

$relatedInstalled = $installedFonts | Where-Object { $_ -match 'caskaydiacove|cascadiacode' } | Sort-Object | Get-Unique
Write-Host "Existing related fonts detected:" $relatedInstalled -ForegroundColor DarkGray

$registryFonts = @()
$fontReg = $null
try {
    $fontReg = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' -ErrorAction Stop
} catch {
    Write-Host "Registry font list unavailable: $($_.Exception.Message)" -ForegroundColor DarkYellow
}
if ($null -ne $fontReg) {
    foreach ($prop in $fontReg.PSObject.Properties) {
        $val = ($prop.Value | Out-String).Trim()
        $nm  = ($prop.Name | Out-String).Trim()
        $registryFonts = Merge-UniqueForms $registryFonts (Get-FontIdentityForms (Get-FontBaseNameSafe $val))
        $registryFonts = Merge-UniqueForms $registryFonts (Get-FontIdentityForms (Get-FontBaseNameSafe $nm))
    }
}

foreach ($File in $Fontdir) {
    if ($File.Name -match 'pfb$') { continue }

    $candidateForms = Get-FontIdentityForms $File.BaseName
    if ($candidateForms.Count -eq 0) { $candidateForms = @(Normalize-FontName $File.BaseName) }
    $candidateNorm = if ($candidateForms.Count -gt 0) { $candidateForms[0] } else { '' }

    # 1. Exact file existence check (handles .ttf/.otf pairs) before invoking Shell CopyHere.
    $destFile = Join-Path -Path 'C:\Windows\Fonts' -ChildPath $File.Name
    if (Test-Path -LiteralPath $destFile) {
        Write-Host "Skip (file exists) $($File.Name)" -ForegroundColor Green
        $installedFonts = Merge-UniqueForms $installedFonts $candidateForms
        continue
    }

    # 2. Registry check: Fonts are registered under HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts
    if ($registryFonts.Count -gt 0) {
        $exactRegMatch = $candidateForms | Where-Object { $registryFonts -contains $_ }
        if ($exactRegMatch.Count -gt 0) {
            Write-Host "Skip (registry) $($File.Name)" -ForegroundColor Green
            $installedFonts = Merge-UniqueForms $installedFonts $candidateForms
            continue
        }
        if (Test-FontFormsOverlapFuzzy $candidateForms $registryFonts) {
            Write-Host "Skip (registry family) $($File.Name)" -ForegroundColor Green
            $installedFonts = Merge-UniqueForms $installedFonts $candidateForms
            continue
        }
    }

    # 3. Original heuristic set: in-memory list
    if (($candidateForms | Where-Object { $installedFonts -contains $_ }).Count -gt 0) {
        Write-Host "Skip (installed map) $($File.Name)" -ForegroundColor Green
        $installedFonts = Merge-UniqueForms $installedFonts $candidateForms
        continue
    }
    if (Test-FontFormsOverlapFuzzy $candidateForms $installedFonts) {
        Write-Host "Skip (installed family) $($File.Name)" -ForegroundColor Green
        $installedFonts = Merge-UniqueForms $installedFonts $candidateForms
        continue
    }

    Write-Host "Installing font (no matches) $($File.Name) | norm=$candidateNorm" -ForegroundColor Yellow
    $objFolder.CopyHere($File.FullName)
    $installedFonts = Merge-UniqueForms $installedFonts $candidateForms
}
Write-Host "Font installation script completed." -ForegroundColor Cyan