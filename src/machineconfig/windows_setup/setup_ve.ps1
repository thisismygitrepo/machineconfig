
$ve_name = 've'
$py_version = 39

mkdir ~/venvs
cd ~

set mypy ($env:LOCALAPPDATA + "\Programs\Python\Python$py_version\python.exe")
&$mypy  -m venv "./venvs/$ve_name"  # ve will have same python version as `python`, where it.
# activate
& ~/venvs/$ve_name/Scripts/Activate.ps1
&$mypy -m pip install --upgrade pip  # upgrades the pip that is within the environment.
