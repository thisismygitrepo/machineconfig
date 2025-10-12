

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
function mcfg {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with "machineconfig>=5.84" mcfg $args
}
echo "Function 'mcfg' has been defined. You can now use it to run machineconfig commands."
