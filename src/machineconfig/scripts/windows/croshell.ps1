

param ($f="", $c="", $r="", $run="")
#paarm ($python="")

$ErrorActionPreference = "Stop"
# Write-Host "$args"


~/venvs/ve/Scripts/Activate.ps1
#$py = "C:\Users\Alex\venvs\ve\Scripts\python.exe"
#$ipy = "C:\Users\Alex\venvs\ve\Scripts\ipython.exe"

if ($r -eq "") {}
else {
    ipython -i --no-banner -m crocodile.croshell -- --cmd "dat=P(r'$r').readit(); print(D.get_repr(dat))"
    # python -m crocodile.run $args  # --term-title CROSHELL
    break
}

# if ($run -eq "") {}
# else {
#     ipython -i --no-banner -m crocodile.run -- $args
#     break
# }

if ($c -eq "") {
    # Clear-Host
#    python -i -m crocodile.croshell
    ipython -i --no-banner -m crocodile.croshell
#  --term-title CROSHELL
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
