

# below, check if npm is installed @ C:\Program Files\nodejs\npm
if (Test-Path -Path "C:\Program Files\nodejs\npm") {
    echo "npm already installed ✅"
} else {
    winget install --Id CoreyButler.NVMforWindows
}


# test path ~/AppData/Roaming/npm/lolcatjs then install if not found
if (Test-Path -Path "~/AppData/Roaming/npm/lolcatjs") {  # may be ensure that utility.cmd is available
    echo "lolcatjs already installed ✅"
} else {
    # install nodejs
    npm install -g lolcatjs  # -g is essential to have cli utility as well as js library.
}


# install figlet if not found
if (Test-Path -Path "~/AppData/Roaming/npm/figlet") {  # may be ensure that utility.cmd is available
    # all good
} else {
    echo "figlet already installed ✅"
    npm install -g figlet-cli  # -g is essential to have cli utility as well as js library.
}


# install boxes if not found
if (Test-Path -Path "~/AppData/Local/Microsoft/WindowsApps/boxes.exe") {  # may be ensure that utility.cmd is available
    echo "boxes already installed ✅"
} else {
    $ve_name='ve'
    & ~/venvs/$ve_name/Scripts/Activate.ps1
    python -m fire machineconfig.jobs.python_windows_installers.boxes main
    deactivate
}
