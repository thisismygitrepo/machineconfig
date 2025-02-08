# to run: powershell.exe -executionpolicy Bypass -nologo -noninteractive -file .\Install_Fonts.ps1

$FONTS = 0x14
$Path = ".\fonts-to-be-installed"
$objShell = New-Object -ComObject Shell.Application
$objFolder = $objShell.Namespace($FONTS)

# Get all currently installed fonts
$installedFonts = [System.Drawing.Text.InstalledFontCollection]::new().Families.Name

# Process each font in the directory
Get-ChildItem -Path $Path | Where-Object { $_.Extension -match '^\.(ttf|otf)$' } | ForEach-Object {
    $fontName = [System.Drawing.Text.PrivateFontCollection]::new().AddFontFile($_.FullName).Families.Name
    
    if ($installedFonts -contains $fontName) {
        Write-Host "Skipping $fontName - already installed"
    } else {
        Write-Host "Installing $fontName..."
        $objFolder.CopyHere($_.FullName)
        Start-Sleep -Milliseconds 500  # Give Windows time to process the font
    }
}