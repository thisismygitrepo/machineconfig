
cd ~
mkdir code -ErrorAction SilentlyContinue
cd ~/code
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.

$ve_name='ve'
& ~/venvs/$ve_name/Scripts/Activate.ps1

cd ~/code/crocodile
pip install -e .  # local installation of crocodile (allows for development)
pip install -r requirements.txt  # not installed automatically by corocdile.
cd ~/code/machineconfig
pip install -e .
echo "Finished setting up repos"

