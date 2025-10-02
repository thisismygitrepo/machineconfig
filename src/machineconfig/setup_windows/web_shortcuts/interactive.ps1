

Write-Host "ℹ️  If you have execution policy issues, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1").Content
uv run --python 3.13 --with machineconfig devops self interactive
