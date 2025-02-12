#!/bin/sh
# 📑 Left Pane File Preview Script
# Uses bat/batcat for syntax-highlighted preview with line numbers

batcat --color=always --theme=base16 --style=numbers,grid,header --line-range=300 $@
