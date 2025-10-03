
cd ~
mkdir code -ErrorAction SilentlyContinue
cd ~\code


if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    winget install --no-upgrade --name "Git" --Id Git.Git --source winget --accept-package-agreements --accept-source-agreements --scope user
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Setup machineconfig repository
if (Test-Path "machineconfig") {
    Write-Host "🔄 machineconfig directory exists, updating..."
    Set-Location machineconfig
    git reset --hard
    git pull
    Set-Location ..
} else {
    Write-Host "⏳ Cloning machineconfig repository..."
    git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.
}


cd $HOME\code\machineconfig
& "$HOME\.local\bin\uv.exe" sync --no-dev
echo "Finished setting up repos"
