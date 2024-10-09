
# . $HOME/scripts/activate_ve 've'
. "$HOME\scripts\activate_ve.ps1" ve

python -m fire machineconfig.jobs.python.checkout_version main
deactivate
