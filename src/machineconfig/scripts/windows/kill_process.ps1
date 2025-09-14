

. "$HOME\code\machineconfig\\Scripts\activate.ps1"

python -c "from machineconfig.utils.procs import ProcessManager; ProcessManager().choose_and_kill()"
deactivate

