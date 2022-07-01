
ve_name='ve'
py_version=3.9
mypy=python$py_version

sudo apt install $mypy  # ignore system level one. launched with `python39`, as opposed to `python`
sudo apt install $mypy-venv  # requires Yes
$mypy -m pip install --upgrade pip

mkdir ~/venvs/
cd ~/venvs/ || exit
$mypy -m venv $ve_name
cd ~ || exit
source ~/venvs/ve/bin/activate || exit
