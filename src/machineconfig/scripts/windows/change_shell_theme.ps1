
$tmp = pwd

if ($args[0] -eq $null) {
    $name = ""
}
else {
    $name = $args[0]
}

cd ~/code/machineconfig/src/machineconfig
~/venvs/ve/Scripts/Activate.ps1
python -m fire ./setup_windows_terminal/fancy_prompt_themes.py choose $args[0]
.$profile  # reload the profile

cd $tmp

