

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


machineconfig_path=$HOME/code/machineconfig/src/machineconfig
. $machineconfig_path/settings/broot/br.sh
. $machineconfig_path/settings/lf/linux/exe/lfcd.sh
source $machineconfig_path/settings/tere/terecd.sh

# from https://github.com/cantino/mcfly
eval "$(mcfly init bash)"

# from https://github.com/ajeetdsouza/zoxide
eval "$(zoxide init bash)"

# export DISPLAY=localhost:0.0  # xming server

# gh extension install github/gh-copilot
# from https://www.npmjs.com/package/@githubnext/github-copilot-cli
# eval "$(github-copilot-cli alias -- "$0")"  # gives ??, git?, gh? aliases to github-clopilot-cli


# TERM=xterm
