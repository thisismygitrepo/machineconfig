
# ================================================== REPOS ======================================
cd ~
mkdir code
cd ~/code
git clone https://github.com/thisismygitrepo/crocodile.git --depth 4
git clone https://github.com/thisismygitrepo/dotfiles --depth 4  # Choose browser-based authentication.

# assumes ve is activated.
cd ~/code/crocodile
pip install -e .  # local installation of crocodile (allows for development)
pip install -r requirements.txt  # not installed automatically by corocdile.
