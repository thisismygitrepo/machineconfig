

if (-not (Test-Path -Path "$HOME\.local\bin\uv.exe")) {
    Write-Output "uv binary not found, installing..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
} else {
    Write-Output "uv binary found, updating..."
    & "$HOME\.local\bin\uv.exe" self update
}
& "$HOME\.local\bin\uv.exe" python install 3.14
