
rm ~/dotfiles/creds/rclone/rclone.conf
mv ~/.config/rclone/rclone.conf $HOME/dotfiles/creds/rclone/rclone.conf
# create symlink from ~/.config/rclone/rclone.conf to ~/dotfiles/creds/rclone/rclone.conf
New-Item -ItemType SymbolicLink -Path $HOME/.config/rclone/rclone.conf -Value $HOME/dotfiles/creds/rclone/rclone.conf

