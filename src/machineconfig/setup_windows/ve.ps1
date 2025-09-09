

# --- Define ve name and python version here ---
if (-not $ve_name) {
    $ve_name = "ve"
}

if (-not $py_version) {
    $py_version = "3.13"  # fastest version.
}

# --- End of user defined variables ---

$venvPath = "$HOME\venvs"

if (-not (Test-Path -Path $venvPath)) {
    New-Item -ItemType Directory -Path $venvPath | Out-Null
}

# delete $HOME/venvs/$ve_name and its contents if it exists
Set-Location -Path $venvPath
if (Test-Path -Path $ve_name) {
    Write-Output ''
    Write-Output '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    Write-Output "🗑️ $ve_name already exists, deleting ..."
    Write-Output '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    Write-Output ''
    Remove-Item -Recurse -Force $ve_name
}

# install uv package manager if not present, else, run an update using `uv self update`
if (-not (Test-Path -Path "$HOME\.local\bin\uv.exe")) {
    Write-Output "uv binary not found, installing..."
    irm https://astral.sh/uv/install.ps1 | iex
} else {
    Write-Output "uv binary found, updating..."
    & "$HOME\.local\bin\uv.exe" self update
}


~\.local\bin\uv.exe python upgrade $py_version
~\.local\bin\uv.exe venv "$venvPath\$ve_name" --python $py_version --python-preference only-managed
if (-not $env:VIRTUAL_ENV) {
    echo "Activating virtual environment @ $HOME\venvs\$ve_name"
    & "$HOME\venvs\$ve_name\Scripts\Activate.ps1" -ErrorAction Stop
}
# ~\.local\bin\uv.exe pip install --upgrade pip

