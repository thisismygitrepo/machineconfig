
cd ~
mkdir code -ErrorAction SilentlyContinue
cd ~\code

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    winget install --no-upgrade --name "Git" --Id Git.Git --source winget --accept-package-agreements --accept-source-agreements --scope user
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}


git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.


cd $HOME\code\crocodile
if (-not $env:VIRTUAL_ENV) {
    echo "Activating virtual environment @ $HOME\venvs\$ve_name"
    & "$HOME\venvs\$ve_name\Scripts\Activate.ps1" -ErrorAction Stop
}

if (-not (Test-Path variable:CROCODILE_EXTRA)) {
    Write-Host "⚠️ Using default CROCODILE_EXTRA"
    & "$HOME\.local\bin\uv.exe" pip install -e .
} else {
    Write-Host "➡️ CROCODILE_EXTRA = $CROCODILE_EXTRA"
    & "$HOME\.local\bin\uv.exe" pip install -e .[$CROCODILE_EXTRA]
}

cd ~\code\machineconfig
& "$HOME\.local\bin\uv.exe" pip install -e .
echo "Finished setting up repos"
