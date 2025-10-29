# Nushell initialization script
# Translation of init.ps1 to Nushell

const CONFIG_ROOT = $"($env.HOME)/.config/machineconfig"

# Add directories to PATH if not already present
def add_to_path_if_not_already [...directories: string] {
    for dir in $directories {
        if $dir not-in $env.PATH {
            $env.PATH = ($env.PATH | append $dir)
        }
    }
}

# Add directories to PATH
add_to_path_if_not_already (
    $"($CONFIG_ROOT)/scripts/linux"
    $"($env.HOME)/dotfiles/scripts/linux"
    "/usr/local/bin"
)

# Source external scripts and define aliases
if ($"($CONFIG_ROOT)/scripts/linux" | path exists) {
    # Source helper scripts
    source $"($CONFIG_ROOT)/settings/broot/brootcd.nu"
    source $"($CONFIG_ROOT)/settings/lf/linux/lfcd.nu"
    source $"($CONFIG_ROOT)/settings/tere/terecd.nu"
    source $"($CONFIG_ROOT)/scripts/linux/wrap_mcfg.nu"

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
    print $"Missing config files: ($CONFIG_ROOT)"
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
