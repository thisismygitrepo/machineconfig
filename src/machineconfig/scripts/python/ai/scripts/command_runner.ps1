$TerminalOutputDirectory = "/.ai/terminal/debug"
$TerminalOutputPathRaw = Join-Path $TerminalOutputDirectory "terminal_output_raw.txt"
$TerminalOutputPath = Join-Path $TerminalOutputDirectory "terminal_output.txt"

# Ensure the output directory exists before writing files.
New-Item -ItemType Directory -Path $TerminalOutputDirectory -Force | Out-Null

Set-Content -Path $TerminalOutputPath -Value $null
Add-Content -Path $TerminalOutputPath -Value "New run is underway. If you are reading this message, it means the execution has not finished yet, and you will need to wait. Once done you won't see this message and you will see terminal output instead."
Write-Host "Starting new uv run..."

$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = "uv"
$processInfo.ArgumentList.Add("run")
$processInfo.ArgumentList.Add("/home/alex/code/bytesense/exchanges/src/exchanges/cli/cli_binance.py")
$processInfo.ArgumentList.Add("b")
$processInfo.UseShellExecute = $false
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.EnvironmentVariables["COLUMNS"] = "200"

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $processInfo
$process.Start() | Out-Null
$standardOutput = $process.StandardOutput.ReadToEnd()
$standardError = $process.StandardError.ReadToEnd()
$process.WaitForExit()

$rawOutput = $standardOutput + $standardError
Set-Content -Path $TerminalOutputPathRaw -Value $rawOutput

$cleanOutput = $rawOutput -replace "`e\[[0-9;]*[mK]", ""
Set-Content -Path $TerminalOutputPath -Value $cleanOutput
