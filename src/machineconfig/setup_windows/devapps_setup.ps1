

$ScriptPath = Split-Path $MyInvocation.InvocationName

& "$ScriptPath/tools/bat.ps1"
& "$ScriptPath/tools/fd.ps1"
& "$ScriptPath/tools/fzf.ps1"
& "$ScriptPath/tools/lf.ps1"
& "$ScriptPath/tools/rg.ps1"
& "$ScriptPath/tools/zoomit.ps1"
