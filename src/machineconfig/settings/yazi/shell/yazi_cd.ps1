# function y {
#     $tmp = (New-TemporaryFile).FullName
#     yazi $args --cwd-file="$tmp"
#     $cwd = Get-Content -Path $tmp -Encoding UTF8
#     if (-not [String]::IsNullOrEmpty($cwd) -and $cwd -ne $PWD.Path) {
#         Set-Location -LiteralPath (Resolve-Path -LiteralPath $cwd).Path
#     }
#     Remove-Item -Path $tmp
# }
function y {
    # Save + temporarily disable WezTerm/Starship prompt marking
    $oldWez = $env:WEZTERM_SHELL_SKIP_ALL
    $env:WEZTERM_SHELL_SKIP_ALL = "1"   # tells WezTerm integration to skip markers (supported knob)
    $oldTransient = $env:STARSHIP_DISABLE_TRANSIENT_PROMPT
    $env:STARSHIP_DISABLE_TRANSIENT_PROMPT = "true"

    $tmp = (New-TemporaryFile).FullName
    try {
        yazi $args --cwd-file="$tmp"
        $cwd = Get-Content -Path $tmp -Encoding UTF8
        if (-not [string]::IsNullOrEmpty($cwd) -and $cwd -ne $PWD.Path) {
            Set-Location -LiteralPath (Resolve-Path -LiteralPath $cwd).Path
        }
    } finally {
        # Clean up temp file
        Remove-Item -Path $tmp -ErrorAction SilentlyContinue
        # Restore env
        if ($null -ne $oldWez) { $env:WEZTERM_SHELL_SKIP_ALL = $oldWez } else { Remove-Item Env:\WEZTERM_SHELL_SKIP_ALL -ErrorAction SilentlyContinue }
        if ($null -ne $oldTransient) { $env:STARSHIP_DISABLE_TRANSIENT_PROMPT = $oldTransient } else { Remove-Item Env:\STARSHIP_DISABLE_TRANSIENT_PROMPT -ErrorAction SilentlyContinue }
        # Nudge terminal back to sane modes (cursor on, no mouse, no bracketed paste)
        Write-Host -NoNewline "`e[0m`e[?25h`e[?1000l`e[?1002l`e[?1006l`e[?2004l"
    }
}
