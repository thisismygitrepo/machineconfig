# to run: powershell.exe -executionpolicy Bypass -nologo -noninteractive -file .\Install_Fonts.ps1

$FONTS = 0x14
$Path = ".\fonts-to-be-installed"
$objShell = New-Object -ComObject Shell.Application
$objFolder = $objShell.Namespace($FONTS)
$Fontdir = Get-ChildItem -Path $Path -File

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

# Cache installed font basenames once (raw + normalized map)
$installedFontFiles = Get-ChildItem C:\Windows\Fonts -File
$installedFonts = @{}
foreach ($f in $installedFontFiles) { $installedFonts[(Normalize-FontName $f.BaseName)] = 1 }

Write-Host "Existing related fonts detected:" ($installedFonts.Keys | Where-Object { $_ -match 'caskaydiacove|cascadiacode' } | Sort-Object | Get-Unique) -ForegroundColor DarkGray

foreach ($File in $Fontdir) {
    if ($File.Name -notmatch 'pfb$') {
    $candidateRaw = $File.BaseName
    $candidateNorm = Normalize-FontName $candidateRaw

        # 1. Exact file existence check (handles .ttf/.otf pairs) before invoking Shell CopyHere.
        $destFile = Join-Path -Path 'C:\Windows\Fonts' -ChildPath $File.Name
        if (Test-Path -LiteralPath $destFile) { Write-Host "Skip (file exists) $($File.Name)" -ForegroundColor Green; continue }

        # 2. Registry check: Fonts are registered under HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts
        try {
            $fontReg = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' -ErrorAction Stop
            $regMatch = $false
            foreach ($prop in $fontReg.PSObject.Properties) {
                $val = ($prop.Value | Out-String).Trim()
                $nm  = ($prop.Name | Out-String).Trim()
                $valNorm = Normalize-FontName ( [System.IO.Path]::GetFileNameWithoutExtension($val) )
                $nmNorm  = Normalize-FontName $nm
                if ($valNorm -eq $candidateNorm -or $nmNorm -eq $candidateNorm -or $nmNorm -match [Regex]::Escape($candidateNorm)) { $regMatch = $true; break }
            }
            if ($regMatch) {
                Write-Host "Skip (registry) $($File.Name)" -ForegroundColor Green
                continue
            }
        } catch {
            Write-Host "Registry font query failed: $($_.Exception.Message) (continuing)" -ForegroundColor DarkYellow
        }

        # 3. Original heuristic set: in-memory list
        if ($installedFonts.ContainsKey($candidateNorm)) { Write-Host "Skip (norm map) $($File.Name)" -ForegroundColor Green; continue }
        if ($installedFonts.Keys | Where-Object { $_ -match [Regex]::Escape($candidateNorm) }) { Write-Host "Skip (norm regex) $($File.Name)" -ForegroundColor Green; continue }

        Write-Host "Installing font (no matches) $($File.Name) | norm=$candidateNorm" -ForegroundColor Yellow
        $objFolder.CopyHere($File.FullName)
    }
}
Write-Host "Font installation script completed." -ForegroundColor Cyan