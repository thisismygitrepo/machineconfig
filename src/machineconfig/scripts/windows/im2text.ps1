
#activate_ve
. $PSScriptRoot/activate_ve.ps1
$orig_path = $pwd

mkdir 'C:\temp' -ErrorAction SilentlyContinue
$target_path='c:\temp\test3.png'

if ($args.Length -eq 0) {
    # get image from clipboard
Add-Type -AssemblyName System.Windows.Forms
$clipboard = [System.Windows.Forms.Clipboard]::GetDataObject()

if ($clipboard.ContainsImage()) {
    [System.Drawing.Bitmap]$clipboard.getimage().Save($target_path, [System.Drawing.Imaging.ImageFormat]::Png)
#    Write-Output "clipboard content saved as $target_path"
} else {Write-Output "clipboard does not contains image data"}

}
else  {$target_path = Resolve-Path $args[0]}

cd ~/AppData/Local/Tesseract-OCR/
pytesseract.exe $target_path | Set-Clipboard
echo $(Get-Clipboard)

deactivate -ErrorAction SilentlyContinue
cd $orig_path
