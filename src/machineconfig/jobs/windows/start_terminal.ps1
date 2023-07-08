
# wt  --profile croshell -d . --title "MyTerminal" --tabColor "red"`; split-pane --vertical --size 0.55 pwsh machineconfig-workingdirectory ~/code/crocodile -Command "pwd" `; split-pane -V PowerShell -NoExit -Command  "cd code/machineconfig" `; split-pane -H wsl.exe cmatrix`; split-pane -V wsl.exe sl
# wt -p "Command Prompt" `; split-pane -p "Windows PowerShell" `; split-pane -H wsl.exe

# See more settings here: https://docs.microsoft.com/en-us/windows/terminal/

$WINDOW_NUM = 600

wt --window $WINDOW_NUM --title home --startingDirectory "$HOME/code/crocodile" pwsh -NoExit -Command "git status"
sleep 3; wt --window $WINDOW_NUM split-pane --vertical --title mac --size 0.5 --startingDirectory "$HOME/code/machineconfig" pwsh -NoExit -Command "git status"
sleep 3; wt --window $WINDOW_NUM  split-pane --horizontal --title dot --size 0.5  --startingDirectory "$HOME/dotfiles" pwsh -NoExit -Command "ls"

# sleep 3; wt --window $WINDOW_NUM swap-pane up
#sleep 3; wt --window $WINDOW_NUM move-focus left split-pane --horizontal --title THIS_MACHINEwsl --size 0.3 wsl
sleep 3; wt --window $WINDOW_NUM new-tab --title crypto --startingDirectory "$HOME/code/crypto" pwsh -NoExit -Command "git status"
sleep 3; wt --window $WINDOW_NUM split-pane --horizontal --title data --size 0.5 --startingDirectory "$HOME/data" pwsh -NoExit -Command "lf"
