#!/usr/bin/bash
#=======================================================================
# 🔗 WINDOWS-LINUX CROSS-PLATFORM SYMLINKS
#=======================================================================
# This script creates symbolic links between Windows and Linux filesystems

echo """#=======================================================================
🖥️  WINDOWS INTEGRATION | Creating links to Windows filesystem
#=======================================================================
"""

echo """📂 Linking Windows code directory...
   🔗 /mnt/c/Users/$(whoami)/code -> ~/code
"""
ln -s /mnt/c/Users/$(whoami)/code ~/code

echo """⚙️  Linking Windows dotfiles...
   🔗 /mnt/c/Users/$(whoami)/dotfiles -> ~/dotfiles
"""
ln -s /mnt/c/Users/$(whoami)/dotfiles ~/dotfiles

echo """#=======================================================================
✅ SETUP COMPLETE | Cross-platform symlinks created successfully
#=======================================================================
"""
