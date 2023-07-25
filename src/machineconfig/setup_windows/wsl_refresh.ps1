
Write-Host "Currently, there is: "
wsl -l -v
wsl --unregister Ubuntu-22.04
Write-Host "You can install ... "
wsl --list --online
wsl --install -d Ubuntu-22.04
#  winget install Canonical.Ubuntu.2004 --source winget
# then launch from Ubutnu.exe
sudo apt update -y
sudo apt upgrade -y
