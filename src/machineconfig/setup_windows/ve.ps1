

# install uv package manager if not present, else, run an update using `uv self update`
if (-not (Test-Path -Path "$HOME\.local\bin\uv.exe")) {
    Write-Output "uv binary not found, installing..."
    irm https://astral.sh/uv/install.ps1 | iex
} else {
    Write-Output "uv binary found, updating..."
    & "$HOME\.local\bin\uv.exe" self update
}

# ~\.local\bin\uv.exe python upgrade $py_version
# ~\.local\bin\uv.exe pip install --upgrade pip

