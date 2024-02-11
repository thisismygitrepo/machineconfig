

# export PATH="~/.local/bin:~/code/machineconfig/src/machineconfig/scripts/linux:~/dotfiles/scripts/linux:~/.nix-profile/bin:/usr/games:$PATH"

add_to_path_if_not_already() {
    for dir in "$@"; do
        if [[ ! $PATH =~ (^|:)"${dir}"(:|$) ]]; then
            export PATH="${dir}:$PATH"
        fi
    done
}

add_to_path_if_not_already \
    "$HOME/.local/bin" \
    "$HOME/code/machineconfig/src/machineconfig/scripts/linux" \
    "$HOME/dotfiles/scripts/linux" \
    "$HOME/.nix-profile/bin" \
    "/usr/games"
# this way, if the script was run multiple times, e.g. due to nested shells in zellij, there will be no duplicates in the path
# export DISPLAY=localhost:0.0  # xming server


# echo "Sourcing scripts ..."
machineconfig_path=$HOME/code/machineconfig/src/machineconfig
. $machineconfig_path/settings/broot/br.sh
. $machineconfig_path/settings/lf/linux/exe/lfcd.sh
. $machineconfig_path/settings/tere/terecd.sh

# set alias l to lsd -la
alias l='lsd -la'

# echo "Initing zoxide ..."
# from https://github.com/ajeetdsouza/zoxide
eval "$(zoxide init bash)"

# from https://github.com/starship/starship
eval "$(starship init bash)"

# LEVE THIS IN THE END TO AVOID EXECUTION FAILURE OF THE REST OF THE SCRIPT
# from https://github.com/cantino/mcfly
eval "$(mcfly init bash)"
