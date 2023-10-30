# CroShellFTP 2.0

# croshell -c "print(r'$machine', r'$file1')"
#~/venvs/ve/Scripts/Activate.ps1
. $PSScriptRoot/activate_ve.ps1 ve
python $PSScriptRoot/../python/ftpsx.py $args
deactivate -ErrorAction SilentlyContinue
