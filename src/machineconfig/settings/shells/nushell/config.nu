# machineconfig Nushell configuration loader
# This file should be sourced from the user's config.nu
# Add the following line to your ~/.config/nushell/config.nu:
#   source ~/.config/machineconfig/settings/shells/nushell/config.nu

# Import the machineconfig module
use ($nu.home-path | path join ".config" "machineconfig" "settings" "shells" "nushell" "init.nu") *

# Starship prompt configuration
# User should run: `mkdir ~/.cache/starship; starship init nu | save -f ~/.cache/starship/init.nu`
# Then add to their config.nu: `use ~/.cache/starship/init.nu`

# Zoxide configuration
# User should run: `zoxide init nushell | save -f ~/.zoxide.nu`
# Then add to their config.nu: `source ~/.zoxide.nu`

# Mcfly or Atuin history search
# For mcfly: `mkdir ~/.cache/mcfly; mcfly init nu | save -f ~/.cache/mcfly/init.nu`
# Then add to config.nu: `source ~/.cache/mcfly/init.nu`
# For atuin: `atuin init nu | save -f ~/.atuin.nu`
# Then add to config.nu: `source ~/.atuin.nu`

# User's custom init file
# If you have ~/dotfiles/machineconfig/init_nu.nu, add to config.nu:
#   source ~/dotfiles/machineconfig/init_nu.nu
