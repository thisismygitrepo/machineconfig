#!/usr/bin/bash

# this script is for setting up a virtual environment for python


if [ -z "$ve_name" ]; then
    ve_name="ve"
fi

if [ -z "$py_version" ]; then
    py_version=3.9
fi


mypy=python$py_version
py_version_no_dot=$(echo $py_version | tr -d '.')


# check if $mypy is installed
if ! command -v $mypy &> /dev/null; then
    echo ''
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo "$mypy could not be found, installing ..."
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo ''
    sudo add-apt-repository ppa:deadsnakes/ppa  # you need to press enter at this point to continue. # without this repo, 3.9 is not available.
    sudo apt update
    sudo apt install -y $mypy  # ignore system level one. launched with `python39`, as opposed to `python`
    #    nix-env -iA "nixpkgs.python$py_version_no_dot"
fi


if ! dpkg -s $mypy-venv > /dev/null 2>&1; then  # python-venv is not a command, but a module of python.
    echo ''
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo "$mypy-venv could not be found, installing ..."
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo ''
    sudo apt install -y $mypy-venv
fi


if ! command -v pip &> /dev/null; then
    echo ''
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo "pip could not be found, installing ..."
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo ''
    sudo apt install -y python3-pip
fi


if ! dpkg -s python3-tk > /dev/null 2>&1; then
    echo ''
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo "python3-tk could not be found, installing ..."
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo ''
    sudo apt install -y python3-tk  # without this, plt.show() will return UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
fi

# TOOD: if inside wsl, you also need xming to be installed and running. otherwise, plt.show returns: ImportError: Cannot load backend 'TkAgg' which requires the 'tk' interactive framework, as 'headless' is currently running. xserver?

mkdir ~/venvs/
cd ~/venvs/ || exit
$mypy -m venv $ve_name
cd ~ || exit
source ~/venvs/$ve_name/bin/activate || exit

$mypy -m pip install --upgrade pip
pip install --upgrade pip

echo "Finished installing virtual environment"
echo "Use this to activate: source ~/venvs/$ve_name/bin/activate"
