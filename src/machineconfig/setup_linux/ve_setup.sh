
ve_name = 've'
py_version = 3.9

mypy=python$py_version

sudo apt install -y $mypy  # ignore system level one. launched with `python39`, as opposed to `python`
sudo apt install -y $mypy-venv
sudo apt install -y python3-pip

mkdir ~/venvs/
cd ~/venvs/ || exit
$mypy -m venv $ve_name
cd ~ || exit
source ~/venvs/$ve_name/bin/activate || exit

$mypy -m pip install --upgrade pip
pip install --upgrade pip
