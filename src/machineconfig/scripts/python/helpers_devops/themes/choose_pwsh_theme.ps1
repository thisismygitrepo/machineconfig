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
    if (Test-Path $profilePath) {
        $profileContent = Get-Content $profilePath -Raw
    } else {
        $profileContent = ""
    }
    
    # Check if oh-my-posh line already exists and replace it
    if ($profileContent -match "oh-my-posh init pwsh[^\r\n]*") {
        # Replace existing oh-my-posh line
        $profileContent = $profileContent -replace "oh-my-posh init pwsh[^\r\n]*", $ompLine
    } else {
        # Add the oh-my-posh line with proper newlines
        if ($profileContent.Length -gt 0 -and -not $profileContent.EndsWith("`n")) {
            $profileContent += "`n"
        }
        if ($profileContent.Length -gt 0) {
            $profileContent += "`n"
        }
        $profileContent += $ompLine
        $profileContent += "`n"
    }
    
    # Write back to profile
    $profileContent | Set-Content $profilePath -Encoding UTF8 -NoNewline
    
    Write-Host "Profile updated successfully!" -ForegroundColor Green
    Write-Host "The theme will be applied automatically in future PowerShell sessions." -ForegroundColor Cyan
} else {
    Write-Host "`nNo theme selected." -ForegroundColor DarkGray
}
