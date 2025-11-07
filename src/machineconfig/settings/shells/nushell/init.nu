# machineconfig Nushell initialization

let config_root = (
    $env.CONFIG_ROOT?
    | default ($env.HOME | path join ".config" "machineconfig")
)

def ensure_directory [dir: string] -> nothing {
    if (($dir | path exists) == false) {
        try {
            mkdir $dir
        } catch {
            null
        }
    }
}

def temp_file [prefix: string suffix: string] -> string {
    let base_dir = (
        $env.TMPDIR?
        | default (
            $env.TEMP?
            | default (
                $env.TMP?
                | default "/tmp"
            )
        )
    )

    ensure_directory $base_dir

    let token = (random uuid | str replace "-" "" | str substring 0..16)
    let path = ($base_dir | path join $"($prefix)($token)($suffix)")

    "" | save --force $path

    $path
}

export def wrap_in_shell_script [command: string ...args: string] -> nothing {
    let op_dir = ($env.HOME | path join "tmp_results" "tmp_scripts" "machineconfig")
    ensure_directory $op_dir

    let random_name = (random uuid | str replace "-" "" | str substring 0..16)
    let op_program_path = ($op_dir | path join $"($random_name).sh")
    let timestamp = (date now --utc | format date "%Y-%m-%d %H:%M:%SZ")

    print $"machineconfig: running ($command) at ($timestamp)"
    print $"machineconfig: op program path ($op_program_path)"

    let run_status = (
        try {
            with-env { OP_PROGRAM_PATH: $op_program_path } {
                run-external $command ...$args
            }
            $env.LAST_EXIT_CODE? | default 0
        } catch {
            1
        }
    )

    if ($op_program_path | path exists) {
        let has_bat = (((which bat) | length) > 0)
        if $has_bat {
            run-external bat "--style=plain" "--paging=never" $op_program_path
        } else {
            print (open --raw $op_program_path)
        }

        let follow_status = (
            try {
                run-external bash $op_program_path
                $env.LAST_EXIT_CODE? | default 0
            } catch {
                1
            }
        )

        if $follow_status == 0 {
            print $"machineconfig: completed ($command)"
        } else {
            print $"machineconfig: script exited with status ($follow_status)"
        }
    } else if $run_status == 0 {
        print $"machineconfig: completed ($command)"
    } else {
        print $"machineconfig: ($command) exited with status ($run_status)"
    }
}

export def br [...args: string] -> nothing {
    let cmd_file = (temp_file "broot-" ".cmd")

    try {
        run-external broot "--outcmd" $cmd_file ...$args
    } catch {
        if ($cmd_file | path exists) {
            rm $cmd_file
        }
        return
    }

    if ($cmd_file | path exists) {
        let command_text = (open --raw $cmd_file | str trim)
        rm $cmd_file

        if ($command_text | str length) > 0 {
            let parsed_cd = (
                try {
                    $command_text
                    | parse "cd \"{path}\""
                    | get path
                    | first
                } catch {
                    null
                }
            )

            if $parsed_cd != null {
                if ($parsed_cd | str length) > 0 {
                    cd $parsed_cd
                }
            } else {
                try {
                    run-external nu "-c" $command_text
                } catch {
                    null
                }
            }
        }
    }
}

export def lfcd [...args: string] -> nothing {
    let tmp = (temp_file "lf-" ".tmp")

    try {
        run-external lf $"--last-dir-path=$tmp" ...$args
    } catch {
        null
    }

    if ($tmp | path exists) {
        let dir = (open --raw $tmp | str trim)
        rm $tmp

        if (($dir | str length) > 0) and ($dir | path exists) {
            cd $dir
        }
    }
}

export def y [...args: string] -> nothing {
    let tmp = (temp_file "yazi-" ".tmp")

    try {
        run-external yazi ...$args $"--cwd-file=$tmp"
    } catch {
        null
    }

    if ($tmp | path exists) {
        let dir = (open --raw $tmp | str trim)
        rm $tmp

        if (($dir | str length) > 0) and ($dir | path exists) {
            cd $dir
        }
    }
}

export def tere [...args: string] -> nothing {
    let result = (
        try {
            run-external tere ...$args | complete
        } catch {
            null
        }
    )

    if $result != null {
        let dest = ($result.stdout | str trim)
        if (($dest | str length) > 0) and ($dest | path exists) {
            cd $dest
        }
    }
}

export alias lf = lfcd

export def d [...args: string] -> nothing {
    wrap_in_shell_script "devops" ...$args
}

export def c [...args: string] -> nothing {
    wrap_in_shell_script "cloud" ...$args
}

export def a [...args: string] -> nothing {
    wrap_in_shell_script "agents" ...$args
}

export def s [...args: string] -> nothing {
    wrap_in_shell_script "sessions" ...$args
}

export def fx [...args: string] -> nothing {
    wrap_in_shell_script "ftpx" ...$args
}

export def f [...args: string] -> nothing {
    wrap_in_shell_script "fire" ...$args
}

export def r [...args: string] -> nothing {
    wrap_in_shell_script "croshell" ...$args
}

export def u [...args: string] -> nothing {
    wrap_in_shell_script "utils" ...$args
}

export def t [...args: string] -> nothing {
    wrap_in_shell_script "terminal" ...$args
}

export def ms [...args: string] -> nothing {
    wrap_in_shell_script "msearch" ...$args
}

export def x [...args: string] -> nothing {
    wrap_in_shell_script "explore" ...$args
}

export alias l = lsd -la

let starship_cache_dir = ($env.HOME | path join ".cache" "starship")
if (((which starship) | length) > 0) {
    ensure_directory $starship_cache_dir
    let starship_init = ($starship_cache_dir | path join "init.nu")

    try {
        starship init nu | save --force $starship_init
    } catch {
        try {
            starship init nu | save $starship_init
        } catch {
            null
        }
    }

    try {
        source $starship_init
    } catch {
        null
    }

    try {
        use $starship_init starship
    } catch {
        null
    }
}

let zoxide_init = ($env.HOME | path join ".zoxide.nu")
if (((which zoxide) | length) > 0) {
    try {
        zoxide init nushell | save --force $zoxide_init
    } catch {
        try {
            zoxide init nushell | save $zoxide_init
        } catch {
            null
        }
    }

    try {
        source $zoxide_init
    } catch {
        null
    }
}

let mcfly_cache_dir = ($env.HOME | path join ".cache" "mcfly")
if (((which mcfly) | length) > 0) {
    ensure_directory $mcfly_cache_dir
    let mcfly_init = ($mcfly_cache_dir | path join "init.nu")

    try {
        mcfly init nu | save --force $mcfly_init
    } catch {
        try {
            mcfly init nu | save $mcfly_init
        } catch {
            null
        }
    }

    try {
        source $mcfly_init
    } catch {
        null
    }
}

let user_init = ($env.HOME | path join "dotfiles" "machineconfig" "init_nu.nu")
if ($user_init | path exists) {
    try {
        source $user_init
    } catch {
        null
    }
}

