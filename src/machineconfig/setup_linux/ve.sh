#!/usr/bin/bash

# this script is for setting up a virtual environment for python3.9
# the virtual environment is called 've' and is located in ~/venvs/

if [ -z "$ve_name" ]; then  # check if variable ve_name is set, if not, set it to 've'
ve_name="ve"
fi
if [ -z "$py_version" ]; then  # check if variable py_version is set, if not, set it to '3.9'
py_version=3.9
fi
mypy=python$py_version
py_version_no_dot=$(echo $py_version | tr -d '.')
# CAUTION: python ve installer does text manipulation on this file and make many hidden assumptions, exercie caution with development.


# check if python3.9 is installed
if ! command -v $mypy &> /dev/null
then
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


 check if $mypy-venv is installed
if ! command -v $mypy-venv &> /dev/null
then
    echo ''
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo "$mypy-venv could not be found, installing ..."
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo ''
    sudo apt install -y $mypy-venv
fi

 check if python3-pip is installed
if ! command -v pip &> /dev/null
then
    echo ''
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo "pip could not be found"
    sudo apt install -y python3-pip
fi


# check if python3-tk is installed
if ! command -v python3-tk &> /dev/null
then
    echo ''
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo "python3-tk could not be found"
    echo '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    echo ''

    sudo apt install -y python$py_version-tk  # without this, plt.show() will return UserWarning: Matplotlib is currently using agg, which is a non-GUI backend, so cannot show the figure.
fi

# if inside wsl, you also need xming to be installed and running. otherwise, plt.show returns: ImportError: Cannot load backend 'TkAgg' which requires the 'tk' interactive framework, as 'headless' is currently running. xserver?

mkdir ~/venvs/
cd ~/venvs/ || exit
$mypy -m venv $ve_name
cd ~ || exit
source ~/venvs/$ve_name/bin/activate || exit

$mypy -m pip install --upgrade pip
pip install --upgrade pip

echo "finished installing virtual environment"
