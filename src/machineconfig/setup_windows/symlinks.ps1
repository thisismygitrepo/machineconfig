
#$ve_name='ve'
#& ~/venvs/$ve_name/Scripts/Activate.ps1
. ~/code/machineconfig/
python -m fire machineconfig.profile.create main
deactivate
