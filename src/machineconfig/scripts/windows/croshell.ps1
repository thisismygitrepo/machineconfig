
param ($c="")
#paarm ($python="")

~/venvs/ve/Scripts/Activate.ps1
#$py = "C:\Users\Alex\venvs\ve\Scripts\python.exe"
#$ipy = "C:\Users\Alex\venvs\ve\Scripts\ipython.exe"

if ($c -eq "") {
    clear
#    python -i -m crocodile.croshell
    ipython -i --no-banner --term-title CROSHELL -m crocodile.croshell

}
else {
    python -c ("from crocodile.toolbox import *; import crocodile.environment as env;" + $c)
}


# --autocall 1 in order to enable shell-like behaviour: e.g.: P x is interpreted as P(x)

#if ($args[0] -eq $null) {
#    $name = "ipython"
#}
#else {
#    $name = $args[0]
#}

# https://www.red-gate.com/simple-talk/sysadmin/powershell/how-to-use-parameters-in-powershell/
