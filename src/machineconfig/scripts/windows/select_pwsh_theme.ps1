# Requires: fzf, oh-my-posh
# Purpose: Interactive Oh My Posh theme chooser with live preview

# Path to your Oh My Posh themes directory
$themesDir = "$env:LOCALAPPDATA\Programs\oh-my-posh\themes"

if (-not (Test-Path $themesDir)) {
    Write-Host "Themes directory not found at $themesDir" -ForegroundColor Red
    exit 1
}

# Get all theme files and extract just the theme names for display
$themes = Get-ChildItem $themesDir -Filter "*.omp.json" | ForEach-Object {
    [PSCustomObject]@{
        Name = $_.BaseName
        Path = $_.FullName
    }
}

# Create a simple preview command that shows theme name and a sample prompt
$previewCommand = "pwsh -NoProfile -Command `"Write-Host 'Theme: ' -NoNewline -ForegroundColor Cyan; Write-Host (Split-Path '{}' -Leaf); Write-Host ''; oh-my-posh print primary --config '{}' 2>`$null`""

# Run fzf with preview
$selectedThemeName = $themes | ForEach-Object { $_.Path } |
    fzf --height 80% --border --ansi --reverse `
        --header "Select an Oh My Posh theme (Ctrl+C to cancel)" `
        --preview $previewCommand `
        --preview-window=right:60%:wrap

# After fzf selection
if ($selectedThemeName) {
    Write-Host "`nYou selected:" -ForegroundColor Green
    Write-Host (Split-Path $selectedThemeName -Leaf) -ForegroundColor Yellow
    Write-Host "`nApplying theme..." -ForegroundColor Cyan
    
    # Apply the theme to current session
    oh-my-posh init pwsh --config $selectedThemeName | Invoke-Expression
    
    Write-Host "`nTheme applied to current session!" -ForegroundColor Green
    Write-Host "To make this permanent, add this line to your PowerShell profile:" -ForegroundColor Cyan
    Write-Host "oh-my-posh init pwsh --config '$selectedThemeName' | Invoke-Expression" -ForegroundColor Yellow
} else {
    Write-Host "`nNo theme selected." -ForegroundColor DarkGray
}
