



def gcd [] {
    let last_command = (history | last 1 | get command.0)
    let command_output = (do -i { nu -c $last_command } | complete)
    gh copilot explain $"Input command is: ($last_command) The output is this: ($command_output.stdout)($command_output.stderr)"
}


alias l = lsd -la
alias gcs = gh copilot suggest -t shell
alias gcg = gh copilot suggest -t git
alias gce = gh copilot explain

# as per https://github.com/starship/starship?tab=readme-ov-file#step-1-install-starship
# $nu.config-path
use ~/.cache/starship/init.nu


# https://github.com/fdncred/nu_plugin_parquet
# plugin add ~/.cargo/bin/nu_plugin_parquet
# https://github.com/FMotalleb/nu_plugin_port_list
# plugin add ~/.cargo/bin/nu_plugin_port_list
# https://github.com/FMotalleb/nu_plugin_qr_maker


# source /home/alex/.config/broot/launcher/nushell/br
# use '/home/alex/.config/broot/launcher/nushell/br' *


# as per https://github.com/ajeetdsouza/zoxide?tab=readme-ov-file#installation
source ~/.zoxide.nu

use '/home/alex/.config/broot/launcher/nushell/br' *
