

# --- Define ve name and python version here ---
if (-not $ve_name) {
    $ve_name = "ve"
}

if (-not $py_version) {
    $py_version = "3.11"  # fastest version.
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

if (-not (Test-Path -Path "$HOME\.cargo\bin\uv.exe")) {
    Write-Output "uv binary not found, installing..."
    irm https://astral.sh/uv/install.ps1 | iex
}


~\.cargo\bin\uv.exe venv "$venvPath\$ve_name" --python $py_version --python-preference only-managed
if (-not $env:VIRTUAL_ENV) {
    echo "Activating virtual environment @ $HOME\venvs\$ve_name"
    & "$HOME\venvs\$ve_name\Scripts\Activate.ps1" -ErrorAction Stop
}
~\.cargo\bin\uv.exe pip install --upgrade pip

