#!/bin/sh
# 📂 LF File Manager Directory Change Integration
#
# Changes working directory in shell to last dir in lf on exit (adapted from ranger).
#
# 📝 Setup Instructions:
#     LFCD="/path/to/lfcd.sh"
#     if [ -f "$LFCD" ]; then
#         source "$LFCD"
#     fi
#
# ⌨️ Optional Keybinding:
#     bind '"\C-o":"lfcd\C-m"'  # bash
#     bindkey -s '^o' 'lfcd\n'  # zsh
#

lfcd () {
    # 🔄 Create temporary file for directory tracking
    tmp="$(mktemp)"
    lf -last-dir-path="$tmp" "$@"
    if [ -f "$tmp" ]; then
        dir="$(cat "$tmp")"
        rm -f "$tmp"
        if [ -d "$dir" ]; then
            if [ "$dir" != "$(pwd)" ]; then
                cd "$dir"
            fi
        fi
    fi
}

# 🔗 Create alias for quick access
alias lf="lfcd"
