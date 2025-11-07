# machineconfig Nushell environment setup

let config_root = (
	$env.CONFIG_ROOT?
	| default ($env.HOME | path join ".config" "machineconfig")
)

load-env {
	CONFIG_ROOT: $config_root
}

let path_entries = [
	($config_root | path join "scripts")
	($env.HOME | path join "dotfiles" "scripts" "linux")
	($env.HOME | path join ".local" "bin")
	($env.HOME | path join ".cargo" "bin")
	"/usr/games"
]

for entry in $path_entries {
	if ($entry | path exists) {
		path add $entry
	}
}


