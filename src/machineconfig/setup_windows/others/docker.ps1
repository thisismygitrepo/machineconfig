
# as per https://docs.docker.com/desktop/install/windows-install/
mkdir ~/tmp_results/tmp_installers/docker
cd ~/tmp_results/tmp_installers/docker

curl "https://desktop.docker.com/win/main/amd64/Docker Desktop Installer.exe" --output installer.exe
Start-Process .\installer.exe -Wait install --accept-license
