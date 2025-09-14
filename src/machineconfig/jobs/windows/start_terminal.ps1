
 wt  --profile croshell -d . --title "MyTerminal" --tabColor "red"`; split-pane --vertical --size 0.55 pwsh machineconfig-workingdirectory ~/code/machineconfig -Command "pwd" `; split-pane -V PowerShell -NoExit -Command  "cd code/machineconfig" `; split-pane -H wsl.exe cmatrix`; split-pane -V wsl.exe sl
# wt -p "Command Prompt" `; split-pane -p "Windows PowerShell" `; split-pane -H wsl.exe

# See more settings here: https://docs.microsoft.com/en-us/windows/terminal/

