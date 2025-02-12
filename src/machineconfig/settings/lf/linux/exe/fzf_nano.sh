#!/bin/sh
# 🔍 Fuzzy Finder with Nano Editor Integration

# 📝 Open selected file in nano
nano (~/scripts/fzf2g)  # space used for precedence in execution

# 💡 Alternative commands (commented):
# 🔎 FZF with bat preview:
# fzf --ansi --preview-window 'right:60%' --preview 'bat --color=always --style=numbers,grid,header --line-range :300 {}'

# 🪟 Windows Git Bash version:
# & "C:\Program Files\Git\usr\bin\nano.exe" (fzf --ansi --preview-window 'right:60%' --preview 'bat --color=always --style=numbers,grid,header --line-range :300 {}')

# 📜 PowerShell script integration:
# fzf | ~/scripts/nano.ps1

