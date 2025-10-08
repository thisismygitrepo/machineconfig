

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig devops $args
}

function cloud {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig cloud $args
}

function croshell {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig croshell $args
}

function agents {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig agents $args
}

function fire {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig fire $args
}

function ftpx {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig ftpx $args
}

function sessions {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig sessions $args
}

function kill_process {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig kill_process $args
}
