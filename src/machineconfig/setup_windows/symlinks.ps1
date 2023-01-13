
#$ve_name='ve'
#& ~/venvs/$ve_name/Scripts/Activate.ps1
. ~/code/machineconfig/src/machineconfig/scripts/windows/activate_ve.ps1
python -m fire machineconfig.profile.create main --program_name=all
deactivate
