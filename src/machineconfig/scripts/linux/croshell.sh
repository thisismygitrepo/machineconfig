
# source activate_ve.sh
source ~/venvs/ve/bin/activate

ipython -i --no-banner -m crocodile.croshell

# --term-title CROSHELL

#if ($c -eq "") {
#    clear
#
##}
#else {
#    python -c ("from crocodile.toolbox import *; import crocodile.environment as env;" + $c)
#}


# --autocall 1 in order to enable shell-like behaviour: e.g.: P x is interpreted as P(x)

#if ($args[0] -eq $null) {
#    $name = "ipython"
#}
#else {
#    $name = $args[0]
#}

# https://www.red-gate.com/simple-talk/sysadmin/powershell/how-to-use-parameters-in-powershell/
