

cd ~
mkdir ~/venvs
apt install python3.9-venv
python -m venv "./venvs/ve"  # ve will have same python version as `python`, where it.
& ~/venvs/ve/bin/activate  # activate, now use python instead of $mypy
pip install crocodile
pip install machineconfig
python -m fire machineconfig.profile.create main

