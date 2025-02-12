#!/usr/bin/bash
# 🔗 Windows-Linux Cross-Platform Symlinks

# 📂 Link Windows code directory
ln -s /mnt/c/Users/$(whoami)/code ~/code

# ⚙️ Link Windows dotfiles
ln -s /mnt/c/Users/$(whoami)/dotfiles ~/dotfiles
