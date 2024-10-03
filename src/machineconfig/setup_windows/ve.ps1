

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


& "$HOME\.cargo\bin\uv.exe" venv "$venvPath\$ve_name" --python 3.11 --python-preference only-managed


cd $HOME
mkdir code -ErrorAction SilentlyContinue
cd $HOME\code

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    winget install --no-upgrade --name "Git" --Id Git.Git --source winget --accept-package-agreements --accept-source-agreements --scope user
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}


git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.


cd $HOME\code\crocodile
if (-not $env:VIRTUAL_ENV) {
    echo "Activating virtual environmen @ $HOME\venvs\$ve_name"
    & "$HOME\venvs\$ve_name\Scripts\Activate.ps1" -ErrorAction Stop
}

if (-not (Test-Path variable:CROCODILE_EXTRA)) {
    Write-Host "⚠️ Using default CROCODILE_EXTRA"
    & "$HOME\.cargo\bin\uv.exe" pip install -e .
} else {
    Write-Host "➡️ CROCODILE_EXTRA = $CROCODILE_EXTRA"
    & "$HOME\.cargo\bin\uv.exe" pip install -e .[$CROCODILE_EXTRA]
}

cd $HOME\code\machineconfig
& "$HOME\.cargo\bin\uv.exe" pip install -e .
echo "Finished setting up repos"
