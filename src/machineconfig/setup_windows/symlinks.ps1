

# CAUTION: this below is deliberately chosen over ~/scripts/activate_ve, because this is yet to be established
$machineconfig_path = (python -c "print(__import__('machineconfig').__file__[:-12])")
. machineconfig_path/scripts/windows/activate_ve.ps1

python -m fire machineconfig.profile.create main --choice=all
deactivate
