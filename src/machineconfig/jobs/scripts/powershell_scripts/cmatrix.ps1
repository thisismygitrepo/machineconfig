<#
.SYNOPSIS
    Starts Windows Terminal with 6 panes running rusty-rain in different styles.
.DESCRIPTION
    Uses `wt.exe` command chaining to create a custom grid layout.
    Requires rusty-rain to be in your system PATH.
#>

# Define the executable command
$rr = "rusty-rain"

# --- Pane Configuration ---

# 1. Main Pane: Classic Matrix (Green Binary, White Head)
$cmd1 = "$rr --group bin --color green --head white"

# 2. Right Side: Red Alert (Japanese, Red, Shaded)
$cmd2 = "$rr --group jap --color red --shade"

# 3. Bottom Right: The Ocean (Shapes, Blue RGB, Rising Up)
$cmd3 = "$rr --group shapes --color 0,191,255 --direction up"

# 4. Bottom Strip 1: Developer Mode (Programming Langs, Yellow/Orange)
$cmd4 = "$rr --group pglangs --color 255,215,0"

# 5. Bottom Strip 2: Nature (Plants, Green, Slow)
$cmd5 = "$rr --group plants --color green --speed 50"

# 6. Inner Vertical: Chaos (Emojis, random colors implied, moving Left)
$cmd6 = "$rr --group emojis --direction left"

# --- Layout Construction ---
# Logic: 
# 1. Create Tab (Pane 1)
# 2. Split Vertical 40% (Pane 2)
# 3. Split that Pane Horizontal 50% (Pane 3)
# 4. Focus Left (Back to Pane 1) -> Split Horizontal 30% (Pane 4)
# 5. Split that bottom pane Vertical 50% (Pane 5)
# 6. Focus Up (Back to Main) -> Split Vertical 30% (Pane 6)

$wtArgs = "new-tab -p `"Windows PowerShell`" $cmd1 ; " + `
          "split-pane -V -s 0.4 $cmd2 ; " + `
          "split-pane -H -s 0.5 $cmd3 ; " + `
          "move-focus left ; " + `
          "split-pane -H -s 0.3 $cmd4 ; " + `
          "split-pane -V -s 0.5 $cmd5 ; " + `
          "move-focus up ; " + `
          "split-pane -V -s 0.3 $cmd6"

# --- Execution ---
Write-Host "Launching Rusty Rain Grid..." -ForegroundColor Cyan
Start-Process wt -ArgumentList $wtArgs
