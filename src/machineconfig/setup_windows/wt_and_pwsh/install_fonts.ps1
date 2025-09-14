# to run: powershell.exe -executionpolicy Bypass -nologo -noninteractive -file .\Install_Fonts.ps1

$FONTS = 0x14
$Path = ".\fonts-to-be-installed"
$objShell = New-Object -ComObject Shell.Application
$objFolder = $objShell.Namespace($FONTS)
$Fontdir = Get-ChildItem -Path $Path -File

# Cache installed font basenames once to avoid repeated enumeration and normalize by removing underscores
$installedFonts = @(Get-ChildItem C:\Windows\Fonts -File | Select-Object -ExpandProperty BaseName | ForEach-Object { ($_ -replace '_','').ToLower() })

Write-Host "Existing related fonts detected:" ($installedFonts | Where-Object { $_ -match 'caskaydiacove|cascadiacode' } | Sort-Object | Get-Unique) -ForegroundColor DarkGray

foreach ($File in $Fontdir) {
    if ($File.Name -notmatch 'pfb$') {
        $candidate = ($File.BaseName -replace '_','').ToLower()

        # 1. Exact file existence check (handles .ttf/.otf pairs) before invoking Shell CopyHere.
        $destFile = Join-Path -Path 'C:\Windows\Fonts' -ChildPath $File.Name
        if (Test-Path -LiteralPath $destFile) {
            Write-Host "Skip (file exists) $($File.Name)" -ForegroundColor Green
            continue
        }

        # 2. Registry check: Fonts are registered under HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts
        try {
            $fontReg = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' -ErrorAction Stop
            $regMatch = $false
            foreach ($prop in $fontReg.PSObject.Properties) {
                $val = ($prop.Value | Out-String).Trim().ToLower()
                $nm  = ($prop.Name | Out-String).Trim().ToLower()
                if ($val -eq $File.Name.ToLower() -or $val -eq ($File.BaseName + '.ttf').ToLower() -or $nm -match [Regex]::Escape($candidate)) {
                    $regMatch = $true; break
                }
            }
            if ($regMatch) {
                Write-Host "Skip (registry) $($File.Name)" -ForegroundColor Green
                continue
            }
        } catch {
            Write-Host "Registry font query failed: $($_.Exception.Message) (continuing)" -ForegroundColor DarkYellow
        }

        # 3. Original heuristic set: in-memory list
        if ($installedFonts -contains $candidate) {
            Write-Host "Skip (already installed) $($File.Name)" -ForegroundColor Green
            continue
        }
        if ($installedFonts | Where-Object { $_ -match [Regex]::Escape($candidate) }) {
            Write-Host "Skip (regex match) $($File.Name)" -ForegroundColor Green
            continue
        }

        Write-Host "Installing font $($File.Name)" -ForegroundColor Yellow
        $objFolder.CopyHere($File.FullName)
    }
}
Write-Host "Font installation script completed." -ForegroundColor Cyan