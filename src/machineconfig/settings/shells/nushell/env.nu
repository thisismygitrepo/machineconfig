# machineconfig Nushell environment setup

def reduce_non_empty [segments: list<string>] -> list<string> {
	segments
	| reduce --fold [] { |segment, acc|
		if (($segment | str length) > 0) {
			$acc | append $segment
		} else {
			$acc
		}
	}
}

let default_root = ($env.HOME | path join ".config" "machineconfig")
let config_root = (
	$env.CONFIG_ROOT?
	| default $default_root
	| path expand
)

load-env { CONFIG_ROOT: $config_root }

let existing_segments = (
	$env.PATH?
	| default ""
	| split row (char esep)
	| reduce_non_empty
)

let desired_paths = [
	($config_root | path join "scripts")
	($env.HOME | path join "dotfiles" "scripts" "linux")
	($env.HOME | path join ".local" "bin")
	($env.HOME | path join ".cargo" "bin")
	"/usr/games"
]

let merged_segments = (
	$desired_paths
	| reduce --fold $existing_segments { |entry, acc|
		if (($entry | path exists) and (not ($entry in $acc))) {
			$acc | append $entry
		} else {
			$acc
		}
	}
)

let new_path = ($merged_segments | str join (char esep))
load-env { PATH: $new_path }


