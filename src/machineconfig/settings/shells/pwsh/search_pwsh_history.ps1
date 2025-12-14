function Register-TvFuzzyHistoryKeyHandler {
    [CmdletBinding()]
    param(
        [string]$Chord = "Ctrl+r",
        [string]$Channel = "pwsh-history"
    )

    try {
        Import-Module PSReadLine -ErrorAction Stop | Out-Null
    }
    catch {
        return
    }

    $handler = {
        param($key, $arg)

        $tvCmd = Get-Command tv -ErrorAction SilentlyContinue
        if ($null -eq $tvCmd) {
            try {
                [Microsoft.PowerShell.PSConsoleReadLine]::ReverseSearchHistory($key, $arg)
                return
            } catch { }
            try {
                [Microsoft.PowerShell.PSConsoleReadLine]::ReverseSearchHistory()
                return
            } catch { }
            return
        }

        $buffer = $null
        $cursor = 0
        try { [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$buffer, [ref]$cursor) } catch { }

        $currentPrompt = ""
        if (-not [string]::IsNullOrEmpty($buffer)) {
            if ($cursor -lt 0) { $cursor = 0 }
            elseif ($cursor -gt $buffer.Length) { $cursor = $buffer.Length }
            $currentPrompt = $buffer.Substring(0, $cursor)
        }

        $tvQuery = $currentPrompt
        if (-not [string]::IsNullOrEmpty($tvQuery) -and ($tvQuery -match "[\r\n]")) {
            $parts = $tvQuery -split "\r?\n"
            $tvQuery = $parts[-1]
        }

        $selected = $null
        $attempts = @(
            @($Channel, "--input", $tvQuery, "--inline"),
            @($Channel, "--input", $tvQuery),
            @($Channel, "--inline"),
            @($Channel)
        )

        $originalCursorPosition = $null
        try { $originalCursorPosition = $Host.UI.RawUI.CursorPosition } catch { }
        try { [Console]::WriteLine() } catch { }

        foreach ($tvArgs in $attempts) {
            $out = $null
            try { $out = & tv @tvArgs 2>$null } catch { $out = $null }
            if ($null -ne $out) {
                $selected = ($out | Select-Object -First 1)
                if (-not [string]::IsNullOrWhiteSpace($selected)) {
                    break
                }
            }
        }

        if ($null -ne $originalCursorPosition) {
            try { $Host.UI.RawUI.CursorPosition = $originalCursorPosition } catch { }
        }

        if ([string]::IsNullOrWhiteSpace($selected)) {
            return
        }

        $selected = $selected.TrimEnd("`r", "`n")

        try {
            $existingLen = if ($null -eq $buffer) { 0 } else { $buffer.Length }
            [Microsoft.PowerShell.PSConsoleReadLine]::Replace(0, $existingLen, $selected)
            try { [Microsoft.PowerShell.PSConsoleReadLine]::SetCursorPosition($selected.Length) } catch { }
        }
        catch {
            try { [Microsoft.PowerShell.PSConsoleReadLine]::Insert($selected) } catch { }
        }
    }

    try {
        Set-PSReadLineKeyHandler -Chord $Chord -BriefDescription "TvHistory" -Description "Fuzzy search history (tv)" -ScriptBlock $handler.GetNewClosure() -ErrorAction Stop
    }
    catch {
        return
    }
}

Register-TvFuzzyHistoryKeyHandler
