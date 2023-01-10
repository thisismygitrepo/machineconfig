#!/usr/bin/bash

sudo add-apt-repository ppa:deadsnakes/ppa
# you need to press enter at this point to continue.
# without this repo, 3.9 is not available.
sudo apt update

ve_name='ve'
py_version=3.9
mypy=python$py_version

sudo apt install -y $mypy  # ignore system level one. launched with `python39`, as opposed to `python`
sudo apt install -y $mypy-venv
sudo apt install -y python3-pip
sudo apt install -y python$py_version-tk  # without this, plt.show() will return UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
# if inside wsl, you also need xming to be installed and running. otherwise, plt.show returns: ImportError: Cannot load backend 'TkAgg' which requires the 'tk' interactive framework, as 'headless' is currently running. xserver?

mkdir ~/venvs/
cd ~/venvs/ || exit
$mypy -m venv $ve_name
cd ~ || exit
source ~/venvs/$ve_name/bin/activate || exit

$mypy -m pip install --upgrade pip
pip install --upgrade pip

echo "finished installing virtual environment"
