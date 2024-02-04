
# echo $nu.env-path

# as per https://github.com/ajeetdsouza/zoxide?tab=readme-ov-file#installation
zoxide init nushell | save -f ~/.zoxide.nu


mkdir ~/.cache/starship
starship init nu | save -f ~/.cache/starship/init.nu

