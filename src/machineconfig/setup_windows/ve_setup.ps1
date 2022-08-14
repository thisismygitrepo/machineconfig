
$ve_name = 'latest'
$py_version = 310

mkdir ~/venvs -ErrorAction SilentlyContinue
cd ~

set mypy ($env:LOCALAPPDATA + "\Programs\Python\Python$py_version\python.exe")
&$mypy  -m venv "./venvs/$ve_name"  # ve will have same python version as `python`, where it.
# activate
& ~/venvs/$ve_name/Scripts/Activate.ps1
&$mypy -m pip install --upgrade pip  # upgrades the pip from Python location/lib/site-pacakges/pip
pip install --upgrade pip  # upgrades the pip that is within the environment.
echo "Finished setting up virtual environment."

