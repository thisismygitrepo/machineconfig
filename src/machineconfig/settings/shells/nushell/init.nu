# machineconfig Nushell initialization

# Cross-platform home directory helper
def get_home []: nothing -> string {
    $env.HOME? | default ($env.USERPROFILE? | default $nu.home-path)
}

def get_config_root []: nothing -> string {
    $env.CONFIG_ROOT? | default ((get_home) | path join ".config" "machineconfig")
}

def ensure_directory [dir: string] {
    if not ($dir | path exists) {
        try { mkdir $dir } catch { }
    }
}

def temp_file [prefix: string, suffix: string]: nothing -> string {
    let base_dir = ($env.TMPDIR? | default ($env.TEMP? | default ($env.TMP? | default "/tmp")))
    ensure_directory $base_dir
    let token = (random uuid | str replace "-" "" | str substring 0..16)
    let file_path = ($base_dir | path join $"($prefix)($token)($suffix)")
    "" | save --force $file_path
    $file_path
}

export def wrap_in_shell_script [command: string, ...args: string] {
    let op_dir = ((get_home) | path join "tmp_results" "tmp_scripts" "machineconfig")
    ensure_directory $op_dir
    let random_name = (random uuid | str replace "-" "" | str substring 0..16)
    let op_program_path = ($op_dir | path join $"($random_name).sh")
    let timestamp = (date now | format date "%Y-%m-%d %H:%M:%SZ")

    print $"machineconfig: running ($command) at ($timestamp)"
    print $"machineconfig: op program path ($op_program_path)"

    let run_status = try {
        with-env { OP_PROGRAM_PATH: $op_program_path } { ^$command ...$args }
        0
    } catch {
        1
    }

    if ($op_program_path | path exists) {
        if (which bat | is-not-empty) {
            ^bat "--style=plain" "--paging=never" $op_program_path
        } else {
            print (open --raw $op_program_path)
        }

        let follow_status = try {
            ^bash $op_program_path
            0
        } catch {
            1
        }

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

export def --env br [...args: string] {
    let cmd_file = (temp_file "broot-" ".cmd")
    try { ^broot "--outcmd" $cmd_file ...$args } catch { rm --force $cmd_file; return }
    if ($cmd_file | path exists) {
        let command_text = (open --raw $cmd_file | str trim)
        rm --force $cmd_file
        if ($command_text | str length) > 0 {
            let parsed_cd = try {
                $command_text | parse "cd \"{path}\"" | get path | first
            } catch { null }
            if $parsed_cd != null and ($parsed_cd | str length) > 0 {
                cd $parsed_cd
            } else {
                try { nu -c $command_text } catch { }
            }
        }
    }
}

export def --env lfcd [...args: string] {
    let tmp = (temp_file "lf-" ".tmp")
    try { ^lf $"--last-dir-path=($tmp)" ...$args } catch { }
    if ($tmp | path exists) {
        let dir = (open --raw $tmp | str trim)
        rm --force $tmp
        if ($dir | str length) > 0 and ($dir | path exists) {
            cd $dir
        }
    }
}

export def --env y [...args: string] {
    let tmp = (temp_file "yazi-" ".tmp")
    try { ^yazi ...$args $"--cwd-file=($tmp)" } catch { }
    if ($tmp | path exists) {
        let dir = (open --raw $tmp | str trim)
        rm --force $tmp
        if ($dir | str length) > 0 and ($dir | path exists) {
            cd $dir
        }
    }
}

export def --env tere_cd [...args: string] {
    let result = try { ^tere ...$args | complete } catch { null }
    if $result != null {
        let dest = ($result.stdout | str trim)
        if ($dest | str length) > 0 and ($dest | path exists) {
            cd $dest
        }
    }
}

export alias lf = lfcd

export def d [...args: string] { wrap_in_shell_script "devops" ...$args }
export def c [...args: string] { wrap_in_shell_script "cloud" ...$args }
export def a [...args: string] { wrap_in_shell_script "agents" ...$args }
export def s [...args: string] { wrap_in_shell_script "sessions" ...$args }
export def fx [...args: string] { wrap_in_shell_script "ftpx" ...$args }
export def f [...args: string] { wrap_in_shell_script "fire" ...$args }
export def r [...args: string] { wrap_in_shell_script "croshell" ...$args }
export def u [...args: string] { wrap_in_shell_script "utils" ...$args }
export def t [...args: string] { wrap_in_shell_script "terminal" ...$args }
export def ms [...args: string] { wrap_in_shell_script "msearch" ...$args }
export def x [...args: string] { wrap_in_shell_script "explore" ...$args }

export alias l = lsd -la

