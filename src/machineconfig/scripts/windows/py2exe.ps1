
#activate_ve
# . $PSScriptRoot/activate_ve.ps1
. $HOME/venvs/ve/Scripts/activate.ps1

croshell -c "import_n_install('pyinstaller')"
$destination = $(croshell -c "print(P.tmpdir())")
pyinstaller $args[0] --onefile --workpath=$destination
cd $destination
echo $destination

deactivate -ErrorAction SilentlyContinue
