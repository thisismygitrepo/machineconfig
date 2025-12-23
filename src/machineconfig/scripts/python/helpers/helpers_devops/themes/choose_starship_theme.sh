#!/bin/bash

# Ensure UTF-8 encoding for symbols and CLI tools
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export LC_CTYPE=C.UTF-8
export PYTHONIOENCODING=utf-8

# Presets
presets=(
    "nerd-font-symbols    Changes the symbols for each module to use Nerd Font symbols."
    "no-nerd-font    Changes the symbols so that no Nerd Font symbols are used."
    "bracketed-segments    Changes the format to show segments in brackets."
    "plain-text-symbols    Changes the symbols for each module into plain text."
    "no-runtime-versions    Hides the version of language runtimes."
    "no-empty-icons    Does not show icons if the toolset is not found."
    "pure-preset    Emulates the look and behavior of Pure."
    "pastel-powerline    Inspired by M365Princess."
    "tokyo-night    Inspired by tokyo-night-vscode-theme."
    "gruvbox-rainbow    Inspired by Pastel Powerline and Tokyo Night."
    "jetpack    Pseudo minimalist preset inspired by geometry and spaceship."
)

# Join presets with newlines
input_data=$(printf "%s\n" "${presets[@]}")

preview_config="/tmp/starship_preview.toml"
# Preview command needs to extract the first column (preset name) from the line
# {} will be replaced by the selected line
# We use awk to handle multiple spaces as delimiter
preview_cmd="preset=\$(echo '{}' | awk '{print \$1}'); starship preset \"\$preset\" > $preview_config && LANG=C.UTF-8 LC_ALL=C.UTF-8 STARSHIP_CONFIG=$preview_config STARSHIP_SHELL=fish starship prompt"

if command -v tv &> /dev/null; then
    # tv requires input from stdin if no source-command is given
    selected_line=$(printf "%s" "$input_data" | LANG=C.UTF-8 LC_ALL=C.UTF-8 tv --ansi --preview-command "$preview_cmd" --preview-size 50)
elif command -v fzf &> /dev/null; then
    selected_line=$(printf "%s" "$input_data" | LANG=C.UTF-8 LC_ALL=C.UTF-8 fzf --ansi --preview "preset=\$(echo {} | awk '{print \$1}'); starship preset \$preset > $preview_config && LANG=C.UTF-8 LC_ALL=C.UTF-8 STARSHIP_CONFIG=$preview_config STARSHIP_SHELL=fish starship prompt" --preview-window bottom:30%)
else
    echo "Error: 'tv' or 'fzf' not found."
    exit 1
fi

if [ -n "$selected_line" ]; then
    selected_preset=$(echo "$selected_line" | awk '{print $1}')
    echo "Applying $selected_preset..."
    starship preset "$selected_preset" -o ~/.config/starship.toml
    echo "Done!"
fi
