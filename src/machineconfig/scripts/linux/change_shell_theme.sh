
$tmp = pwd

if ($args[0] -eq $null) {
    $name = ""
}
else {
    $name = $args[0]
}

cd ~/code/dotfiles
~/venvs/ve/Scripts/Activate.ps1
python -m fire ./windows_terminal_setup/fancy_prompt_themes.py choose $args[0]
.$profile  # reload the profile

cd $tmp

