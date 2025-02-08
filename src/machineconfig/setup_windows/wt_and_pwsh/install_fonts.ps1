# to run: powershell.exe -executionpolicy Bypass -nologo -noninteractive -file .\Install_Fonts.ps1

function Test-FontInstalled {
    param(
        [string]$FontName
    )
    $fonts = Get-ChildItem "C:\Windows\Fonts" | Where-Object {$_.PSIsContainer -eq $false} | Select-Object -ExpandProperty BaseName
    return $fonts -contains $FontName
}

$FONTS = 0x14
$Path = ".\fonts-to-be-installed"
$objShell = New-Object -ComObject Shell.Application
$objFolder = $objShell.Namespace($FONTS)
$Fontdir = dir $Path

foreach($File in $Fontdir) {
    if(!($file.name -match "pfb$")) {
        $fontName = $File.BaseName
        if(!(Test-FontInstalled -FontName $fontName)) {
            $objFolder.CopyHere($File.fullname)
            Write-Host "Installing font: $fontName"
        } else {
            Write-Host "Font already installed: $fontName"
        }
    }
}