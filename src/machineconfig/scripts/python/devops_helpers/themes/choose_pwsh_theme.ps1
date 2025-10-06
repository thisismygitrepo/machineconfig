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
    
    # Safely update the PowerShell profile
    $profilePath = $PROFILE
    $ompLine = "oh-my-posh init pwsh --config '$selectedThemeName' | Invoke-Expression"
    
    # Create profile directory if it doesn't exist
    $profileDir = Split-Path $profilePath -Parent
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }
    
    # Read existing profile content or create empty array
    $profileContent = @()
    if (Test-Path $profilePath) {
        $profileContent = Get-Content $profilePath
    }
    
    # Check if oh-my-posh line already exists and replace it, or add it
    $found = $false
    for ($i = 0; $i -lt $profileContent.Count; $i++) {
        if ($profileContent[$i] -match "oh-my-posh init pwsh") {
            $profileContent[$i] = $ompLine
            $found = $true
            break
        }
    }
    
    if (-not $found) {
        # Add the line at the end with a blank line before it
        $profileContent += ""
        $profileContent += $ompLine
    }
    
    # Write back to profile
    $profileContent | Set-Content $profilePath -Encoding UTF8
    
    Write-Host "Profile updated successfully!" -ForegroundColor Green
    Write-Host "The theme will be applied automatically in future PowerShell sessions." -ForegroundColor Cyan
} else {
    Write-Host "`nNo theme selected." -ForegroundColor DarkGray
}
