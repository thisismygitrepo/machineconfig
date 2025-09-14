# to run: powershell.exe -executionpolicy Bypass -nologo -noninteractive -file .\Install_Fonts.ps1

$FONTS = 0x14
$Path = ".\fonts-to-be-installed"
$objShell = New-Object -ComObject Shell.Application
$objFolder = $objShell.Namespace($FONTS)
$Fontdir = Get-ChildItem -Path $Path -File

# Cache installed font basenames once to avoid repeated enumeration and normalize by removing underscores
$installedFonts = @(Get-ChildItem C:\Windows\Fonts -File | Select-Object -ExpandProperty BaseName | ForEach-Object { ($_ -replace '_','').ToLower() })

Write-Host "🔍 Existing fonts detected:" ($installedFonts | Where-Object { $_ -match 'caskaydiacove|cascadiacode' } | Sort-Object | Get-Unique) -ForegroundColor DarkGray

foreach ($File in $Fontdir) {
    if ($File.Name -notmatch 'pfb$') {
        $candidate = ($File.BaseName -replace '_','').ToLower()
        # If any installed font contains the candidate substring, skip copy to avoid replacement prompt.
        if ($installedFonts -contains $candidate) {
            Write-Host "✅ Skipping already installed font $($File.Name)" -ForegroundColor Green
            continue
        }
        # Fallback: broader match using -match if -contains misses stylistic variations
        if ($installedFonts | Where-Object { $_ -match [Regex]::Escape($candidate) }) {
            Write-Host "✅ Skipping (regex) already installed font $($File.Name)" -ForegroundColor Green
            continue
        }
        Write-Host "⬆️ Installing font $($File.Name)" -ForegroundColor Yellow
        $objFolder.CopyHere($File.FullName)
    }
}
Write-Host "🏁 Font installation script completed." -ForegroundColor Cyan