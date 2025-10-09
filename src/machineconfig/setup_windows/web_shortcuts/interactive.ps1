

iex (iwr "https://raw.githubusercontent.com/thisismygitrepo/machineconfig/main/src/machineconfig/setup_windows/uv.ps1").Content
function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with machineconfig>=5.6 devops $args
}

function cloud {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with machineconfig>=5.6 cloud $args
}

function croshell {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with machineconfig>=5.6 croshell $args
}

function agents {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with machineconfig>=5.6 agents $args
}

function fire {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with machineconfig>=5.6 fire $args
}

function ftpx {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with machineconfig>=5.6 ftpx $args
}

function sessions {
    & "$HOME\.local\bin\uv.exe" run --python 3.14 --with machineconfig>=5.6 sessions $args
}

