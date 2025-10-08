
function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig devops $args
}

function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig cloud $args
}

function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig croshell $args
}

function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig agents $args
}

function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig fire $args
}

function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig ftpx $args
}

function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig sessions $args
}

function devops {
    & "$HOME\.local\bin\uv.exe" run --python 3.13 --with machineconfig kill_process $args
}

