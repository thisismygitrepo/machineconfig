#!/bin/bash
# ⌨️ Linux Mint Keyboard Shortcuts Configuration

# 🚀 Rofi Launcher Shortcut Settings
KEYBINDING_NAME='Launch Rofi'
KEYBINDING_COMMAND='rofi -show drun'
KEYBINDING_BINDING='<Control><Alt>p'
KEYBINDING_PATH='/org/cinnamon/desktop/keybindings/custom-keybindings/custom0/'

# 🔑 Configure Shortcut
# Set the name
gsettings set org.cinnamon.desktop.keybindings.custom-keybinding:$KEYBINDING_PATH name "$KEYBINDING_NAME"
# Set the command
gsettings set org.cinnamon.desktop.keybindings.custom-keybinding:$KEYBINDING_PATH command "$KEYBINDING_COMMAND"
# Set the binding
gsettings set org.cinnamon.desktop.keybindings.custom-keybinding:$KEYBINDING_PATH binding "['$KEYBINDING_BINDING']"

# 📋 Update Keybindings List
# Get the current list of custom keybindings
CURRENT_KEYBINDINGS=$(gsettings get org.cinnamon.desktop.keybindings custom-list)

# 🔄 Add new keybinding if not present
if [[ "$CURRENT_KEYBINDINGS" != *custom0* ]]; then
    if [ "$CURRENT_KEYBINDINGS" = "@as []" ]; then
        NEW_KEYBINDINGS="['custom0']"
    else
        NEW_KEYBINDINGS="${CURRENT_KEYBINDINGS%]*}, 'custom0']"
    fi
    gsettings set org.cinnamon.desktop.keybindings custom-list "$NEW_KEYBINDINGS"
fi
