

# CAUTION: this below is deliberately chosen over ~/scripts/activate_ve, because this is yet to be established
. ~/code/machineconfig/src/machineconfig/scripts/windows/activate_ve.ps1

python -m fire machineconfig.profile.create main --choice=all
deactivate
