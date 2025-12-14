function Register-TvFuzzyHistoryKeyHandler {
	[CmdletBinding()]
	param()

	try {
		Import-Module PSReadLine -ErrorAction Stop | Out-Null
	}
	catch {
		return
	}

	Set-PSReadLineKeyHandler -Chord "Ctrl+r" -BriefDescription "TvHistory" -Description "Fuzzy search history (tv)" -ScriptBlock {
		$tvCmd = Get-Command tv -ErrorAction SilentlyContinue
		if ($null -eq $tvCmd) {
			try { [Microsoft.PowerShell.PSConsoleReadLine]::ReverseSearchHistory() } catch { }
			return
		}

		$selected = $null
		try {
			$selected = & tv pwsh-history 2>$null | Select-Object -First 1
		}
		catch {
			$selected = $null
		}

		if ([string]::IsNullOrWhiteSpace($selected)) {
			return
		}

		try {
			$buffer = $null
			$cursor = 0
			[Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$buffer, [ref]$cursor)
			if ($null -eq $buffer) { [Microsoft.PowerShell.PSConsoleReadLine]::Insert($selected) }
			else { [Microsoft.PowerShell.PSConsoleReadLine]::Replace(0, $buffer.Length, $selected) }
		}
		catch {
			Write-Output $selected
		}
	}
}

Register-TvFuzzyHistoryKeyHandler
