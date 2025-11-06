

if (-not (Test-Path -Path "$HOME\.local\bin\uv.exe")) {
    Write-Output "uv binary not found, installing..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
} else {
    Write-Output "uv binary found, updating..."
    & "$HOME\.local\bin\uv.exe" self update
}

# `C:\Users\aalsaf01\.local\bin` is not on your PATH. To use installed Python executables, run `$env:PATH = "C:\Users\aalsaf01\.local\bin;$env:PATH"` or `uv python update-shell`.
& "$env:USERPROFILE\.local\bin\uv.exe" python update-shell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'User')

# & "$HOME\.local\bin\uv.exe" python install 3.14
uv python install 3.14

