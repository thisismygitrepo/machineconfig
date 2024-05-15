
# Editable installation of crocodile and machineconfig
# no assumptions on which ve is activate is used for installation, this is dictated by activate_ve.

cd ~
mkdir code -ErrorAction SilentlyContinue
cd ~/code

winget install --no-upgrade --name "Git" --Id Git.Git --source winget --accept-package-agreements --accept-source-agreements

git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.


cd ~/code/crocodile

if (-not (Test-Path variable:CROCODILE_EXTRA)) {
    Write-Host "⚠️ Using default CROCODILE_EXTRA"
    pip install -e .
} else { 
    Write-Host "➡️ CROCODILE_EXTRA = $CROCODILE_EXTRA"
    pip install -e .[$CROCODILE_EXTRA]
}

cd ~/code/machineconfig
pip install -e .
echo "Finished setting up repos"
