$presets = @{
    "nerd-font-symbols" = "Changes the symbols for each module to use Nerd Font symbols."
    "no-nerd-font" = "Changes the symbols so that no Nerd Font symbols are used."
    "bracketed-segments" = "Changes the format to show segments in brackets."
    "plain-text-symbols" = "Changes the symbols for each module into plain text."
    "no-runtime-versions" = "Hides the version of language runtimes."
    "no-empty-icons" = "Does not show icons if the toolset is not found."
    "pure-preset" = "Emulates the look and behavior of Pure."
    "pastel-powerline" = "Inspired by M365Princess."
    "tokyo-night" = "Inspired by tokyo-night-vscode-theme."
    "gruvbox-rainbow" = "Inspired by Pastel Powerline and Tokyo Night."
    "jetpack" = "Pseudo minimalist preset inspired by geometry and spaceship."
}

$input_list = $presets.Keys | ForEach-Object { "$_`t$($presets[$_])" }

$preview_config = "$env:TEMP/starship_preview.toml"

# Preview command for PowerShell
# We need to split the line and get the first part.
# tv replaces {} with the line.
# We use powershell -c for the preview command to be safe and consistent.

$preview_cmd = "powershell -c `"`$preset = '{}'.Split('`t')[0]; starship preset `$preset > $preview_config; `$env:STARSHIP_CONFIG='$preview_config'; `$env:STARSHIP_SHELL='powershell'; starship prompt`""

if (Get-Command "tv" -ErrorAction SilentlyContinue) {
    $selected_line = $input_list | tv --preview-command $preview_cmd --preview-size 50
} elseif (Get-Command "fzf" -ErrorAction SilentlyContinue) {
    # fzf fallback
    $selected_line = $input_list | fzf --ansi --delimiter "`t" --with-nth 1,2 --preview "powershell -c `"`$preset = {1}; starship preset `$preset > $preview_config; `$env:STARSHIP_CONFIG='$preview_config'; `$env:STARSHIP_SHELL='powershell'; starship prompt`"" --preview-window bottom:50%
} else {
    Write-Host "Error: 'tv' or 'fzf' not found."
    exit 1
}

if ($selected_line) {
    $selected_preset = $selected_line.Split("`t")[0]
    Write-Host "Applying $selected_preset..."
    starship preset $selected_preset -o "$HOME/.config/starship.toml"
    Write-Host "Done!"
}
