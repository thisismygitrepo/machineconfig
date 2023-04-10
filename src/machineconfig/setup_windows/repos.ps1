
cd ~
mkdir code -ErrorAction SilentlyContinue
cd ~/code
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/machineconfig --depth 4  # Choose browser-based authentication.


# CAUTION: The below is preferred over: ~/scripts/activate_ve.ps1 because this script explictly places the repos
# in the locations as above, and are used as below subsequently
# $machineconfig_path = (python -c "print(__import__('machineconfig').__file__[:-12])")
# . $machineconfig_path/scripts/windows/activate_ve.ps1
# no assumptions on which ve is activate is used for installation, this is dictated by activate_ve.
# this only solves the matter of where to find activate_ve script

cd ~/code/crocodile
pip install -e .  # local installation of crocodile (allows for development)
# pip install -r requirements.txt  # not installed automatically by corocdile.
cd ~/code/machineconfig
pip install -e .
echo "Finished setting up repos"

