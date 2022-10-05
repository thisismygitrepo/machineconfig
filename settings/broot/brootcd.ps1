
# from https://github.com/Canop/broot/issues/159
# launch this function that wraps broot.

function br {
    $tempFile = New-TemporaryFile
    try {
        $broot = $env:BROOT
        if (-not $broot) {
             $broot = 'broot'
        }
        & $broot --outcmd $tempFile $args
        if ($LASTEXITCODE -ne 0) {
            Write-Error "$broot exited with code $LASTEXITCODE"
            return
        }
        $command = Get-Content $tempFile
        if ($command) {
            # broot returns extended-length paths but not all PowerShell/Windows
            # versions might handle this so strip the '\\?'
            Invoke-Expression $command.Replace("\\?\", "")
        }
    } finally {
        Remove-Item -force $tempFile
    }
}

$isDotSourced = $MyInvocation.InvocationName -eq '.' -or $MyInvocation.Line -eq ''
if (-not $isDotSourced) {
    br $args
}

