
$ve_name='ve'
$py_version=39

mkdir ~/venvs -ErrorAction SilentlyContinue
cd ~

winget install --name "Windows Terminal" --Id "Microsoft.WindowsTerminal" --Source winget  # Terminal is is installed by default on W 11
winget install --name "Powershell" --Id "Microsoft.PowerShell" --source winget  # powershell require admin
winget install --Id "Python.Python.3.9" --source winget

set mypy ($env:LOCALAPPDATA + "\Programs\Python\Python$py_version\python.exe")
&$mypy  -m venv "./venvs/$ve_name"  # ve will have same python version as `python`, where it.

& ~/venvs/$ve_name/Scripts/Activate.ps1  # activate, now use python instead of $mypy

#mkdir ~/code -ErrorAction SilentlyContinue
#cd code
pip install --upgrade pip  # upgrades the pip that is within the environment.
pip install crocodile
pip install machineconfig

python -m fire machineconfig.profile.create main
python -m fire machineconfig.setup_windows_terminal.set_settings main
