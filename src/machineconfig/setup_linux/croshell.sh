
# curl https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_linux/croshell.sh | bash

apt install python3.9-venv
cd ~
mkdir ~/venvs
python -m venv "./venvs/ve"  # ve will have same python version as `python`, where it.

. ~/venvs/ve/bin/activate  # activate, now use python instead of $mypy


mkdir ~/code
cd ~/code
git clone https://github.com/thisismygitrepo/machineconfig.git
git clone https://github.com/thisismygitrepo/crocodile.git
pip install -e ./machineconfig
pip install -e ./crocodile
python -m fire machineconfig.profile.create main
. ~/.bashrc
