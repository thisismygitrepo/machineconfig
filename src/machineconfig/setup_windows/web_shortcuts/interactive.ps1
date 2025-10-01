Write-Host "
🚀 ===========================================
📦 Machine Configuration Installation Script
============================================="

Write-Host "ℹ️  If you have execution policy issues, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"

Invoke-WebRequest -Uri "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/ve.ps1" -OutFile "ve.ps1"
.\ve.ps1
rm ve.ps1

uv run --python 3.13 --with machineconfig devops self interactive
# uv run --python 3.13 --with machineconfig https://raw.githubusercontent.com/thisismygitrepo/machineconfig/ee4f69e838e1acbb275bfb5a3d3faee23345f2a8/src/machineconfig/scripts/python/devops.py
