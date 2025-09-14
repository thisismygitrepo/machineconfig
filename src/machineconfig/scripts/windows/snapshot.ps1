
. "$HOME\code\machineconfig\\Scripts\activate.ps1"

python $PSScriptRoot/../python/snapshot.py $args
deactivate -ErrorAction SilentlyContinue
