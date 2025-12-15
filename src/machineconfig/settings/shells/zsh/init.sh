#!/bin/zsh
# Record script start time for runtime measurement
# _START_TIME_NS=$(date +%s%N)
# _show_elapsed() {
#     local _end_ns _elapsed_ns _secs _ms
#     _end_ns=$(date +%s%N)
#     _elapsed_ns=$((_end_ns - _START_TIME_NS))
#     _secs=$((_elapsed_ns / 1000000000))
#     _ms=$((_elapsed_ns / 1000000 % 1000))
#     printf "Script runtime: %d.%03d seconds\n" "$_secs" "$_ms"
# }

# 🛠️ Zsh Shell Configuration and Initialization

add_to_path_if_not_already() {
    for dir in "$@"; do
        if [[ ! $PATH =~ (^|:)"${dir}"(:|$) ]]; then
            export PATH="$PATH:${dir}"
        fi
    done
}
CONFIG_ROOT="$HOME/.config/machineconfig"

# 📂 Add directories to PATH
add_to_path_if_not_already \
    "$CONFIG_ROOT/scripts" \
    "$HOME/dotfiles/scripts/linux" \
    "$HOME/.local/bin" \
    "$HOME/.cargo/bin" \
    "/usr/games"
# this way, if the script was run multiple times, e.g. due to nested shells in zellij, there will be no duplicates in the path
# export DISPLAY=localhost:0.0  # xming server
    # "$HOME/.nix-profile/bin" \
    # "/home/linuxbrew/.linuxbrew/bin" \

# echo "Sourcing scripts ..."
. $CONFIG_ROOT/settings/broot/br.sh
. $CONFIG_ROOT/settings/lf/linux/exe/lfcd.sh
. $CONFIG_ROOT/settings/tere/terecd.sh
. $CONFIG_ROOT/settings/yazi/shell/yazi_cd.sh
. $CONFIG_ROOT/scripts/wrap_mcfg

# check if file in ~/dotfiles/machineconfig/init_linux.sh exists and source it
if [ -f "$HOME/dotfiles/machineconfig/init_linux.sh" ]; then
    # echo "Sourcing $HOME/dotfiles/machineconfig/init_linux.sh"
    source "$HOME/dotfiles/machineconfig/init_linux.sh"
fi

# if [ -x "$HOME/.bun/bin/bun" ]; then
#     alias node='$HOME/.bun/bin/bun'
# fi

alias l='lsd -la'
alias d='wrap_in_shell_script devops'
alias c='wrap_in_shell_script cloud'
alias a='wrap_in_shell_script agents'
alias s='wrap_in_shell_script sessions'
alias fx='wrap_in_shell_script ftpx'
alias f='wrap_in_shell_script fire'
alias r='wrap_in_shell_script croshell'
alias u='wrap_in_shell_script utils'
alias t='wrap_in_shell_script terminal'
alias ms='wrap_in_shell_script msearch'
alias x='. $CONFIG_ROOT/scripts/wrap_mcfg explore'

# alias gcs='gh copilot suggest -t shell'
# alias gcg='gh copilot suggest -t git'
# alias gce='gh copilot explain'
# Check uniqueness of aliases
# type gcs
# type gcg
# type gce
# gcd() {
#   x=$(history -p '!!')
#   y=$(eval "$x" 2>&1)
#   gh copilot explain "Input command is: $x The output is this: $y"
# }


# https://github.com/atuinsh/atuin
# eval "$(atuin init bash)"
# source /home/alex/.config/broot/launcher/bash/br
# eval "$(thefuck --alias)"
# from https://github.com/ajeetdsouza/zoxide
eval "$(zoxide init zsh)"
# from https://github.com/starship/starship
eval "$(starship init zsh)"

# LEVE THIS IN THE END TO AVOID EXECUTION FAILURE OF THE REST OF THE SCRIPT
if command -v atuin &> /dev/null; then
    eval "$(atuin init bash)"
elif command -v mcfly &> /dev/null; then
    eval "$(mcfly init bash)"
else
    # eval "$(tv init bash)"
    tv_shell_history() {
        # _disable_bracketed_paste
        local current_prompt="${READLINE_LINE:0:$READLINE_POINT}"
        local output
        # move to the next line so that the prompt is not overwritten
        printf "\n"
        # Get history using tv with the same arguments as zsh version
        output=$(tv bash-history --input "$current_prompt" --inline)

        if [[ -n "$output" ]]; then
            # Clear the right side of cursor and set new line
            READLINE_LINE="$output"
            READLINE_POINT=${#READLINE_LINE}
            # Uncomment this to automatically accept the line
            # (i.e. run the command without having to press enter twice)
            # accept-line() { echo; }; accept-line
        fi
        # move the cursor back to the previous line
        printf "\033[A"
        # _enable_bracketed_paste
    }
    bind -x '"\C-r": tv_shell_history'
fi

