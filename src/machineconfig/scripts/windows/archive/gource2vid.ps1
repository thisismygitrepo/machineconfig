
$repo = Read-Host -Prompt 'Input your repository directory'
# $repo = Resolve-Path $repo
if (-not (Test-Path $repo)) {
    Write-Host "Directory does not exist: $repo"
    exit
}
mkdir ~/gource
cd ~/gource
rm *
& "$HOME\AppData\Local\Gource\cmd\gource" -1920x1080 --seconds-per-day 0.4 -o gource.ppm $repo
C:\ffmpeg\bin\ffmpeg.exe -y -r 30 -f image2pipe -vcodec ppm -i .\gource.ppm -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 gource.avi

rm gource.ppm
