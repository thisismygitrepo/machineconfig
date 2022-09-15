

$ve_name='ve'
$py_version=310

mkdir ~/venvs -ErrorAction SilentlyContinue
cd ~

winget install Python.Python.3.10 --source winget
set mypy ($env:LOCALAPPDATA + "\Programs\Python\Python$py_version\python.exe")
&$mypy  -m venv "./venvs/$ve_name"  # ve will have same python version as `python`, where it.

& ~/venvs/$ve_name/Scripts/Activate.ps1  # activate, now use python instead of $mypy

pip install --upgrade pip  # upgrades the pip that is within the environment.
pip install crocodile
pip install machineconfig

python -m fire machineconfig.create_symlinks main
python -m fire machinconfig.setup_windows_terminal.set_settings main
