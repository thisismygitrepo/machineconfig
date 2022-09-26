

$ScriptPath = Split-Path $MyInvocation.InvocationName

& "$ScriptPath/tools/bat.ps1"  # colored bat

& "$ScriptPath/tools/fd.ps1"  # search for files/folder names only. Result can be fed to fzf for further filtering. For that use: fd | fzf. one can also make fd the searcher in fzf
& "$ScriptPath/tools/fzf.ps1"  # search for files/folder names, but can come with preview option. For that use: my variant fzz.ps1
& "$ScriptPath/tools/ugrep.ps1"  # search for words in files.

& "$ScriptPath/tools/broot.ps1"
& "$ScriptPath/tools/kondo.ps1"

& "$ScriptPath/tools/lf.ps1"
& "$ScriptPath/tools/rg.ps1"  # used by lvim and spacevim
& "$ScriptPath/tools/zoomit.ps1"
