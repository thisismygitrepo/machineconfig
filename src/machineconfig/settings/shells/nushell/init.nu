# Nushell initialization script
# Translation of init.ps1 to Nushell



# Add directories to PATH if not already present
def add_to_path_if_not_already [...directories: string] {
    let raw_path = ($env.PATH? | default [])
    let path_type = ($raw_path | describe)

    mut path_entries = if $path_type == "string" {
        $raw_path | split row (char esep)
    } else if $path_type == "list<string>" {
        $raw_path
    } else if $path_type == "nothing" {
        []
    } else {
        []
    }

    for dir in $directories {
        if $dir not-in $path_entries {
            $path_entries = ($path_entries | append $dir)
        }
    }

    $path_entries
}

export-env {
    let config_root = $"($env.HOME)/.config/machineconfig"
    load-env { CONFIG_ROOT: $config_root }

    let new_path = (add_to_path_if_not_already $"($config_root)/scripts" $"($env.HOME)/dotfiles/scripts/linux" "/usr/local/bin")
    load-env { PATH: $new_path }

    # Source external scripts and define aliases
    if ($"($config_root)/scripts" | path exists) {
        # Source helper scripts
    # let broot_script = ($config_root | path join "settings" "broot" "brootcd.nu")
    # let lf_script = ($config_root | path join "settings" "lf" "linux" "lfcd.nu")
    # let tere_script = ($config_root | path join "settings" "tere" "terecd.nu")

        def wrap_in_shell_script [command: string ...args: string] -> nothing {
            let op_dir = ($env.HOME | path join "tmp_results" "tmp_scripts" "machineconfig")
            if ($op_dir | path exists) == false {
                try { mkdir $op_dir } catch { null }
            }

            let random_name = (random uuid | str replace "-" "" | str substring 0..16)
            let op_program_path = ($op_dir | path join $"($random_name).sh")
            let timestamp = (date now --utc | format date "%Y-%m-%d %H:%M:%SZ")

            print $"machineconfig: running ($command) at ($timestamp)"

            let status = (try {
                with-env { OP_PROGRAM_PATH: $op_program_path } {
                    run-external $command ...$args
                    $env.LAST_EXIT_CODE? | default 0
                }
            } catch {
                1
            })

            if ($op_program_path | path exists) {
                if (which bat | is-empty) {
                    print (open --raw $op_program_path)
                } else {
                    run-external bat "--style=plain" "--paging=never" $op_program_path
                }

                let follow_status = (try {
                    run-external bash $op_program_path
                    $env.LAST_EXIT_CODE? | default 0
                } catch {
                    1
                })

                if $follow_status == 0 {
                    print $"machineconfig: completed '$command'"
                } else {
                    print $"machineconfig: program exited with status ($follow_status)"
                }
            } else if $status == 0 {
                print $"machineconfig: completed '$command'"
            } else {
                print $"machineconfig: '$command' exited with status ($status)"
            }
        }

        # Define aliases and custom commands
        def lsdla [] { lsd -la }
        alias l = lsdla

        def d [...args: string] { wrap_in_shell_script devops ...$args }
        def c [...args: string] { wrap_in_shell_script cloud ...$args }
        def a [...args: string] { wrap_in_shell_script agents ...$args }
        def ss [...args: string] { wrap_in_shell_script sessions ...$args }
        def ff [...args: string] { wrap_in_shell_script ftpx ...$args }
        def f [...args: string] { wrap_in_shell_script fire ...$args }
        def rr [...args: string] { wrap_in_shell_script croshell ...$args }
        def u [...args: string] { wrap_in_shell_script utils ...$args }
        def t [...args: string] { wrap_in_shell_script terminal ...$args }
        def ms [...args: string] { wrap_in_shell_script msearch ...$args }
    } else {
        print $"Missing config files: ($config_root)"
    }
}

# Initialize zoxide if available
# Patched by machineconfig from https://github.com/ajeetdsouza/zoxide
try {
    source <(zoxide init nushell)
} catch {
    # Do nothing if zoxide is not available
}

# Initialize Starship prompt if available
try {
    source <(starship init nu)
} catch {
    # Do nothing if starship is not available
}
# as per https://github.com/starship/starship?tab=readme-ov-file#step-1-install-starship
# $nu.config-path
# use ~/.cache/starship/init.nu

