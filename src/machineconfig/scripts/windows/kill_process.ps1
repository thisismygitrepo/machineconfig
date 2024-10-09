

# . $HOME/scripts/activate_ve 've'
. $HOME/venvs/ve/Scripts/activate.ps1

python -c "from machineconfig.utils.procs import ProcessManager; ProcessManager().choose_and_kill()"
deactivate

