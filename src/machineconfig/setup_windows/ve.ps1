
# this script is for setting up a virtual environment for python
# default virual enviroment nanme is `ve` and is located in ~/venvs/

# --- Define ve name and python version here ---
if (-not (Test-Path variable:ve_name)) {
    $ve_name='ve'
} else { Write-Host "ve_name is already defined as $ve_name" }

if (-not (Test-Path variable:py_version)) {
    $py_version=3.11
} else { Write-Host "py_version is already defined as $py_version" }
# --- End of user defined variables ---

$version_no_dot = $py_version -replace '\.', ''

mkdir ~/venvs -ErrorAction SilentlyContinue
Set-Location $HOME

Set-Variable mypy ($env:LOCALAPPDATA + "\Programs\Python\Python$version_no_dot\python.exe")

if (Test-Path $mypy) {
    Write-Host "$mypy exists."
} else {
    Write-Host "$mypy does not exist, trying to install it ($py_version)"
    winget install --id Python.Python.$py_version --source winget --accept-package-agreements --accept-source-agreements
}

# delete folder and its contents: "./venvs/$ve_name"
if (Test-Path "./venvs/$ve_name") {
    Write-Host "Deleting existing virtual environment at ./venvs/$ve_name"
    Remove-Item -Recurse -Force "./venvs/$ve_name"
}
&$mypy  -m venv "./venvs/$ve_name"  # ve will have same python version as `python`, where it.

# activate
& ~/venvs/$ve_name/Scripts/Activate.ps1
&$mypy -m pip install --upgrade pip  # upgrades the pip from Python location/lib/site-pacakges/pip
&$HOME/venvs/$ve_name/Scripts/python.exe -m pip install --upgrade pip  # upgrades the pip that is within the environment.

Write-Output "Finished setting up virtual environment."
Write-Output "Use this to activate: & ~/venvs/$ve_name/Scripts/Activate.ps1"
