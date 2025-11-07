# machineconfig Nushell configuration loader

let machineconfig_root = (
	$env.CONFIG_ROOT?
	| default ($nu.config-path | path dirname | path join ".." "machineconfig")
	| path expand
)

let init_script = ($machineconfig_root | path join "settings" "shells" "nushell" "init.nu")

if ($init_script | path exists) {
	try {
		overlay use $init_script --reload
	} catch {
		try {
			source $init_script
		} catch {
			print $"machineconfig: failed to load ($init_script)"
		}
	}
} else {
	print $"machineconfig: missing init script at ($init_script)"
}
