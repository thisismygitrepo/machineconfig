
mkdir ~/gource

cd ~/gource

$HOME\AppData\Local\Gource\cmd\gource -1920x1080 -s 0.4 -o gource.ppm C:\Users\aalsaf01\code\SQLScriptsRepo
C:\ffmpeg\bin\ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i .\gource.ppm -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -crf 1 -threads 0 -bf 0 gource.avi
