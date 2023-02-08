
# below, check if npm is installed @ C:\Program Files\nodejs\npm
if (Test-Path -Path "C:\Program Files\nodejs\npm") {
    # all good
} else {
    winget install --Id CoreyButler.NVMforWindows
}

# test path ~/AppData/Roaming/npm/lolcatjs then install if not found
if (Test-Path -Path "~/AppData/Roaming/npm/lolcatjs") {  # may be ensure that utility.cmd is available
    # all good
} else {
    # install nodejs
    npm install -g lolcatjs  # -g is essential to have cli utility as well as js library.
}


# install figlet if not found
if (Test-Path -Path "~/AppData/Roaming/npm/figlet") {  # may be ensure that utility.cmd is available
    # all good
} else {
    # install nodejs
    npm install -g figlet-cli  # -g is essential to have cli utility as well as js library.
}

