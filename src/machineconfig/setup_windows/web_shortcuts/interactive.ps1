

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig devops $args
}
echo "devops command is now defined in this shell session."
