
activate_ve
croshell -c "import_n_install('pyinstaller')"
$destination = $(croshell -c "print(P.tmpdir())")
pyinstaller $args[0] --onefile --workpath=$destination
cd $destination
echo $destination
