# machineconfig Nushell environment setup

# Cross-platform home directory (works on Windows and Unix)
let home = ($env.HOME? | default ($env.USERPROFILE? | default $nu.home-path))

# Set up CONFIG_ROOT
let default_root = ($home | path join ".config" "machineconfig")
$env.CONFIG_ROOT = ($env.CONFIG_ROOT? | default $default_root | path expand)

# Add directories to PATH (nushell uses $env.PATH as a list)
use std/util "path add"

# Add desired paths if they exist
let paths_to_add = [
    ($env.CONFIG_ROOT | path join "scripts")
    ($home | path join "dotfiles" "scripts" "linux")
    ($home | path join ".local" "bin")
    ($home | path join ".cargo" "bin")
    "/usr/games"
]

for p in $paths_to_add {
    if ($p | path exists) {
        path add $p
    }
}
